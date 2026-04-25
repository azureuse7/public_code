# Ingress - Context Path Based Routing

## Step-01: Introduction

This guide demonstrates how to implement context path based routing using Ingress. Different URL paths are routed to different backend services within the same cluster.

[![Image](https://www.stacksimplify.com/course-images/azure-aks-ingress-path-based-routing.png "Azure AKS Kubernetes - Masterclass")](https://www.udemy.com/course/aws-eks-kubernetes-masterclass-devops-microservices/?referralCode=257C9AD5B5AF8D12D1E1)

## Step-04: Deploy and Verify

```bash
# Deploy all applications
kubectl apply -R -f kube-manifests/

# List pods
kubectl get pods

# List services
kubectl get svc

# List ingress resources
kubectl get ingress

# Verify Ingress Controller logs
kubectl get pods -n ingress-basic
kubectl logs -f <pod-name> -n ingress-basic
```

## Step-05: Access Applications

```bash
# Access App1
# http://<Public-IP-created-for-Ingress>/app1/index.html

# Access App2
# http://<Public-IP-created-for-Ingress>/app2/index.html

# Access the User Management Web App
# http://<Public-IP-created-for-Ingress>
# Username: admin101
# Password: password101
```
