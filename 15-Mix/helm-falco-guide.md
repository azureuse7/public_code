# Helm Installation & Troubleshooting Guide — Falco

---

## Finding the Helm Repo for Falco

The official Falco Helm chart is maintained by the Falco project itself.

### Official Sources

- **ArtifactHub:** https://artifacthub.io/packages/helm/falco-security/falco — search `falco` and filter by publisher `falcosecurity`
- **GitHub:** https://github.com/falcosecurity/charts

**Repo URL:**
```
https://falcosecurity.github.io/charts
```

### Add and Install

```bash
# Add the repo
helm repo add falcosecurity https://falcosecurity.github.io/charts

# Update your local index
helm repo update

# Search to confirm what's available
helm search repo falcosecurity/falco --versions
```

### Inspect the Chart Before Installing

```bash
# Pull down the default values so you can customise
helm show values falcosecurity/falco > falco-values.yaml
```

Key overrides to consider:

- `driver.kind: modern_ebpf`
- `falcoctl` artifact references (pointing to `gagan.jfrog.io`)
- Image registry overrides for air-gapped pulling
- `falco.httpOutput` for Illumio integration

### Install

```bash
helm upgrade --install falco falcosecurity/falco \
  --namespace <namespace> \
  --create-namespace \
  -f falco-values.yaml \
  --version 4.x.x   # pin to a specific chart version
```

---

## Helm Command Reference

### `helm install`

Use for a first-time deployment only. Fails if a release with that name already exists.

```bash
helm install falco falcosecurity/falco \
  --namespace <namespace> \
  --create-namespace \
  -f values.yaml
```

### `helm upgrade`

Use to update an existing release.

```bash
helm upgrade falco falcosecurity/falco \
  --namespace <namespace> \
  -f values.yaml
```

### `helm upgrade --install`

The most common CI/CD pattern — installs if the release does not exist, upgrades if it does.

```bash
helm upgrade --install falco falcosecurity/falco \
  --namespace <namespace> \
  --create-namespace \
  -f values.yaml
```

### `helm template`

Renders manifests locally without deploying anything. Useful for inspecting manifests before applying and for debugging Gatekeeper/Kyverno policy violations.

```bash
helm template falco falcosecurity/falco \
  --namespace <namespace> \
  -f values.yaml
```

Deploy rendered output without Helm release management:

```bash
helm template falco falcosecurity/falco -f values.yaml | kubectl apply -f -
```

### Quick Comparison

| Command | Deploys to cluster | Fails if release exists | Tracks release history | Best use case |
|---|---|---|---|---|
| `helm install` | Yes | Yes | Yes | First-time manual installs |
| `helm upgrade` | Yes | No | Yes | Updating an existing release |
| `helm upgrade --install` | Yes | No | Yes | CI/CD and idempotent automation |
| `helm template` | No | N/A | No | Debugging and manifest inspection |

> **Rule of thumb:** Use `helm upgrade --install` in pipelines. Use `helm template` when you need to inspect the exact manifest before it hits the API server.

### Other Useful Helm Commands

```bash
# List all releases in a namespace
helm list -n <namespace>

# List all releases across all namespaces
helm list -A

# Check the status of the release
helm status falco -n <namespace>

# See what values are actually applied (merged defaults + your overrides)
helm get values falco -n <namespace>

# See ALL values including defaults
helm get values falco -n <namespace> --all

# See the rendered manifests Helm deployed
helm get manifest falco -n <namespace>

# See release history (useful after upgrades)
helm history falco -n <namespace>

# Diff before upgrading (requires helm-diff plugin)
helm diff upgrade falco falcosecurity/falco -n <namespace> -f falco-values.yaml

# Rollback to previous revision
helm rollback falco 1 -n <namespace>

# Uninstall but keep history
helm uninstall falco -n <namespace> --keep-history

# Dry run an upgrade to validate before applying
helm upgrade falco falcosecurity/falco -n <namespace> -f falco-values.yaml --dry-run
```

### Find Helm Release Names

If you do not know the Helm release name:

