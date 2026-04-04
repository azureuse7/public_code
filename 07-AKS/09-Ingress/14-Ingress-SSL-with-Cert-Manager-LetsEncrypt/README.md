# Ingress - SSL with Cert Manager and Let's Encrypt

## Step-01: Introduction

This guide demonstrates how to implement SSL/TLS for Kubernetes Ingress using [Let's Encrypt](https://letsencrypt.org/) and cert-manager.

[![Image](https://www.stacksimplify.com/course-images/azure-aks-ingress-ssl-letsencrypt.png "Azure AKS Kubernetes - Masterclass")](https://www.udemy.com/course/aws-eks-kubernetes-masterclass-devops-microservices/?referralCode=257C9AD5B5AF8D12D1E1)

## Step-02: Install Cert Manager

```bash
# Label the ingress-basic namespace to disable resource validation
kubectl label namespace ingress-basic cert-manager.io/disable-validation=true

# Add the Jetstack Helm repository
helm repo add jetstack https://charts.jetstack.io

# Update your local Helm chart repository cache
helm repo update

# Install the cert-manager Helm chart
helm install \
  cert-manager jetstack/cert-manager \
  --namespace ingress-basic \
  --version v1.8.2 \
  --set installCRDs=true
```

Sample output from a successful installation:

```
NAME: cert-manager
LAST DEPLOYED: Mon Jul 11 17:26:31 2022
NAMESPACE: ingress-basic
STATUS: deployed
REVISION: 1
TEST SUITE: None
NOTES:
cert-manager v1.8.2 has been deployed successfully!

In order to begin issuing certificates, you will need to set up a ClusterIssuer
or Issuer resource (for example, by creating a 'letsencrypt-staging' issuer).

More information on the different types of issuers and how to configure them
can be found in our documentation:

https://cert-manager.io/docs/configuration/

For information on how to configure cert-manager to automatically provision
Certificates for Ingress resources, take a look at the ingress-shim documentation:

https://cert-manager.io/docs/usage/ingress/
```

```bash
# Verify cert-manager pods
kubectl get pods --namespace ingress-basic

# Verify cert-manager services
kubectl get svc --namespace ingress-basic
```

## Step-06: Create the ClusterIssuer Manifest

Create or review the ClusterIssuer resource that tells cert-manager how to obtain certificates from Let's Encrypt:

```yaml
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt
spec:
  acme:
    # The ACME server URL
    server: https://acme-v02.api.letsencrypt.org/directory
    # Email address used for ACME registration
    email: dkalyanreddy@gmail.com
    # Name of a secret used to store the ACME account private key
    privateKeySecretRef:
      name: letsencrypt
    solvers:
      - http01:
          ingress:
            class: nginx
```

### Deploy the ClusterIssuer

```bash
# Apply the ClusterIssuer manifest
kubectl apply -f kube-manifests/01-CertManager-ClusterIssuer/cluster-issuer.yml

# List cluster issuers
kubectl get clusterissuer

# Describe the cluster issuer
kubectl describe clusterissuer letsencrypt
```

## Step-08: Review the Ingress SSL Manifest

Review the file `01-Ingress-SSL.yml` to ensure the correct TLS configuration and annotations are in place.

## Step-09: Deploy All Manifests and Verify

> **Note:** Certificate request, generation, approval, and download may take from 5 minutes to a couple of days, depending on configuration. Mistakes during setup can cause delays or failures.

```bash
# Deploy all manifests
kubectl apply -R -f kube-manifests/

# Verify pods
kubectl get pods

# Verify cert-manager pod logs
kubectl get pods -n ingress-basic
kubectl logs -f <cert-manager-pod-name> -n ingress-basic

# Verify SSL certificates (READY should be True)
kubectl get certificate
```

Expected output once certificates are issued:

```
NAME                      READY   SECRET                    AGE
app1-kubeoncloud-secret   True    app1-kubeoncloud-secret   45m
app2-kubeoncloud-secret   True    app2-kubeoncloud-secret   45m
```

Sample success log from cert-manager:

```log
I0824 13:09:00.495721       1 controller.go:129] cert-manager/controller/orders "msg"="syncing item" "key"="default/app2-kubeoncloud-secret-2792049964-67728538"
I0824 13:09:00.495900       1 sync.go:102] cert-manager/controller/orders "msg"="Order has already been completed, cleaning up any owned Challenge resources" "resource_kind"="Order" "resource_name"="app2-kubeoncloud-secret-2792049964-67728538" "resource_namespace"="default"
I0824 13:09:00.496904       1 controller.go:135] cert-manager/controller/orders "msg"="finished processing work item" "key"="default/app2-kubeoncloud-secret-2792049964-67728538"
```

## Step-10: Access the Application

```
https://sapp1.kubeoncloud.com/app1/index.html
https://sapp2.kubeoncloud.com/app2/index.html
```

## Step-11: Verify Ingress Logs for Client IP

```bash
# List pods in the ingress-basic namespace
kubectl -n ingress-basic get pods

# Check Ingress Controller logs
kubectl -n ingress-basic logs -f nginx-ingress-controller-xxxxxxxxx
```
