# Helm Installation and Troubleshooting Guide

## Overview

This guide provides a practical reference for installing, validating, and troubleshooting Helm-based deployments, using **Falco** as the working example.

It covers:

- Finding and verifying the correct Helm repository
- Installing or upgrading a chart
- Rendering templates before deployment
- Inspecting release state
- Troubleshooting pods, logs, policy blocks, image pull issues, and hostPath usage
- Useful `kubectl`, `kubectx`, and `kubens` workflows

---

## Placeholder Conventions

Replace the placeholders below with values from your environment:

- `<namespace>` — target Kubernetes namespace
- `<pod name>` — target pod name
- `<node name>` — target node name
- `<release name>` — Helm release name
- `<source-namespace>` — namespace that already contains the required secret
- `<secret-name>` — Kubernetes secret name
- `<constraint-kind>` — Gatekeeper constraint kind
- `<constraint-name>` — Gatekeeper constraint name
- `<partial-name>` — partial Helm release name
- `<your-version>` — chart version you want to inspect
- `<your-registry>` — registry hostname used for image pulls
- `<key>` — secret data key

---

## 1. Finding the Helm Repository for Falco

The official Falco Helm chart is maintained by the Falco project.

### Canonical sources

- Artifact Hub: search for `falco` and filter by publisher `falcosecurity`
- GitHub: `falcosecurity/charts`

### Helm repository URL

```bash
https://falcosecurity.github.io/charts
```

### Add the repository

```bash
helm repo add falcosecurity https://falcosecurity.github.io/charts
helm repo update
helm search repo falcosecurity/falco --versions
```

---

## 2. Inspect the Chart Before Installing

Before installation, pull the default values and review them carefully.

```bash
helm show values falcosecurity/falco > falco-values.yaml
```

This is especially useful when you need to override settings such as:

- `driver.kind: modern_ebpf`
- `falcoctl` artifact settings
- Image registry overrides for restricted or private environments
- `falco.httpOutput` for downstream integrations

---

## 3. Install or Upgrade the Chart

### Install or upgrade using Helm

```bash
helm upgrade --install falco falcosecurity/falco \
  --namespace <namespace> \
  --create-namespace \
  -f falco-values.yaml \
  --version 4.x.x
```

Pinning a chart version is recommended so you can control upgrades and avoid unexpected changes.

---

## 4. Helm Command Reference

### `helm install`

Use this for a first-time deployment only.

```bash
helm install falco falcosecurity/falco \
  --namespace <namespace> \
  --create-namespace \
  -f values.yaml
```

- Creates a new release named `falco`
- Fails if the release already exists

### `helm upgrade`

Use this to update an existing release.

```bash
helm upgrade falco falcosecurity/falco \
  --namespace <namespace> \
  -f values.yaml
```

### `helm upgrade --install`

This is the most common CI/CD pattern.

```bash
helm upgrade --install falco falcosecurity/falco \
  --namespace <namespace> \
  --create-namespace \
  -f values.yaml
```

- Installs the release if it does not exist
- Upgrades the release if it already exists

### `helm template`

Use this to render manifests locally without deploying anything.

```bash
helm template falco falcosecurity/falco \
  --namespace <namespace> \
  -f values.yaml
```

This is especially useful for:

- Inspecting generated manifests before deployment
- Troubleshooting Gatekeeper or Kyverno policy violations
- Rendering static YAML for GitOps workflows

### Deploy rendered output without Helm release management

```bash
helm template falco falcosecurity/falco -f values.yaml | kubectl apply -f -
```

### Quick comparison

| Command | Deploys to cluster | Fails if release exists | Tracks release history | Best use case |
|---|---|---:|---:|---|
| `helm install` | Yes | Yes | Yes | First-time manual installs |
| `helm upgrade` | Yes | No | Yes | Updating an existing release |
| `helm upgrade --install` | Yes | No | Yes | CI/CD and idempotent automation |
| `helm template` | No | N/A | No | Debugging and manifest inspection |

### Rule of thumb

- Use `helm upgrade --install` in pipelines
- Use `helm template` when you need to inspect the exact manifest before it reaches the API server

---

## 5. Useful Helm Commands After Deployment