```bash
# List all releases across all namespaces
helm list -A

# List releases in a specific namespace
helm list -n <namespace>

# Inspect Helm release secrets directly
kubectl get secret -n <namespace> -l owner=helm --sort-by='{.metadata.creationTimestamp}'

# Search by partial release name
helm list -A | grep <partial-name>
```

> Helm stores releases as secrets named: `sh.helm.release.v1.<release-name>.v<revision>`

---

## Render Helm Templates Before Deploying

Before applying any changes, render the chart locally to confirm the generated manifests look correct.

```bash
# Render the chart and inspect imagePullSecrets for Redis
helm template falco falco/falco \
  -f your-values.yaml \
  | grep -A 30 'falcosidekick-ui-redis' \
  | grep -A 5 'imagePullSecrets'

# Inspect the chart defaults for the embedded Redis dependency
helm show values falco/falco | grep -A 20 'redis:'

# Check waitRedis key for your chart version
helm show values falcosecurity/falco --version <your-version> | grep -A 10 waitRedis
helm show values falcosecurity/falco --version <your-version> | grep -A 10 wait-redis
```

---

## Post-Install Debugging

### Step 1 — Check the Pods

```bash
kubectl get pods -n <namespace> -o wide
```

You are looking for:
- `falco-xxxxx` — Running (one per node, DaemonSet)
- `falco-falcoctl-xxxxx` — Running (sidecar or init container)

If pods are in `CrashLoopBackOff`, `Init:Error`, or `Pending` — proceed to Step 2.

### Step 2 — Check Pod Logs

```bash
# Main Falco container
kubectl logs -n <namespace> daemonset/falco -c falco

# falcoctl sidecar (downloads rules artifacts)
kubectl logs -n <namespace> daemonset/falco -c falcoctl

# If init containers are failing
kubectl logs -n <namespace> <pod-name> -c falco-driver-loader

# Previous container crash logs
kubectl logs -n <namespace> <pod-name> -c falco --previous
```

### Step 3 — Describe the Pod

```bash
kubectl describe pod -n <namespace> <pod-name>
```

Check the **Events** section at the bottom. Common issues:

| Event | Likely Cause |
|---|---|
| `ImagePullBackOff` | Artifactory mirror not reachable or wrong image path |
| `FailedMount` | Kernel headers or `/dev` hostPath issues |
| `OOMKilled` | Increase memory limits in values |
| Policy denial | Gatekeeper or Kyverno blocking the DaemonSet |

### Step 4 — Check for Policy Violations

Falco needs privileged access which policies often block:

```bash
# Kyverno policy violations
kubectl get policyreport -n <namespace>
kubectl get clusterpolicyreport

# Gatekeeper constraint violations
kubectl get constraints -A
kubectl describe <constraint-kind> <constraint-name>

# Check if Falco's serviceaccount is exempted
kubectl get policyexception -n <namespace>
```

Falco typically needs exceptions for:

- `hostPID`, `hostNetwork`, `privileged: true`
- hostPath mounts: `/dev`, `/proc`, `/boot`, `/lib/modules`
- `runAsNonRoot: false` (driver loader runs as root)

### Step 5 — Verify the Driver is Loading (`modern_ebpf`)

```bash
# Check kernel version on nodes — modern_ebpf needs kernel >= 5.8
kubectl get nodes -o wide

# On AKS — check kernel version directly
kubectl debug node/<node-name> -it --image=ubuntu -- uname -r

# Check Falco logs for driver probe confirmation
kubectl logs -n <namespace> daemonset/falco -c falco | grep -i "ebpf\|driver\|probe"
```

### Step 6 — Verify Rules and Alerts Are Working

```bash
# Watch live Falco alerts
kubectl logs -n <namespace> daemonset/falco -c falco -f

# Trigger a test rule (opens a shell in a container)
kubectl run test --image=ubuntu --restart=Never -it --rm -- bash
# Then inside the container: cat /etc/shadow  ← should fire a Falco alert

# Check falcoctl pulled the correct rules
kubectl logs -n <namespace> daemonset/falco -c falcoctl | grep -i "rule\|artifact\|pull"
```

### Step 7 — Check HTTP Output (Illumio Integration)

