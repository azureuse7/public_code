# Helm on Kubernetes
> Helm is the package manager for Kubernetes. Charts bundle all the Kubernetes manifests for an application. This guide covers the core CLI workflow, creating your own chart, and deploying charts via Terraform.

---

## 1. Manage Helm Repositories

```bash
# List configured repositories
helm repo list

# Add a repository
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo add stacksimplify https://stacksimplify.github.io/helm-charts/
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx

# Update all repositories (fetch latest chart index)
helm repo update

# Search for a chart
helm search repo nginx
helm search repo mychart1
helm search repo mychart2 --versions   # show all available chart versions
```

---

## 2. Install a Chart

```bash
# Install with auto-generated release name
helm install my-nginx bitnami/nginx

# Install a specific chart version
helm install myapp stacksimplify/mychart2 --version "0.1.0"

# Install into a specific namespace (creates it if it doesn't exist)
helm install myapp stacksimplify/mychart1 --namespace demo --create-namespace

# Override a value at install time
helm install myapp stacksimplify/mychart1 --set image.tag=2.0.0

# Install from a local chart directory
helm install myapp ./myapp --namespace demo --create-namespace
```

---

## 3. List and Inspect Releases

```bash
# List all releases (current namespace)
helm list
helm list --namespace demo

# Filter by state
helm list --deployed
helm list --superseded
helm list --failed

# Show release status and deployed resources
helm status myapp
helm status myapp --show-resources

# Show full revision history
helm history myapp
```

---

## 4. Upgrade a Release

```bash
# Upgrade to a newer chart version
helm upgrade myapp stacksimplify/mychart2 --version "0.2.0"

# Upgrade and override a value
helm upgrade myapp stacksimplify/mychart1 --set "image.tag=3.0.0"

# Upgrade to the latest chart version (no --version flag)
helm upgrade myapp stacksimplify/mychart2
```

---

## 5. Rollback a Release

```bash
# Roll back to the previous revision
helm rollback myapp

# Roll back to a specific revision number
helm rollback myapp 1

# Confirm the revision after rollback
helm history myapp
helm status myapp --show-resources
```

---

## 6. Uninstall a Release

```bash
helm uninstall myapp
helm uninstall myapp --namespace demo
```

---

## 7. Creating a Local Chart

### Scaffold a new chart

```bash
mkdir helm-demo && cd helm-demo
helm create myapp
```

Helm generates this structure:

```
myapp/
├── Chart.yaml          # chart metadata (name, version, appVersion)
├── values.yaml         # default values
└── templates/
    ├── deployment.yaml
    ├── service.yaml
    ├── hpa.yaml
    ├── ingress.yaml
    ├── _helpers.tpl    # shared template helpers
    └── tests/
        └── test-connection.yaml
```

### Minimal `Chart.yaml`

```yaml
apiVersion: v2
name: myapp
description: Simple NGINX deployment demo
type: application
version: 0.1.0       # chart version (bump on chart changes)
appVersion: "1.25.2" # app image tag
```

### Minimal `values.yaml`

```yaml
image:
  repository: nginx
  tag: "1.25.2"
service:
  type: ClusterIP
  port: 80
```

### `templates/deployment.yaml`

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "myapp.fullname" . }}
spec:
  replicas: 1
  selector:
    matchLabels:
      app: {{ include "myapp.name" . }}
  template:
    metadata:
      labels:
        app: {{ include "myapp.name" . }}
    spec:
      containers:
        - name: nginx
          image: "{{ .Values.image.repository }}:{{ .Values.image.tag }}"
          ports:
            - containerPort: 80
```

### `templates/service.yaml`

```yaml
apiVersion: v1
kind: Service
metadata:
  name: {{ include "myapp.fullname" . }}
spec:
  type: {{ .Values.service.type }}
  ports:
    - port: {{ .Values.service.port }}
      targetPort: 80
  selector:
    app: {{ include "myapp.name" . }}