```bash
# List all releases in a namespace
helm list -n <namespace>

# Check the status of the release
helm status falco -n <namespace>

# See the user-supplied values applied to the release
helm get values falco -n <namespace>

# See all values, including chart defaults
helm get values falco -n <namespace> --all

# See the rendered manifests Helm deployed
helm get manifest falco -n <namespace>

# See release history
helm history falco -n <namespace>

# Preview changes before upgrading (requires helm-diff plugin)
helm diff upgrade falco falcosecurity/falco -n <namespace> -f falco-values.yaml

# Roll back to a previous revision
helm rollback falco 1 -n <namespace>

# Uninstall but keep release history
helm uninstall falco -n <namespace> --keep-history

# Dry-run an upgrade to validate before applying
helm upgrade falco falcosecurity/falco -n <namespace> -f falco-values.yaml --dry-run
```

---

## 6. Render Helm Templates Before Deploying

Before applying changes, render the chart locally and inspect the generated manifests.

### Render the chart

```bash
helm template falco falcosecurity/falco \
  --namespace <namespace> \
  -f your-values.yaml
```

### Render the Redis StatefulSet and inspect `imagePullSecrets`

```bash
helm template falco falcosecurity/falco \
  -f your-values.yaml \
  | grep -A 30 'falcosidekick-ui-redis' \
  | grep -A 5 'imagePullSecrets'
```

Use this to confirm that `imagePullSecrets` are rendered in the expected location for the Redis dependency.

### Inspect chart defaults for the embedded Redis dependency

```bash
helm show values falcosecurity/falco | grep -A 20 'redis:'
```

This helps confirm which Redis-related keys are supported by your chart version.

### Check `waitRedis` or `wait-redis` keys for your chart version

The exact init-container key can vary by chart version.

```bash
helm show values falcosecurity/falco --version <your-version> | grep -A 10 waitRedis
```

```bash
helm show values falcosecurity/falco --version <your-version> | grep -A 10 wait-redis
```

---

## 7. Deployment Validation and Debugging Flow

### Step 1 — Check the pods

```bash
kubectl get pods -n <namespace> -o wide
```

For a DaemonSet-based Falco deployment, you are typically looking for:

- One Falco pod per eligible node
- All pods in `Running` state

If pods are in `CrashLoopBackOff`, `Init:Error`, or `Pending`, continue to the next steps.

### Step 2 — Check pod logs

```bash
# Main Falco container
kubectl logs -n <namespace> daemonset/falco -c falco

# falcoctl sidecar or helper container
kubectl logs -n <namespace> daemonset/falco -c falcoctl

# Driver loader init container
kubectl logs -n <namespace> <pod name> -c falco-driver-loader

# Previous Falco container crash logs
kubectl logs -n <namespace> <pod name> -c falco --previous
```

### Step 3 — Describe the pod

```bash
kubectl describe pod -n <namespace> <pod name>
```

The **Events** section at the bottom is often the fastest way to identify the failure mode.

Common examples:

- `ImagePullBackOff` — registry unreachable, bad image path, or invalid credentials
- `FailedMount` — hostPath or mount-related issue
- `OOMKilled` — resource limits too low
- Admission webhook denial — blocked by Gatekeeper or Kyverno policies

### Step 4 — Check for policy violations

Falco often needs elevated host access that standard security policies block.

```bash
# Kyverno policy violations
kubectl get policyreport -n <namespace>
kubectl get clusterpolicyreport

# Gatekeeper constraints
kubectl get constraints -A
kubectl describe <constraint-kind> <constraint-name>

# Policy exceptions, if used
kubectl get policyexception -n <namespace>
```

Falco commonly requires exceptions for:

- `hostPID`
- `hostNetwork`
- `privileged: true`
- `hostPath` mounts such as `/dev`, `/proc`, `/boot`, and `/lib/modules`
- Containers that must run as root

### Step 5 — Verify the driver is loading (`modern_ebpf`)

```bash
# Check node details
kubectl get nodes -o wide

# Check the kernel version on a node
kubectl debug node/<node name> -it --image=ubuntu -- uname -r

# Check Falco logs for driver-related messages
kubectl logs -n <namespace> daemonset/falco -c falco | grep -i "ebpf\|driver\|probe"
```

### Step 6 — Verify rules and alerts are working

```bash
# Watch live Falco alerts
kubectl logs -n <namespace> daemonset/falco -c falco -f

# Trigger a test container
kubectl run test --image=ubuntu --restart=Never -it --rm -- bash
```

Inside the container, you can run a known suspicious action such as:

```bash
cat /etc/shadow
```

That should trigger a Falco alert if rules are loaded correctly.

