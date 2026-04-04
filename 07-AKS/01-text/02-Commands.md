# Common kubectl Commands for AKS

A quick-reference guide for frequently used `kubectl` and `az aks` commands when working with Azure Kubernetes Service clusters.

## Cluster Access

### Configure Cluster Credentials (kubeconfig)

```bash
az aks get-credentials --resource-group aks-rg1 --name aksdemo1 --overwrite-existing && kubelogin convert-kubeconfig
```

### Node Status

```bash
kubectl get nodes -o wide
```

## Pods

### List Pods

```bash
kubectl get pods -n <namespace>
kubectl get po -o wide
```

### Describe a Pod

```bash
kubectl describe pod <pod-name> -n <namespace>
```

### Delete a Pod

```bash
kubectl delete pod <pod-name> -n <namespace>
```

### Create a Pod

```bash
kubectl run <desired-pod-name> --image <container-image>
```

### Get Pods from a Namespace

```bash
kubectl get pods -n <namespace>
kubectl get namespace
kubectl get ns
```

### View Pod Logs

```bash
kubectl logs <pod-name> -n <namespace>
```

### Stream Pod Logs

```bash
kubectl logs -f <pod-name>
```

## Services

### Service Info

```bash
kubectl get service -n <namespace>
kubectl get svc -o wide
```

### Delete a Service

```bash
kubectl delete svc <service-name>
```

### Verify Service Deletion

```bash
kubectl get svc -n <namespace>
```

## ReplicaSets

### ReplicaSet Info

```bash
kubectl get replicaset
kubectl get rs
```

### Describe a ReplicaSet

```bash
kubectl describe rs/<replicaset-name>
```

### Delete a ReplicaSet

```bash
kubectl delete rs <replicaset-name>
```

### Verify ReplicaSet Deletion

```bash
kubectl get rs
```

## Namespaces

### List Namespaces

```bash
kubectl get namespace
```

### Get All Objects in a Namespace

```bash
kubectl get all
kubectl get all --namespace <namespace>
```

### Create a Namespace

```bash
kubectl create ns <namespace-name>
```

## Deployments

### List All Deployments

```bash
kubectl get deployments --all-namespaces
```

### Delete a Deployment

```bash
kubectl delete -n <namespace> deployment <deployment-name>
```

## Network Policies

```bash
kubectl get NetworkPolicies -n gatekeeper-system
kubectl edit NetworkPolicies -n gatekeeper-system
kubectl apply -f <file> -n <namespace>
```

## RBAC - Role Bindings

List all role bindings and cluster role bindings with their associated service accounts:

```bash
kubectl get rolebindings,clusterrolebindings \
  --all-namespaces \
  -o custom-columns='KIND:kind,NAMESPACE:metadata.namespace,NAME:metadata.name,SERVICE_ACCOUNTS:subjects[?(@.kind=="ServiceAccount")].name'
```

```bash
kubectl get clusterroles
kubectl get clusterrolebindings
```

Find a role binding by name and delete it:

```bash
kubectl delete clusterrolebinding <name>
kubectl delete clusterrole <name>
```

## Exec into a Pod

```bash
kubectl exec -it <pod-name> -- /bin/sh
```

## Taints

List node taints:

```bash
kubectl get nodes -o json | jq '.items[].spec'
kubectl get nodes -o json | jq '.items[].spec.taints'
```
