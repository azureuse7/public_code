# Kubernetes Troubleshooting Guide

---

## Table of Contents

1. [Render Helm templates before deploying](#render-helm-templates-before-deploying)
2. [Inspect Redis configuration and pods](#inspect-redis-configuration-and-pods)
3. [Check Falco container logs](#check-falco-container-logs)
4. [Create or copy image pull secrets into the target namespace](#create-or-copy-image-pull-secrets-into-the-target-namespace)
5. [Troubleshoot image pull secrets](#troubleshoot-image-pull-secrets)
6. [Find Helm release names](#find-helm-release-names)
7. [Inspect Kubernetes secrets](#inspect-kubernetes-secrets)
8. [Identify hostPath mounts used by Falco](#identify-hostpath-mounts-used-by-falco)
9. [Schedule Falco on tainted nodes](#schedule-falco-on-tainted-nodes)
10. [Helm command reference](#helm-command-reference)
11. [kubectx and kubens reference](#kubectx-and-kubens-reference)
12. [kubens command reference](#kubens-command-reference)

---

## Render Helm templates before deploying

Before applying any changes, render the chart locally to confirm the generated manifests look correct.

### Render the chart and inspect the Redis StatefulSet

```bash
helm template falco falco/falco \
  -f your-values.yaml \
  | grep -A 30 'falcosidekick-ui-redis' \
  | grep -A 5 'imagePullSecrets'
```

Use this to confirm that `imagePullSecrets` are rendered in the correct location for the Redis dependency.

### Inspect the chart defaults for the embedded Redis dependency

```bash
helm show values falco/falco | grep -A 20 'redis:'
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

## Inspect Redis configuration and pods


### Check whether the Redis pod is running

```bash
kubectl get pods -n falco | grep redis
```

### Describe the Redis pod

```bash
kubectl describe pod -n falco <redis-pod-name>
```

### Check Redis logs

```bash
kubectl logs -n falco <redis-pod-name>
```

### Check what image Redis is trying to pull

```bash
kubectl describe pod -n falco -l app.kubernetes.io/component=redis | grep Image
```

### Minimal Redis validation flow

```bash
# 1. Confirm secrets exist in the falco namespace
kubectl get secrets -n falco | grep artifactory

# 2. Check Redis pod
kubectl get pods -n falco | grep redis

# 3. Check what image Redis is actually trying to pull
kubectl describe pod -n falco -l app.kubernetes.io/component=redis | grep Image
```

---

## Check Falco container logs

If the pod has restarted, use the previous container logs to see the actual failure reason.

```bash
kubectl logs -n falco falco-6njtj -c falco --previous
```

Pod `describe` output often shows scheduling and image errors, but not always the underlying crash reason.

---

## Create or copy image pull secrets into the target namespace

If image pull secrets are missing in the `falco` namespace, copy them from a namespace where they already exist.

### Confirm the secrets are missing

```bash
kubectl get secrets -n falco | grep artifactory
```

### Find where the secrets already exist

```bash
kubectl get secrets -A | grep artifactory
```

### Copy the secrets into the `falco` namespace

```bash
kubectl get secret artifactory-sync -n <source-namespace> -o yaml \
  | sed 's/namespace: <source-namespace>/namespace: falco/' \
  | kubectl apply -f -
```

```bash
kubectl get secret artifactory-alt -n <source-namespace> -o yaml \
  | sed 's/namespace: <source-namespace>/namespace: falco/' \
  | kubectl apply -f -
```

### Verify the secrets now exist

```bash
kubectl get secrets -n falco | grep artifactory
```

If the issue was only a missing image pull secret, the next image pull retry should succeed automatically.

---

## Troubleshoot image pull secrets

When image pulls fail, validate the secret type, secret contents, service account configuration, and whether the credentials actually work.

### 1. Verify secret type and contents

The secret type must be `kubernetes.io/dockerconfigjson`.

```bash
kubectl get secret artifactory-sync -n falco -o jsonpath='{.type}'
kubectl get secret artifactory-alt -n falco -o jsonpath='{.type}'
```

Expected output:

```text
kubernetes.io/dockerconfigjson
```

If the type is `Opaque`, the secret is not valid for image pulls.

### Decode the Docker config and inspect the configured registries

```bash
kubectl get secret artifactory-alt -n falco \
  -o jsonpath='{.data.\.dockerconfigjson}' | base64 -d | jq .
```

Make sure the `auths` section contains your expected registry, for example `<your-registry>`. If it only contains a different registry, Kubernetes will not use it for the failing image pull.

### 2. Verify the secret is attached to the service account

```bash
kubectl get serviceaccount falco-falcosidekick -n falco -o yaml
kubectl get serviceaccount falco -n falco -o yaml
```

If `imagePullSecrets` is missing, patch the service account as a fallback:

```bash
kubectl patch serviceaccount falco-falcosidekick -n falco \
  -p '{"imagePullSecrets": [{"name": "artifactory-sync"},{"name": "artifactory-alt"}]}'
```

```bash
kubectl patch serviceaccount falco -n falco \
  -p '{"imagePullSecrets": [{"name": "artifactory-sync"},{"name": "artifactory-alt"}]}'
```

### 3. Verify the credentials actually work

```bash
kubectl run test-pull --rm -it --restart=Never \
  --image=<your-registry>/docker-remote/falcosecurity/falcosidekick:2.32.0 \
  --overrides='{"spec":{"imagePullSecrets":[{"name":"artifactory-alt"}]}}' \
  -n falco -- echo "pull worked"
```

If this succeeds, the credentials are valid and the issue is more likely to be chart rendering, service account attachment, or pod spec placement.

---

## Find Helm release names

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

### Example Helm list output

```text
NAME              NAMESPACE   REVISION  STATUS    CHART
my-app            dev         3         deployed  my-app-1.2.0
```

---

## Inspect Kubernetes secrets

### List secrets in a namespace

```bash
kubectl get secrets -n <namespace>
```

### View secret metadata only

```bash
kubectl describe secret <secret-name> -n <namespace>
```

### View the raw secret YAML

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

## Identify hostPath mounts used by Falco

Falco commonly mounts several host paths to observe system calls and container runtime events. This is especially relevant when troubleshooting Gatekeeper or Kyverno `denyhostpath` policy violations.

### Print all hostPath mounts used by the Falco DaemonSet

```bash
kubectl get ds falco -n falco -o jsonpath='{.spec.template.spec.volumes}' \
  | jq '.[].hostPath.path // empty'
```



### Inspect hostPath usage from a Helm dry-run

```bash
helm template falco falcosecurity/falco -f your-values.yaml | grep -A 2 hostPath
```

---

## Schedule Falco on tainted nodes

If Falco is deployed as a DaemonSet, it usually needs to run on every Linux node. Taints can prevent that.

### Why Falco may not land on every node

- On AKS, a chart may only tolerate one specific taint such as a custom taint key or `CriticalAddonsOnly`.
- On EKS, tolerations may be skipped entirely if the values logic only renders them for Azure.

That can leave Falco unscheduled on GPU nodes, infra nodes, or any other tainted node pool.

### Recommended toleration for a security DaemonSet

```yaml
tolerations:
  - operator: "Exists"
```

This tolerates all taints.

If you also want to limit Falco to Linux nodes:

```yaml
tolerations:
  - operator: "Exists"

nodeSelector:
  kubernetes.io/os: linux
```

### Quick validation

Compare the number of Linux nodes with the Falco DaemonSet desired pod count.

```bash
# Total Linux nodes
kubectl get nodes -l kubernetes.io/os=linux --no-headers | wc -l

# Falco DaemonSet status
kubectl get ds falco -n falco
```

If the DaemonSet `DESIRED` count is lower than the Linux node count, Falco is not scheduling everywhere.

---

## Helm command reference

### `helm install`

Use this for a first-time deployment only.

```bash
helm install falco falcosecurity/falco \
  --namespace falco \
  --create-namespace \
  -f values.yaml
```

- Creates a new release named `falco`.
- Fails if a release with that name already exists.

### `helm upgrade`

Use this to update an existing release.

```bash
helm upgrade falco falcosecurity/falco \
  --namespace falco \
  -f values.yaml
```

### `helm upgrade --install`

This is the most common CI/CD pattern.

```bash
helm upgrade --install falco falcosecurity/falco \
  --namespace falco \
  --create-namespace \
  -f values.yaml
```

- Installs the release if it does not exist.
- Upgrades the release if it already exists.

### `helm template`

Use this to render manifests locally without deploying anything.

```bash
helm template falco falcosecurity/falco \
  --namespace falco \
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

- Use `helm upgrade --install` in pipelines.
- Use `helm template` when you need to inspect the exact manifest before it hits the API server.

---

## kubectx and kubens reference

These tools make it easier to move between clusters and namespaces.

### `kubectx` commands

```bash
# List all available contexts
kubectx

# Switch to a specific context
kubectx my-aks-cluster

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
kubens falco

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
# Switch to AKS dev
kubectx aks-dev
kubens falco
kubectl get pods

# Switch to EKS dev
kubectx eks-dev
kubens falco
kubectl get pods

# Toggle back to previous cluster
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

## kubens command reference

Below is a more complete reference for `kubens` specifically.

### Core commands

```bash
# List all namespaces in the current cluster
kubens

# Switch to a specific namespace
kubens my-namespace

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
kubens falco
kubectl get pods
kubectl get daemonset

# Gatekeeper
kubens gatekeeper-system
kubectl get pods
kubectl get constrainttemplates

# Toggle back
kubens -

# Kyverno
kubens kyverno
kubectl get clusterpolicies
kubectl get policyexceptions

# cert-manager
kubens cert-manager
kubectl get certificates

# kube-system
kubens kube-system
kubectl get pods

# Reset to default namespace
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
kubectl config set-context --current --namespace=my-namespace

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
kubectl auth can-i get pods -n my-namespace
```

---