To verify `falcoctl` activity:

```bash
kubectl logs -n <namespace> daemonset/falco -c falcoctl | grep -i "rule\|artifact\|pull"
```

### Step 7 — Verify HTTP output

```bash
# Check Falco logs for HTTP output messages
kubectl logs -n <namespace> daemonset/falco -c falco | grep -i "http\|output\|error"

# Inspect ConfigMaps
kubectl get configmap -n <namespace>
kubectl describe configmap falco -n <namespace>
```

---

## 8. Quick Reference Cheatsheet

| Goal | Command |
|---|---|
| See applied values | `helm get values falco -n <namespace>` |
| See rendered manifests | `helm get manifest falco -n <namespace>` |
| Stream Falco logs | `kubectl logs -n <namespace> daemonset/falco -c falco -f` |
| Inspect pod events | `kubectl describe pod -n <namespace> <pod name>` |
| Check policy blocks | `kubectl get policyreport -n <namespace>` |
| Roll back a release | `helm rollback falco 1 -n <namespace>` |

---

## 9. Inspect Redis Configuration and Pods

### Check whether the Redis pod is running

```bash
kubectl get pods -n <namespace> | grep redis
```

### Describe the Redis pod

```bash
kubectl describe pod -n <namespace> <pod name>
```

### Check Redis logs

```bash
kubectl logs -n <namespace> <pod name>
```

### Check what image Redis is trying to pull

```bash
kubectl describe pod -n <namespace> -l app.kubernetes.io/component=redis | grep Image
```

### Minimal Redis validation flow

```bash
# 1. Confirm image pull secrets exist in the namespace
kubectl get secrets -n <namespace> | grep artifactory

# 2. Check Redis pod status
kubectl get pods -n <namespace> | grep redis

# 3. Check which image Redis is trying to pull
kubectl describe pod -n <namespace> -l app.kubernetes.io/component=redis | grep Image
```

---

## 10. Check Falco Container Logs

If a pod has restarted, inspect the previous container logs.

```bash
kubectl logs -n <namespace> <pod name> -c falco --previous
```

`kubectl describe pod` may show scheduling or image issues, but previous container logs are often the best source for the actual application failure.

---

## 11. Create or Copy Image Pull Secrets into the Target Namespace

If the required image pull secrets are missing in the target namespace, copy them from another namespace.

### Confirm the secrets are missing

```bash
kubectl get secrets -n <namespace> | grep artifactory
```

### Find where the secrets already exist

```bash
kubectl get secrets -A | grep artifactory
```

### Copy the secrets into the target namespace

```bash
kubectl get secret artifactory-sync -n <source-namespace> -o yaml \
  | sed 's/namespace: <source-namespace>/namespace: <namespace>/' \
  | kubectl apply -f -
```

```bash
kubectl get secret artifactory-alt -n <source-namespace> -o yaml \
  | sed 's/namespace: <source-namespace>/namespace: <namespace>/' \
  | kubectl apply -f -
```

### Verify the secrets now exist

```bash
kubectl get secrets -n <namespace> | grep artifactory
```

If the only problem was a missing image pull secret, the next image pull retry may succeed automatically.

---

## 12. Troubleshoot Image Pull Secrets

When image pulls fail, validate the secret type, secret contents, service account configuration, and the credentials themselves.

### 1. Verify secret type and contents

The secret type must be `kubernetes.io/dockerconfigjson`.

```bash
kubectl get secret artifactory-sync -n <namespace> -o jsonpath='{.type}'
kubectl get secret artifactory-alt -n <namespace> -o jsonpath='{.type}'
```

Expected output:

```text
kubernetes.io/dockerconfigjson
```

If the type is `Opaque`, it is not valid for image pulls.

### Decode the Docker config and inspect configured registries

```bash
kubectl get secret artifactory-alt -n <namespace> \
  -o jsonpath='{.data.\.dockerconfigjson}' | base64 -d | jq .
```

Make sure the `auths` section contains the correct registry, for example `<your-registry>`.

### 2. Verify the secret is attached to the service account

```bash
kubectl get serviceaccount falco-falcosidekick -n <namespace> -o yaml
kubectl get serviceaccount falco -n <namespace> -o yaml
```

If `imagePullSecrets` is missing, patch the service account as a fallback.

