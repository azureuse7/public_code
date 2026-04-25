# Kubernetes Pods - Getting Started

A Pod is the smallest deployable unit in Kubernetes. This guide covers creating, inspecting, exposing, and cleaning up pods.

## Step-01: Create a Pod

```bash
# Template
kubectl run <desired-pod-name> --image <container-image>

# Example
kubectl run my-first-pod --image stacksimplify/kubenginx:1.0.0
```

## Step-02: List Pods

```bash
# List pods
kubectl get pods

# Short alias for pods
kubectl get po
```

List pods with the wide option to also see which node each pod is running on:

```bash
kubectl get pods -o wide
```

## Step-03: Describe a Pod

```bash
kubectl describe pod <pod-name>
kubectl describe pod my-first-pod
```

## Step-04: Expose a Pod with a Service

Currently the application is only accessible inside worker nodes. To access it externally, you need to create a **NodePort** or **Load Balancer** service.

Before creating the service, verify the Azure Standard Load Balancer configuration in the Azure portal:
- Frontend IP Configuration
- Load Balancing Rules
- Azure Public IP

```bash
# Create a pod
kubectl run <desired-pod-name> --image <container-image>
kubectl run my-first-pod --image stacksimplify/kubenginx:1.0.0

# Expose the pod as a LoadBalancer service
kubectl expose pod <pod-name> --type=LoadBalancer --port=80 --name=<service-name>
kubectl expose pod my-first-pod --type=LoadBalancer --port=80 --name=my-first-service

# Get service info
kubectl get service
kubectl get svc

# Describe the service
kubectl describe service my-first-service

# Access the application
# http://<External-IP-from-get-service-output>
```

After creating the service, verify in the Azure portal:
- Azure Standard Load Balancer: Frontend IP Configuration and Load Balancing Rules
- Azure Public IP
- Resources section of the AKS cluster in the Azure Portal Management Console

## Step-05: Interact with a Pod

### View Pod Logs

```bash
# Get pod name
kubectl get po

# Dump pod logs
kubectl logs <pod-name>
kubectl logs my-first-pod

# Stream pod logs with -f option
kubectl logs -f my-first-pod
```

> **Note:** Refer to the [kubectl cheat sheet](https://kubernetes.io/docs/reference/kubectl/cheatsheet/) and search for "Interacting with running Pods" for additional log options.

### Connect to a Container in a Pod

```bash
# Connect to the Nginx container in a pod
kubectl exec -it <pod-name> -- /bin/bash
kubectl exec -it my-first-pod -- /bin/bash

# Execute commands inside the Nginx container
ls
cd /usr/share/nginx/html
cat index.html
exit
```

Run individual commands in a container without opening an interactive shell:

```bash
kubectl exec -it my-first-pod -- env
kubectl exec -it my-first-pod -- ls
kubectl exec -it my-first-pod -- cat /usr/share/nginx/html/index.html
```

## Step-06: Get YAML Output of Pod and Service

```bash
# Get pod definition as YAML
kubectl get pod my-first-pod -o yaml

# Get service definition as YAML
kubectl get service my-first-service -o yaml
```

## Step-07: Clean Up

```bash
# Get all objects in the default namespace
kubectl get all

# Delete the service
kubectl delete svc my-first-service

# Delete the pod
kubectl delete pod my-first-pod

# Verify all objects are deleted
kubectl get all
```
