# Azure Kubernetes Service (AKS)

> Comprehensive AKS reference covering cluster setup, workload management, networking, storage, security, RBAC, autoscaling, observability, and DevOps integration.

---

## Contents

| Directory | Topic |
|-----------|-------|
| [00-AKS/](00-AKS/) | Cluster creation, kubectl setup, basic operations |
| [000/](000/) | Troubleshooting — node failures, disk pressure, OOM, API server issues |
| [000-subnets/](000-subnets/) | Subnet planning — EKS vs AKS comparison, CNI modes, IP sizing |
| [01-text/](01-text/) | Core Kubernetes concepts overview |
| [02-CRD/](02-CRD/) | Custom Resource Definitions |
| [03-Pods/](03-Pods/) | Pod creation, lifecycle, commands, exec |
| [04-Replicaset/](04-Replicaset/) | ReplicaSets — maintaining desired pod count |
| [05-Deployment/](05-Deployment/) | Deployments — rolling updates, rollbacks |
| [06-Services/](06-Services/) | Services — ClusterIP, NodePort, LoadBalancer |
| [07-RBAC/](07-RBAC/) | Role-Based Access Control — Roles, ClusterRoles, Bindings |
| [09-Ingress/](09-Ingress/) | Ingress controller, rules, TLS termination |
| [10-NodePools/](10-NodePools/) | Node pools — system vs user, VM sizes, taints |
| [11-TLS/](11-TLS/) | TLS certificates with cert-manager |
| [12-helm/](12-helm/) | Helm — install, upgrade, rollback, chart creation |
| [13-ConfiMap/](13-ConfiMap/) | ConfigMaps — inject configuration into pods |
| [14-Limit-Range/](14-Limit-Range/) | LimitRange — default CPU/memory limits per namespace |
| [15-Requests-Limits/](15-Requests-Limits/) | Resource requests and limits |
| [16-Namespaces-Imperative/](16-Namespaces-Imperative/) | Namespaces — isolation and resource scoping |
| [17-VirtualNodes/](17-VirtualNodes/) | Virtual nodes (ACI integration) |
| [18-Resource-Quota/](18-Resource-Quota/) | ResourceQuota — cap namespace resource consumption |
| [19-AKS-Authentication-and-RBAC/](19-AKS-Authentication-and-RBAC/) | AKS AAD integration and Kubernetes RBAC |
| [20-Kubelogin/](20-Kubelogin/) | kubelogin — Azure AD authentication for kubectl |
| [21-Kustomize/](21-Kustomize/) | Kustomize — environment-specific manifest overlays |
| [22-Autoscaling/](22-Autoscaling/) | HPA, VPA, and Cluster Autoscaler |
| [23-Daemonset/](23-Daemonset/) | DaemonSets — run a pod on every node |
| [24-ACR-attach-to-AKS/](24-ACR-attach-to-AKS/) | Attach Azure Container Registry to AKS (no imagePullSecret needed) |
| [25-Calico-Netwok-Policy/](25-Calico-Netwok-Policy/) | Calico network policies — restrict pod-to-pod traffic |
| [26-Gatekeeper/](26-Gatekeeper/) | OPA Gatekeeper — policy enforcement on the API server |
| [27-Assigning Pods to Nodes/](27-Assigning%20Pods%20to%20Nodes/) | nodeSelector, nodeAffinity, taints and tolerations |
| [28_terratest_aks/](28_terratest_aks/) | Terratest — Go-based automated tests for AKS Terraform code |
| [29-AKS-Devops/](29-AKS-Devops/) | Azure DevOps pipelines for AKS — build, push to ACR, deploy |
| [30.1-Persistence-storage/](30.1-Persistence-storage/) | PersistentVolumes and PersistentVolumeClaims |
| [30.2-Provisioned-storage/](30.2-Provisioned-storage/) | Dynamic provisioning with StorageClass |
| [30.3-User-Management-Web-Application/](30.3-User-Management-Web-Application/) | Full-stack app with persistent MySQL on AKS |
| [30.4-MySQL for AKS Workloads/](30.4-MySQL%20for%20AKS%20Workloads/) | MySQL StatefulSet on AKS |
| [30.5-Azure-File-share-Stoarge-account/](30.5-Azure-File-share-Stoarge-account/) | Azure Files storage class for AKS |
| [31-Secrets/](31-Secrets/) | Kubernetes Secrets and Azure Key Vault CSI driver |
| [32-SideCar/](32-SideCar/) | Sidecar pattern — log shippers, proxy containers |
| [34-ServiceAccount/](34-ServiceAccount/) | ServiceAccounts and Workload Identity |
| [35-Assigning-Pods-to-Nodes/](35-Assigning-Pods-to-Nodes/) | Advanced pod scheduling YAML manifests |
| [43-Falco/](43-Falco/) | Falco — runtime security monitoring via Helm/Terraform, ACNS/WireGuard encryption notes |

---

## Quick Reference

### Cluster connection
```bash
az aks get-credentials --resource-group <rg> --name <cluster> --overwrite-existing
kubectl get nodes
```

### Pod operations
```bash
kubectl get pods -A                          # all namespaces
kubectl describe pod <name>                  # detailed info
kubectl logs <pod> -c <container> -f         # stream logs
kubectl exec -it <pod> -- /bin/sh            # shell into pod
kubectl delete pod <name> --force            # force delete
```

### Deployments
```bash
kubectl apply -f deployment.yaml
kubectl rollout status deployment/<name>
kubectl rollout undo deployment/<name>       # rollback
kubectl scale deployment/<name> --replicas=3
```

### Networking
```bash
kubectl get svc -A                           # all services
kubectl get ingress -A                       # all ingress rules
kubectl port-forward svc/<name> 8080:80      # local tunnel
```

### Troubleshooting
```bash
kubectl get events --sort-by='.lastTimestamp'
kubectl top nodes
kubectl top pods
kubectl describe node <name>                 # check conditions, pressure
```
