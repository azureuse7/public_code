# Kubernetes ReplicaSet - Step-by-Step Guide

A ReplicaSet ensures a specified number of pod replicas are running at any time. This guide covers creating, scaling, testing, and deleting ReplicaSets.

## Step-02: Create a ReplicaSet

Create the ReplicaSet from a manifest file:

```bash
kubectl create -f replicaset-demo.yml
```

**`replicaset-demo.yml`:**

```yaml
apiVersion: apps/v1
kind: ReplicaSet
metadata:
  name: my-helloworld-rs
  labels:
    app: my-helloworld
spec:
  replicas: 3
  selector:
    matchLabels:
      app: my-helloworld
  template:
    metadata:
      labels:
        app: my-helloworld
    spec:
      containers:
      - name: my-helloworld-app
        image: stacksimplify/kube-helloworld:1.0.0
```

### List ReplicaSets

```bash
kubectl get replicaset
kubectl get rs
```

### Describe the ReplicaSet

```bash
kubectl describe rs/<replicaset-name>
kubectl describe rs/my-helloworld-rs
# or
kubectl describe rs my-helloworld-rs
```

### List Pods

```bash
# List all pods
kubectl get pods
kubectl describe pod <pod-name>

# List pods with IP and node information
kubectl get pods -o wide
```

### Verify the Owner of a Pod

Check the `ownerReferences` section under `name` to find the ReplicaSet that owns a pod:

```bash
kubectl get pods <pod-name> -o yaml
kubectl get pods my-helloworld-rs-c8rrj -o yaml
```

## Step-03: Expose the ReplicaSet as a Service

Expose the ReplicaSet with a LoadBalancer service to make it accessible from the internet:

```bash
# Expose as a service
kubectl expose rs <replicaset-name> --type=LoadBalancer --port=80 --target-port=8080 --name=<service-name>
kubectl expose rs my-helloworld-rs --type=LoadBalancer --port=80 --target-port=8080 --name=my-helloworld-rs-service

# Get service info
kubectl get service
kubectl get svc
```

Access the application using the external IP:

```
http://<External-IP-from-get-service-output>/hello
```

## Step-04: Test ReplicaSet High Availability

ReplicaSet automatically recreates pods that are accidentally terminated. This verifies the high availability behavior:

```bash
# Get pod names
kubectl get pods

# Delete a pod
kubectl delete pod <pod-name>

# Verify a new pod was created automatically (check the Age and Name columns)
kubectl get pods
```

## Step-05: Test ReplicaSet Scalability

To scale out, update the `replicas` field in `replicaset-demo.yml` from 3 to 6:

```yaml
# Before
spec:
  replicas: 3

# After
spec:
  replicas: 6
```

Apply the change and verify:

```bash
# Apply the updated manifest
kubectl replace -f replicaset-demo.yml

# Verify new pods were created
kubectl get pods -o wide
```

## Step-06: Delete the ReplicaSet and Service

### Delete the ReplicaSet

```bash
kubectl delete rs <replicaset-name>
kubectl delete rs/my-helloworld-rs
# or
kubectl delete rs my-helloworld-rs

# Verify deletion
kubectl get rs
```

### Delete the Service

```bash
kubectl delete svc <service-name>
kubectl delete svc my-helloworld-rs-service
# or
kubectl delete svc/my-helloworld-rs-service

# Verify deletion
kubectl get svc
```
