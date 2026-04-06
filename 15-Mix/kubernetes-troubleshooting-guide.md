# Kubernetes Troubleshooting Guide

A practical reference for debugging common Kubernetes issues across AKS and EKS clusters, covering Helm, secrets, image pulls, DaemonSets, and namespace/context management.

---

## Table of Contents

1. [Helm Commands Reference](#helm-commands-reference)
2. [Secrets Management](#secrets-management)
3. [Image Pull Troubleshooting](#image-pull-troubleshooting)
4. [DaemonSet Inspection](#daemonset-inspection)
5. [Redis (Embedded Dependency) Debugging](#redis-embedded-dependency-debugging)
6. [Tolerations & Node Scheduling](#tolerations--node-scheduling)
7. [Context & Namespace Management (kubectx / kubens)](#context--namespace-management)

---

## Helm Commands Reference

### `helm install` — First-time deployment only

Creates a brand new release. **Fails if the release already exists.**

```bash
helm install falco falcosecurity/falco \
  --namespace falco \
  --create-namespace \
  -f values.yaml
```

### `helm upgrade` — Update an existing release

Applies new values or chart versions. Use `--install` to install if it doesn't exist yet.

```bash
helm upgrade --install falco falcosecurity/falco \
  --namespace falco \
  --create-namespace \
  -f values.yaml
```

> **Best practice for CI/CD and Terraform pipelines:** always use `helm upgrade --install`.

### `helm template` — Dry-run / local rendering only

Renders YAML locally — **nothing is deployed**. Useful for inspecting manifests before applying, and for debugging Gatekeeper/Kyverno policy violations.

```bash
helm template falco falcosecurity/falco \
  --namespace falco \
  -f values.yaml
```

Pipe into `kubectl` to deploy without Helm managing the release:

```bash
helm template falco falcosecurity/falco -f values.yaml | kubectl apply -f -
```

### Quick Comparison

| | `install` | `upgrade` | `template` |
|---|---|---|---|
| Deploys to cluster | ✅ | ✅ | ❌ (local only) |
| Fails if release exists | ✅ | ❌ | N/A |
| Tracks release history | ✅ | ✅ | ❌ |
| Use in CI/CD pipelines | ⚠️ risky | ✅ (`--install`) | ✅ (for debugging) |
| Needs cluster access | ✅ | ✅ | ❌ |

### Finding Existing Releases

```bash
# List all releases across all namespaces
helm list -A

# List releases in a specific namespace
helm list -n <namespace>

# Search by partial name
helm list -A | grep <partial-name>

# Find via kubectl (Helm stores a secret per release)
kubectl get secret -n <namespace> -l owner=helm --sort-by='{.metadata.creationTimestamp}'
```

Helm secrets follow the pattern: `sh.helm.release.v1.<release-name>.v<revision>`

---

## Secrets Management

### Viewing a Secret

```bash
# List secrets in a namespace
kubectl get secrets -n <namespace>

# View secret metadata (no values decoded)
kubectl describe secret <secret-name> -n <namespace>

# View raw secret (base64 encoded)
kubectl get secret <secret-name> -n <namespace> -o yaml

# Decode a specific key
kubectl get secret <secret-name> -n <namespace> \
  -o jsonpath='{.data.<key>}' | base64 --decode

# Decode all keys at once (requires jq)
kubectl get secret <secret-name> -n <namespace> -o json \
  | jq -r '.data | to_entries[] | "\(.key): \(.value | @base64d)"'
```

### Inspecting `dockerconfigjson` Secrets

```bash
kubectl get secret <secret-name> -n <namespace> -o json \
  | jq -r '.data[".dockerconfigjson"] | @base64d | fromjson'
```

This shows the registry URL, username, and auth token — useful for verifying credentials are correct and not expired.

### Copying a Secret to Another Namespace

```bash
# Check where the secret exists
kubectl get secrets -A | grep <secret-name>

# Copy to a target namespace
kubectl get secret <secret-name> -n <source-namespace> -o yaml \
  | sed 's/namespace: <source-namespace>/namespace: <target-namespace>/' \
  | kubectl apply -f -
```

---

## Image Pull Troubleshooting

### Verify Secret Type and Content

The secret **must** be of type `kubernetes.io/dockerconfigjson`. If it's `Opaque`, image pulls will fail.

```bash
# Check secret type
kubectl get secret <secret-name> -n <namespace> -o jsonpath='{.type}'
# Expected: kubernetes.io/dockerconfigjson

# Verify content includes the correct registry
kubectl get secret <secret-name> -n <namespace> \
  -o jsonpath='{.data.\.dockerconfigjson}' | base64 -d | jq .
```

You should see your registry hostname as a key under `auths`.

### Check if Secret is Attached to the Service Account

```bash
kubectl get serviceaccount <service-account-name> -n <namespace> -o yaml
```

If `imagePullSecrets` is missing, patch the service account:

```bash
kubectl patch serviceaccount <service-account-name> -n <namespace> \
  -p '{"imagePullSecrets": [{"name": "<secret-1>"},{"name": "<secret-2>"}]}'
```

### Test a Manual Image Pull

```bash
kubectl run test-pull --rm -it --restart=Never \
  --image=<your-registry>/<image>:<tag> \
  --overrides='{"spec":{"imagePullSecrets":[{"name":"<secret-name>"}]}}' \
  -n <namespace> -- echo "pull worked"
```

---

## DaemonSet Inspection

### Check All HostPath Mounts

```bash
kubectl get ds <daemonset-name> -n <namespace> \
  -o jsonpath='{.spec.template.spec.volumes}' \
  | jq '.[].hostPath.path // empty'
```

This prints all host filesystem paths mounted into the DaemonSet's pods — useful when troubleshooting `restrict-host-path` policy violations in Gatekeeper or Kyverno.

### Verify DaemonSet Scheduling Coverage

```bash
# Total Linux nodes
kubectl get nodes -l kubernetes.io/os=linux --no-headers | wc -l

# DaemonSet desired vs scheduled pods
kubectl get ds <daemonset-name> -n <namespace>
```

If `DESIRED` is less than your node count, there are nodes the DaemonSet cannot reach (likely a taint issue).

### Check What Image a Pod is Trying to Pull

```bash
kubectl describe pod -n <namespace> -l app.kubernetes.io/component=<component> | grep Image
```

---

## Redis (Embedded Dependency) Debugging

When a Helm chart includes Redis as a sub-chart dependency, use the following to debug:

```bash
# Inspect Redis-related default values
helm show values falco/falco | grep -A 20 'redis:'

# Check if the Redis pod is running
kubectl get pods -n <namespace> | grep redis

# Describe the Redis pod
kubectl describe pod -n <namespace> <redis-pod-name>

# Check Redis logs
kubectl logs -n <namespace> <redis-pod-name>

# Confirm imagePullSecrets are rendered in the Redis StatefulSet
helm template falco falco/falco \
  -f your-values.yaml \
  | grep -A 30 'falcosidekick-ui-redis' \
  | grep -A 5 'imagePullSecrets'

# Check wait-for-redis init container configuration (key may vary by chart version)
helm show values falcosecurity/falco --version <your-version> | grep -A10 waitRedis
helm show values falcosecurity/falco --version <your-version> | grep -A10 wait-redis
```

---

## Tolerations & Node Scheduling

### Tolerate All Taints (Recommended for Security DaemonSets)

For DaemonSets that should run on every node (e.g. security agents), use a catch-all toleration:

```yaml
tolerations:
  - operator: "Exists"
```

This tolerates all taints unconditionally. Combined with a `nodeSelector` to exclude Windows nodes on AKS:

```yaml
tolerations:
  - operator: "Exists"
nodeSelector:
  kubernetes.io/os: linux
```

### Check for Scheduling Gaps

After deploying, compare desired vs actual:

```bash
# Total Linux nodes
kubectl get nodes -l kubernetes.io/os=linux --no-headers | wc -l

# DaemonSet scheduled count
kubectl get ds <daemonset-name> -n <namespace>
```

---

## Context & Namespace Management

### kubectx — Switch Between Clusters

```bash
# List all available contexts
kubectx

# Switch to a specific context
kubectx my-cluster

# Toggle back to the previous context
kubectx -

# Show the current context
kubectx -c

# Rename a context (useful for long auto-generated AKS/EKS names)
kubectx short-name=very-long-arn-or-aks-context-name

# Delete a context
kubectx -d old-context

# Unset the current context
kubectx -u
```

### kubens — Switch Between Namespaces

```bash
# List all namespaces (current one is highlighted)
kubens

# Switch to a specific namespace
kubens my-namespace

# Toggle back to the previous namespace
kubens -

# Show the current namespace
kubens -c

# Unset the current namespace (revert to "default")
kubens -u
```

### Installing kubectx / kubens

```bash
# Homebrew (macOS/Linux) — installs both kubectx AND kubens
brew install kubectx

# Snap
sudo snap install kubectx --classic

# Manual
sudo git clone https://github.com/ahmetb/kubectx /opt/kubectx
sudo ln -s /opt/kubectx/kubectx /usr/local/bin/kubectx
sudo ln -s /opt/kubectx/kubens /usr/local/bin/kubens
```

### Shell Aliases

Add to `~/.bashrc` or `~/.zshrc`:

```bash
alias kx='kubectx'
alias kn='kubens'
alias k='kubectl'
alias kgp='kubectl get pods'
alias kgpa='kubectl get pods -A'
alias kgd='kubectl get daemonsets'
alias kgs='kubectl get svc'
alias kdp='kubectl describe pod'
alias klf='kubectl logs -f'
alias kge='kubectl get events --sort-by=.lastTimestamp'
alias kaf='kubectl apply -f'
alias kdf='kubectl delete -f'
```

### Shell Autocompletion

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

### Typical Workflow Example

```bash
# Switch to AKS dev cluster and check a namespace
kubectx aks-dev
kubens falco
kubectl get pods

# Jump to another namespace
kubens gatekeeper-system
kubectl get constrainttemplates

# Switch to EKS dev
kubectx eks-dev
kubens falco
kubectl get pods

# Toggle back to previous cluster
kubectx -

# Toggle back to previous namespace
kubens -
```

### How kubens Works Under the Hood

```bash
# What kubens my-namespace does
kubectl config set-context --current --namespace=my-namespace

# What kubens -c does
kubectl config view --minify --output 'jsonpath={..namespace}'

# What kubens (list) does
kubectl get namespaces -o jsonpath='{range .items[*]}{.metadata.name}{"\n"}{end}'
```

### Troubleshooting kubens

```bash
# Check RBAC if no namespaces appear
kubectl auth can-i list namespaces

# Verify which cluster you're on
kubectx -c

# Confirm namespace stuck in kubeconfig
kubectl config view --minify | grep namespace

# Check permissions in a specific namespace
kubectl auth can-i get pods -n my-namespace
```

---

*Guide covers Helm, Kubernetes secrets, image pull errors, DaemonSet scheduling, Redis sub-charts, tolerations, and context/namespace tooling.*
