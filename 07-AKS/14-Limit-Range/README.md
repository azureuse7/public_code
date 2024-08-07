---
title: Azure AKS Kubernetes Namespaces Limit Range
description: Understand Kubernetes Namespaces Limit Range Concept Azure Kubernetes Service 
---


## Step-01: Create Namespace manifest

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: dev3
```

## Step-02: Create LimitRange manifest
- Instead of specifying `resources like cpu and memory` in every container spec of a pod defintion, we can provide the default CPU & Memory for all containers in a namespace using `LimitRange`
```yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: ns-resource-quota
  namespace: dev3
spec:
  limits:
    - default:
        memory: "512Mi" # If not specified the Container's memory limit is set to 512Mi, which is the default memory limit for the namespace.
        cpu: "500m"  # If not specified default limit is 1 vCPU per container 
      defaultRequest:
        memory: "256Mi" # If not specified default it will take from whatever specified in limits.default.memory
        cpu: "300m" # If not specified default it will take from whatever specified in limits.default.cpu
      type: Container                        
```

## Step-03: Update all k8s manifest with namespace
- Update all files from with `namespace: dev3` in top metadata section in folder `kube-manifests/` 
- **Example**
```yaml
# Deployment Manifest metadata section
apiVersion: apps/v1
kind: Deployment
metadata:
  name: app1-nginx-deployment
  labels:
    app: app1-nginx
  namespace: dev3    # Added namespace
spec:

# Service Manifest metadata section
apiVersion: v1
kind: Service
metadata:
  name: app1-nginx-clusterip-service
  labels:
    app: app1-nginx
  namespace: dev3   # Added namespace
spec: 
```

## Step-04: Create k8s objects & Test
```
# Create All Objects
kubectl apply -f kube-manifests/

# List Pods
kubectl get pods -n dev3 

# View Pod Specification (CPU & Memory)
kubectl get pod <pod-name> -o yaml -n dev3

# Get & Describe Limits
kubectl get limits -n dev3
kubectl describe limits default-cpu-mem-limit-range -n dev3

# List Services
kubectl get svc -n dev3

# Access Application
http://<Public-IP-from-List-Services-Output>/app1/index.html

```
