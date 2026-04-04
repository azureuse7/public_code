# Ingress - Domain Name Based Routing

## Step-01: Introduction

This guide demonstrates how to implement domain name based routing using Ingress. Three separate applications are served on different subdomains, with ExternalDNS automatically creating the DNS records.

[![Image](https://www.stacksimplify.com/course-images/azure-aks-ingress-domain-name-based-routing.png "Azure AKS Kubernetes - Masterclass")](https://www.udemy.com/course/aws-eks-kubernetes-masterclass-devops-microservices/?referralCode=257C9AD5B5AF8D12D1E1)

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

# Verify ExternalDNS pod logs to ensure DNS record sets were created
kubectl logs -f $(kubectl get po | egrep -o 'external-dns[A-Za-z0-9-]+')

# Verify DNS record sets in Azure DNS Zones
az network dns record-set a list -g dns-zones -z kubeoncloud.com
```

## Step-05: Access Applications

```bash
# Access App1
# http://eapp1.kubeoncloud.com/app1/index.html

# Access App2
# http://eapp2.kubeoncloud.com/app2/index.html

# Access the User Management Web App
# http://eapp3.kubeoncloud.com
# Username: admin101
# Password: password101
```

## Step-06: Clean Up Applications

```bash
# Delete all deployed applications
kubectl delete -R -f kube-manifests/

# Verify that DNS record sets were automatically deleted from Azure DNS Zones
az network dns record-set a list -g dns-zones -z kubeoncloud.com
```