```

### `templates/tests/test-connection.yaml`

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: "{{ include "myapp.fullname" . }}-test"
  annotations:
    "helm.sh/hook": test
spec:
  restartPolicy: Never
  containers:
    - name: wget
      image: busybox:1.36
      command: ['sh', '-c', 'wget -qO- http://{{ include "myapp.fullname" . }}:{{ .Values.service.port }}']
```

### Lint, render, install, test

```bash
# Static validation
helm lint myapp

# Render templates locally without touching the cluster (useful for GitOps/diffs)
helm template myapp ./myapp | tee rendered.yaml

# Install
helm install myapp ./myapp --namespace demo --create-namespace
kubectl get all -n demo

# Port-forward and verify
kubectl port-forward svc/myapp 8080:80 -n demo
curl http://localhost:8080

# Run the bundled Helm test
helm test myapp -n demo

# Upgrade (e.g. bump the image tag)
helm upgrade myapp ./myapp --set image.tag=1.27.0 -n demo

# Rollback to revision 1
helm rollback myapp 1 -n demo

# Clean up
helm uninstall myapp -n demo
kubectl delete namespace demo
```

### Helm feature summary

| Step | Feature |
|------|---------|
| `helm create` | Scaffolds chart boilerplate |
| `.Values.*` + Go templating | Parameterise manifests |
| `helm lint` | Static validation |
| `helm template` | Offline render for GitOps / diffs |
| `helm install` / `upgrade` / `rollback` | Release lifecycle |
| `helm test` | Chart-bundled smoke test |
| `helm package` + `helm push` | Publish to OCI registry |

---

## 8. Troubleshooting

### Release stuck in `pending-install` / `pending-upgrade`

A previous install or upgrade failed mid-way and left the release locked.

```bash
# See the current state
helm list --all -n <namespace>
helm history myapp -n <namespace>

# Force-delete the stuck secret so Helm can retry
kubectl delete secret -n <namespace> -l owner=helm,name=myapp

# Alternatively, roll back to the last known-good revision
helm rollback myapp -n <namespace>

# Or uninstall and reinstall cleanly
helm uninstall myapp -n <namespace> --no-hooks
helm install myapp <repo/chart> -n <namespace>
```

---

### Release in `failed` state

```bash
# Get the failure reason
helm history myapp -n <namespace>
helm status myapp -n <namespace>

# Describe Kubernetes events for the failing pods
kubectl get events -n <namespace> --sort-by='.lastTimestamp'
kubectl describe pod <pod-name> -n <namespace>

# Roll back to the previous working revision
helm rollback myapp -n <namespace>

# Roll back to a specific revision
helm rollback myapp 2 -n <namespace>
```

---

### Render and diff templates before applying

```bash
# Render chart templates locally (no cluster required)
helm template myapp <repo/chart> -f values.yaml > rendered.yaml

# Diff an upgrade before running it (requires helm-diff plugin)
helm plugin install https://github.com/databus23/helm-diff
helm diff upgrade myapp <repo/chart> -f values.yaml -n <namespace>
```

---

### Inspect chart values and metadata

```bash
# Show all default values for a chart
helm show values <repo/chart>
helm show values bitnami/nginx > default-values.yaml

# Show chart metadata (description, version, dependencies)
helm show chart <repo/chart>
helm show chart bitnami/nginx

# Show the full chart README
helm show readme <repo/chart>

# List values actually applied to a release (computed, not defaults)
helm get values myapp -n <namespace>
helm get values myapp -n <namespace> --all   # includes chart defaults
```

---

### Inspect deployed manifests

```bash
# Show all Kubernetes manifests that were applied by a release
helm get manifest myapp -n <namespace>

# Show only the generated notes (post-install instructions)
helm get notes myapp -n <namespace>

# Show hooks defined in the release
helm get hooks myapp -n <namespace>

# Download the chart for local inspection
helm pull bitnami/nginx --untar
```

---

### Debug template rendering issues