```bash
# Confirm Falco is sending alerts to the HTTP endpoint
kubectl logs -n <namespace> daemonset/falco -c falco | grep -i "http\|output\|error"

# Check the Falco config that was rendered
kubectl get configmap -n <namespace>
kubectl describe configmap falco -n <namespace>
```

---

## Redis Troubleshooting

### Check Redis Pod Status

```bash
kubectl get pods -n <namespace> | grep redis

kubectl describe pod -n <namespace> <pod-name>

kubectl logs -n <namespace> <pod-name>

# Check what image Redis is trying to pull
kubectl describe pod -n <namespace> -l app.kubernetes.io/component=redis | grep Image
```

### Minimal Redis Validation Flow

```bash
# 1. Confirm secrets exist in the namespace
kubectl get secrets -n <namespace> | grep artifactory

# 2. Check Redis pod
kubectl get pods -n <namespace> | grep redis

# 3. Check what image Redis is actually trying to pull
kubectl describe pod -n <namespace> -l app.kubernetes.io/component=redis | grep Image
```

---

## Image Pull Secrets

### Copy Secrets Into a Target Namespace

```bash
# Confirm the secrets are missing
kubectl get secrets -n <namespace> | grep artifactory

# Find where the secrets already exist
kubectl get secrets -A | grep artifactory

# Copy the secrets into the target namespace
kubectl get secret artifactory-sync -n <source-namespace> -o yaml \
  | sed 's/namespace: <source-namespace>/namespace: <namespace>/' \
  | kubectl apply -f -

kubectl get secret artifactory-alt -n <source-namespace> -o yaml \
  | sed 's/namespace: <source-namespace>/namespace: <namespace>/' \
  | kubectl apply -f -

# Verify the secrets now exist
kubectl get secrets -n <namespace> | grep artifactory
```

### Troubleshoot Image Pull Secrets

**1. Verify secret type — must be `kubernetes.io/dockerconfigjson`:**

```bash
kubectl get secret artifactory-sync -n <namespace> -o jsonpath='{.type}'
kubectl get secret artifactory-alt -n <namespace> -o jsonpath='{.type}'
```

**2. Decode the Docker config and inspect configured registries:**

```bash
kubectl get secret artifactory-alt -n <namespace> \
  -o jsonpath='{.data.\.dockerconfigjson}' | base64 -d | jq .
```

**3. Verify the secret is attached to the service account:**

```bash
kubectl get serviceaccount falco-falcosidekick -n <namespace> -o yaml
kubectl get serviceaccount falco -n <namespace> -o yaml
```

If `imagePullSecrets` is missing, patch the service account:

```bash
kubectl patch serviceaccount falco-falcosidekick -n <namespace> \
  -p '{"imagePullSecrets": [{"name": "artifactory-sync"},{"name": "artifactory-alt"}]}'

kubectl patch serviceaccount falco -n <namespace> \
  -p '{"imagePullSecrets": [{"name": "artifactory-sync"},{"name": "artifactory-alt"}]}'
```

**4. Verify the credentials actually work:**

```bash
kubectl run test-pull --rm -it --restart=Never \
  --image=<your-registry>/docker-remote/falcosecurity/falcosidekick:2.32.0 \
  --overrides='{"spec":{"imagePullSecrets":[{"name":"artifactory-alt"}]}}' \
  -n <namespace> -- echo "pull worked"
```

---

## Kubernetes Secrets Reference

```bash
# List secrets in a namespace
kubectl get secrets -n <namespace>

# View secret metadata only
kubectl describe secret <secret-name> -n <namespace>

# View the raw secret YAML
kubectl get secret <secret-name> -n <namespace> -o yaml

# Decode a specific key
kubectl get secret <secret-name> -n <namespace> \
  -o jsonpath='{.data.<key>}' | base64 --decode

# Decode all keys at once
kubectl get secret <secret-name> -n <namespace> -o json \
  | jq -r '.data | to_entries[] | "\(.key): \(.value | @base64d)"'

# Inspect a Docker config secret used for image pulls
kubectl get secret artifactory-sync -n <namespace> -o json \
  | jq -r '.data[".dockerconfigjson"] | @base64d | fromjson'
```

---

## hostPath Mounts Used by Falco

Falco commonly mounts several host paths to observe system calls and container runtime events. Relevant when troubleshooting `denyhostpath` policy violations.