```bash
kubectl patch serviceaccount falco-falcosidekick -n <namespace> \
  -p '{"imagePullSecrets": [{"name": "artifactory-sync"},{"name": "artifactory-alt"}]}'
```

```bash
kubectl patch serviceaccount falco -n <namespace> \
  -p '{"imagePullSecrets": [{"name": "artifactory-sync"},{"name": "artifactory-alt"}]}'
```

### 3. Verify the credentials actually work

```bash
kubectl run test-pull --rm -it --restart=Never \
  --image=<your-registry>/docker-remote/falcosecurity/falcosidekick:2.32.0 \
  --overrides='{"spec":{"imagePullSecrets":[{"name":"artifactory-alt"}]}}' \
  -n <namespace> -- echo "pull worked"
```

If this succeeds, the credentials are valid and the issue is more likely related to chart rendering, service account attachment, or pod spec placement.

---

## 13. Find Helm Release Names

If you do not know the Helm release name, use one of the following approaches.

### List all releases across all namespaces

```bash
helm list -A
```

### List releases in a specific namespace

```bash
helm list -n <namespace>
```

### Inspect Helm release secrets directly

```bash
kubectl get secret -n <namespace> -l owner=helm --sort-by='{.metadata.creationTimestamp}'
```

Helm stores releases as secrets with names like:

```text
sh.helm.release.v1.<release-name>.v<revision>
```

### Search by partial release name

```bash
helm list -A | grep <partial-name>
```

### Example output

```text
NAME              NAMESPACE   REVISION  STATUS    CHART
my-app            dev         3         deployed  my-app-1.2.0
```

---

## 14. Inspect Kubernetes Secrets

### List secrets in a namespace

```bash
kubectl get secrets -n <namespace>
```

### View secret metadata only

```bash
kubectl describe secret <secret-name> -n <namespace>
```

### View raw secret YAML

```bash
kubectl get secret <secret-name> -n <namespace> -o yaml
```

### Decode a specific key

```bash
kubectl get secret <secret-name> -n <namespace> \
  -o jsonpath='{.data.<key>}' | base64 --decode
```

Example:

```bash
kubectl get secret artifactory-sync -n <namespace> \
  -o jsonpath='{.data.password}' | base64 --decode
```

### Decode all keys at once

```bash
kubectl get secret <secret-name> -n <namespace> -o json \
  | jq -r '.data | to_entries[] | "\(.key): \(.value | @base64d)"'
```

This requires `jq`.

### Inspect a Docker config secret used for image pulls

```bash
kubectl get secret artifactory-sync -n <namespace> -o json \
  | jq -r '.data[".dockerconfigjson"] | @base64d | fromjson'
```

This is useful for checking the registry URL, username, and auth token stored in the secret.

---

## 15. Identify hostPath Mounts Used by Falco

Falco commonly mounts several host paths to observe system calls and container runtime events. This is especially relevant when troubleshooting Gatekeeper or Kyverno `denyhostpath` policy violations.

### Print all hostPath mounts used by the Falco DaemonSet

```bash
kubectl get ds falco -n <namespace> -o jsonpath='{.spec.template.spec.volumes}' \
  | jq '.[].hostPath.path // empty'
```

### Inspect hostPath usage from a Helm dry-run

```bash
helm template falco falcosecurity/falco -f your-values.yaml | grep -A 2 hostPath
```

---

## 16. Schedule Falco on Tainted Nodes

If Falco is deployed as a DaemonSet, it usually needs to run on every Linux node. Taints can prevent that.

### Why Falco may not land on every node

- A chart may only tolerate one specific taint
- Tolerations may be missing from the rendered DaemonSet
- Falco may be limited to only part of the cluster unintentionally

### Recommended toleration for a security DaemonSet

```yaml
tolerations:
  - operator: "Exists"
```

This tolerates all taints.

To limit Falco to Linux nodes as well:

```yaml
tolerations:
  - operator: "Exists"

nodeSelector:
  kubernetes.io/os: linux
```

### Quick validation

Compare the number of Linux nodes with the DaemonSet desired pod count.

```bash
# Total Linux nodes
kubectl get nodes -l kubernetes.io/os=linux --no-headers | wc -l

# Falco DaemonSet status
kubectl get ds falco -n <namespace>
```

If the DaemonSet `DESIRED` count is lower than the Linux node count, Falco is not scheduling everywhere.

---

## 17. `kubectx` and `kubens` Reference

These tools make it easier to move between clusters and namespaces.

### `kubectx` commands