```bash
# Render with debug output — shows computed values and any template errors
helm template myapp ./myapp --debug

# Dry-run install (renders + validates against the cluster API, no resources created)
helm install myapp ./myapp --dry-run --debug -n <namespace>

# Dry-run upgrade
helm upgrade myapp ./myapp --dry-run --debug -n <namespace>

# Validate rendered YAML against the cluster (requires server-side apply)
helm template myapp ./myapp | kubectl apply --dry-run=server -f -
```

---

### Diagnose pod failures after a release

```bash
# List all resources deployed by the release
helm status myapp -n <namespace> --show-resources

# Check pod status
kubectl get pods -n <namespace>
kubectl describe pod <pod-name> -n <namespace>

# Stream pod logs
kubectl logs <pod-name> -n <namespace> -f
kubectl logs <pod-name> -n <namespace> --previous   # logs from crashed container

# Check recent cluster events
kubectl get events -n <namespace> --sort-by='.lastTimestamp' | tail -20
```

---

### Chart and repository issues

```bash
# Chart not found after helm repo add
helm repo update
helm search repo <chart-name>

# Remove a stale repo and re-add
helm repo remove <repo-name>
helm repo add <repo-name> <url>
helm repo update

# Lint a chart for syntax / best-practice errors
helm lint ./myapp
helm lint ./myapp --strict   # treat warnings as errors

# Check chart dependencies are present
helm dependency list ./myapp
helm dependency update ./myapp   # fetch missing dependencies into charts/
```

---

### Release history and secret inspection

```bash
# Full revision history with status, chart version, and description
helm history myapp -n <namespace>
helm history myapp -n <namespace> --max 10   # limit to last 10

# Helm stores each revision as a Kubernetes secret
kubectl get secrets -n <namespace> -l owner=helm
kubectl get secret sh.helm.release.v1.myapp.v3 -n <namespace> -o jsonpath='{.data.release}' \
  | base64 -d | base64 -d | gunzip | jq '.info'
```

---

### Common error quick-reference

| Error | Likely cause | Fix |
|-------|-------------|-----|
| `Error: release: not found` | Wrong namespace or release name | Add `-n <namespace>` or check `helm list --all-namespaces` |
| `Error: INSTALLATION FAILED: cannot re-use a name that is still in use` | Release exists | Use `helm upgrade` instead of `helm install` |
| `Error: rendered manifests contain a resource that already exists` | Resource created outside Helm | Add `--force` or adopt the resource with `helm adopt` |
| `Error: failed pre-install/pre-upgrade hook` | Hook job failed | Inspect hook pod logs; use `--no-hooks` to skip |
| `Error: context deadline exceeded` | Cluster unreachable or slow | Check `kubectl get nodes`; increase `--timeout` flag |
| `Error: chart requires kubeVersion: >= X` | Cluster version too old | Upgrade cluster or use an older chart version |
| `ImagePullBackOff` after install | Wrong image tag or missing pull secret | Check `helm get values`; verify image exists in registry |
| `CrashLoopBackOff` after install | App misconfiguration | Check pod logs with `kubectl logs --previous` |
| `Pending` pods after install | Insufficient node resources or no matching node | Check `kubectl describe pod` for events |

---

## 9. Terraform Examples

| Directory | Description |
|-----------|-------------|
| [helm-long/](helm-long/) | Full AKS cluster + multiple Helm releases (nginx-ingress, Prometheus, ArgoCD, Harbor, Redis) via Terraform with AAD / kubelogin auth |
| [helm-local/](helm-local/) | Deploy a local Helm chart with Kustomize post-rendering via Terraform |

| Directory | Description |
|-----------|-------------|
| [helm-long/](helm-long/) | Full AKS cluster + multiple Helm releases (nginx-ingress, Prometheus, ArgoCD, Harbor, Redis) via Terraform with AAD / kubelogin auth |
| [helm-local/](helm-local/) | Deploy a local Helm chart with Kustomize post-rendering via Terraform |