```bash
# Print all hostPath mounts used by the Falco DaemonSet
kubectl get ds falco -n <namespace> -o jsonpath='{.spec.template.spec.volumes}' \
  | jq '.[].hostPath.path // empty'

# Inspect hostPath usage from a Helm dry-run
helm template falco falcosecurity/falco -f your-values.yaml | grep -A 2 hostPath
```

---

## Scheduling Falco on Tainted Nodes

Falco is deployed as a DaemonSet and should run on every Linux node. Taints can prevent this.

**Why Falco may not land on every node:**
- On AKS, a chart may only tolerate one specific taint (e.g. `CriticalAddonsOnly`)
- On EKS, tolerations may be skipped entirely if the values logic only renders them for Azure

**Recommended toleration for a security DaemonSet:**

```yaml
tolerations:
  - operator: "Exists"
```

To also limit Falco to Linux nodes:

```yaml
tolerations:
  - operator: "Exists"

nodeSelector:
  kubernetes.io/os: linux
```

**Validate scheduling coverage:**

```bash
# Total Linux nodes
kubectl get nodes -l kubernetes.io/os=linux --no-headers | wc -l

# Falco DaemonSet status
kubectl get ds falco -n <namespace>
```

If the DaemonSet `DESIRED` count is lower than the Linux node count, Falco is not scheduling on all nodes.

---

## Quick Reference Cheatsheet

| Goal | Command |
|---|---|
| See applied values | `helm get values falco -n <namespace>` |
| See rendered manifests | `helm get manifest falco -n <namespace>` |
| Live logs | `kubectl logs -n <namespace> daemonset/falco -c falco -f` |
| Pod events | `kubectl describe pod -n <namespace> <pod-name>` |
| Policy blocks | `kubectl get policyreport -n <namespace>` |
| Rollback | `helm rollback falco 1 -n <namespace>` |

---

## kubectx and kubens Reference

### `kubectx` Commands

```bash
kubectx                        # List all available contexts
kubectx my-aks-cluster         # Switch to a specific context
kubectx -                      # Switch back to the previous context
kubectx dev=my-long-name       # Rename a context
kubectx -d my-old-context      # Delete a context
kubectx -c                     # Show current context
kubectx -u                     # Unset the current context
```

### `kubens` Commands

```bash
kubens                         # List all namespaces in the current cluster
kubens <namespace>             # Switch to a specific namespace
kubens -                       # Switch back to the previous namespace
kubens -c                      # Show current namespace
kubens -u                      # Unset the current namespace
```

### Example Workflow

```bash
# Switch to AKS dev
kubectx aks-dev
kubens <namespace>
kubectl get pods

# Switch to EKS dev
kubectx eks-dev
kubens <namespace>
kubectl get pods

# Toggle back to previous cluster
kubectx -
```

### Useful Aliases

```bash
alias kx='kubectx'
alias kn='kubens'
alias k='kubectl'
alias kgp='kubectl get pods'
alias kgpa='kubectl get pods -A'
alias kgd='kubectl get daemonsets'
alias kdp='kubectl describe pod'
alias kgn='kubectl get nodes'
alias kaf='kubectl apply -f'
alias kdf='kubectl delete -f'
alias klf='kubectl logs -f'
alias kge='kubectl get events --sort-by=.lastTimestamp'
```

### Shell Autocomplete

```bash
# Bash
source <(kubectx completion bash)
source <(kubens completion bash)

# Zsh
source <(kubectx completion zsh)
source <(kubens completion zsh)

# Fish
kubens completion fish | source
```

### What `kubens` Does Under the Hood

```bash
# Equivalent to switching namespace
kubectl config set-context --current --namespace=<namespace>

# Equivalent to showing current namespace
kubectl config view --minify --output 'jsonpath={..namespace}'

# Equivalent to listing namespaces
kubectl get namespaces -o jsonpath='{range .items[*]}{.metadata.name}{"\n"}{end}'
```

### Troubleshooting `kubens`

```bash
kubectl auth can-i list namespaces
kubectx -c
kubectl config view --minify | grep namespace
kubectl auth can-i get pods -n <namespace>
```