```bash
# List all available contexts
kubectx

# Switch to a specific context
kubectx my-cluster

# Switch back to the previous context
kubectx -

# Rename a context
kubectx dev=my-long-context-name

# Delete a context
kubectx -d my-old-context

# Show current context
kubectx -c

# Unset the current context
kubectx -u
```

### `kubens` commands

```bash
# List all namespaces in the current cluster
kubens

# Switch to a specific namespace
kubens <namespace>

# Switch back to the previous namespace
kubens -

# Show current namespace
kubens -c

# Unset the current namespace
kubens -u
```

### Installation

```bash
# Homebrew
brew install kubectx

# Snap
sudo snap install kubectx --classic

# Manual installation
sudo git clone https://github.com/ahmetb/kubectx /opt/kubectx
sudo ln -s /opt/kubectx/kubectx /usr/local/bin/kubectx
sudo ln -s /opt/kubectx/kubens /usr/local/bin/kubens
```

### Example workflow

```bash
# Switch to a cluster and namespace
kubectx my-cluster
kubens <namespace>
kubectl get pods

# Switch to another cluster
kubectx another-cluster
kubens <namespace>
kubectl get pods

# Toggle back to the previous cluster
kubectx -
```

### Shell autocomplete

```bash
# Bash
source <(kubectx completion bash)
source <(kubens completion bash)

# Zsh
source <(kubectx completion zsh)
source <(kubens completion zsh)
```

### Handy aliases

```bash
alias kx='kubectx'
alias kn='kubens'
alias k='kubectl'
alias kgp='kubectl get pods'
alias kdp='kubectl describe pod'
alias kgn='kubectl get nodes'
alias kaf='kubectl apply -f'
alias kdf='kubectl delete -f'
alias klf='kubectl logs -f'
```

---

## 18. `kubens` Reference

### Core commands

```bash
# List all namespaces in the current cluster
kubens

# Switch to a specific namespace
kubens <namespace>

# Switch back to the previous namespace
kubens -

# Show the current namespace
kubens -c

# Unset the current namespace
kubens -u
```

### Practical examples

```bash
# Falco
kubens <namespace>
kubectl get pods
kubectl get daemonset

# Toggle back
kubens -

# kube-system
kubens kube-system
kubectl get pods

# Reset to the default namespace
kubens -u
```

### Autocompletion

```bash
# Bash
source <(kubens completion bash)

# Zsh
source <(kubens completion zsh)

# Fish
kubens completion fish | source
```

### Useful aliases

```bash
alias kn='kubens'
alias kns='kubens'

alias k='kubectl'
alias kgp='kubectl get pods'
alias kgpa='kubectl get pods -A'
alias kgd='kubectl get daemonsets'
alias kgs='kubectl get svc'
alias kdp='kubectl describe pod'
alias klf='kubectl logs -f'
alias kge='kubectl get events --sort-by=.lastTimestamp'
```

### What `kubens` does under the hood

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
# Check whether you can list namespaces
kubectl auth can-i list namespaces

# Check the current context
kubectx -c

# Verify namespace is set in kubeconfig
kubectl config view --minify | grep namespace

# Check access to a namespace
kubectl auth can-i get pods -n <namespace>
```

---

## 19. Practical Troubleshooting Sequence

When a Helm deployment fails or behaves unexpectedly, this order usually gives the fastest path to root cause:

1. Render the chart locally with `helm template`
2. Confirm values with `helm get values`
3. Inspect release status with `helm status`
4. Check pod status with `kubectl get pods`
5. Inspect pod events with `kubectl describe pod`
6. Check current and previous container logs
7. Inspect policy violations from Gatekeeper or Kyverno
8. Validate image pull secrets and service account attachment
9. Verify hostPath mounts and scheduling constraints
10. Roll back if a recent upgrade introduced the issue

---

## 20. Summary

For most Helm-based troubleshooting, the core workflow is:

- **Render first** with `helm template`
- **Validate release state** with `helm status`, `helm get values`, and `helm get manifest`
- **Inspect Kubernetes state** with `kubectl get`, `kubectl describe`, and `kubectl logs`
- **Check environment blockers** such as policy engines, image pull secrets, taints, and hostPath restrictions

Using that sequence makes it much easier to separate:

- chart rendering issues
- Helm release issues
- Kubernetes scheduling issues
- policy enforcement issues
- registry and secret issues
- runtime failures inside the container

