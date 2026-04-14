# Vault as Certificate Issuer on Kubernetes with cert-manager (Terraform-Based Guide)

## Overview

This guide explains **end-to-end** how to configure **HashiCorp Vault as a Certificate Authority (CA)** for **cert-manager** on Kubernetes.

It includes:

- Installing Vault
- Initializing / unsealing Vault
- Configuring Vault PKI
- Enabling Kubernetes authentication
- Installing cert-manager
- Creating Vault Issuer via Terraform-managed Kubernetes manifests
- Issuing certificates
- Using certificates with Ingress
- Verifying automatic renewal

---

# Architecture Flow

```text
Application / Ingress
      |
      v
cert-manager Certificate CRD
      |
      v
cert-manager Vault Issuer
      |
      v
Vault Kubernetes Auth
      |
      v
Vault PKI Engine Signs Certificate
      |
      v
TLS Secret Created in Kubernetes
```

---

# Prerequisites

- Kubernetes cluster (AKS / EKS / On-Prem)
- kubectl configured
- Helm installed
- Terraform >= 1.5
- Vault CLI installed
- DNS / hosts file access for testing

---

# Step 1 — Install Vault

## Add Helm Repository

```bash
helm repo add hashicorp https://helm.releases.hashicorp.com
helm repo update
```

## Terraform: Install Vault via Helm

```hcl
resource "helm_release" "vault" {
  name       = "vault"
  namespace  = "vault"
  repository = "https://helm.releases.hashicorp.com"
  chart      = "vault"

  create_namespace = true

  values = [
    yamlencode({
      server = {
        dev = {
          enabled = false
        }

        standalone = {
          enabled = true
        }

        dataStorage = {
          enabled = true
          size    = "10Gi"
        }
      }
    })
  ]
}
```

---

# Step 2 — Initialize and Unseal Vault

```bash
kubectl exec -n vault vault-0 -- vault operator init
```

Save:

- Unseal Keys
- Root Token

Unseal Vault:

```bash
kubectl exec -n vault vault-0 -- vault operator unseal <KEY1>
kubectl exec -n vault vault-0 -- vault operator unseal <KEY2>
kubectl exec -n vault vault-0 -- vault operator unseal <KEY3>
```

Login:

```bash
kubectl exec -it -n vault vault-0 -- vault login
```

---

# Step 3 — Enable PKI Secrets Engine

```bash
vault secrets enable pki
vault secrets tune -max-lease-ttl=8760h pki
```

---

# Step 4 — Generate Root CA

```bash
vault write pki/root/generate/internal \
    common_name="example.com Root CA" \
    ttl=8760h
```

---

# Step 5 — Configure Vault PKI URLs

```bash
vault write pki/config/urls \
  issuing_certificates="http://vault.vault:8200/v1/pki/ca" \
  crl_distribution_points="http://vault.vault:8200/v1/pki/crl"
```

---

# Step 6 — Create PKI Role

```bash
vault write pki/roles/example-dot-com \
    allowed_domains=example.com \
    allow_subdomains=true \
    max_ttl=24h
```

---

# Step 7 — Create Vault Policy

```bash
vault policy write pki - <<EOF
path "pki*" {
  capabilities = ["read", "list"]
}

path "pki/sign/example-dot-com" {
  capabilities = ["create", "update"]
}

path "pki/issue/example-dot-com" {
  capabilities = ["create"]
}
EOF
```

---

# Step 8 — Enable Kubernetes Auth in Vault

```bash
vault auth enable kubernetes
```

Configure Kubernetes Auth:

```bash
vault write auth/kubernetes/config \
  token_reviewer_jwt="$(cat /var/run/secrets/kubernetes.io/serviceaccount/token)" \
  kubernetes_host="https://${KUBERNETES_PORT_443_TCP_ADDR}:443" \
  kubernetes_ca_cert=@/var/run/secrets/kubernetes.io/serviceaccount/ca.crt
```

---

# Step 9 — Create Vault Kubernetes Auth Role

```bash
vault write auth/kubernetes/role/issuer \
    bound_service_account_names=issuer \
    bound_service_account_namespaces=cert-manager,default \
    policies=pki \
    ttl=20m
```

---

# Step 10 — Install cert-manager

```hcl
resource "helm_release" "cert_manager" {
  name       = "cert-manager"
  namespace  = "cert-manager"
  repository = "https://charts.jetstack.io"
  chart      = "cert-manager"

  create_namespace = true

  values = [
    yamlencode({
      installCRDs = true
    })
  ]
}
```

---

# Step 11 — Create Service Account for Vault Auth

```hcl
resource "kubernetes_service_account" "issuer" {
  metadata {
    name      = "issuer"
    namespace = "default"
  }
}
```

---

# Step 12 — Create Service Account Token Secret

```hcl
resource "kubernetes_secret" "issuer_token" {
  metadata {
    name      = "issuer-token"
    namespace = "default"
    annotations = {
      "kubernetes.io/service-account.name" = "issuer"
    }
  }

  type = "kubernetes.io/service-account-token"
}
```

---

# Step 13 — Create cert-manager Vault Issuer

```hcl
resource "kubernetes_manifest" "vault_issuer" {
  manifest = {
    apiVersion = "cert-manager.io/v1"
    kind       = "Issuer"

    metadata = {
      name      = "vault-issuer"
      namespace = "default"
    }

    spec = {
      vault = {
        server = "http://vault.vault:8200"
        path   = "pki/sign/example-dot-com"

        auth = {
          kubernetes = {
            mountPath = "/v1/auth/kubernetes"
            role      = "issuer"

            secretRef = {
              name = "issuer-token"
              key  = "token"
            }
          }
        }
      }
    }
  }
}
```

---

# Step 14 — Create Certificate Resource

```hcl
resource "kubernetes_manifest" "certificate" {
  manifest = {
    apiVersion = "cert-manager.io/v1"
    kind       = "Certificate"

    metadata = {
      name      = "demo-example-com"
      namespace = "default"
    }

    spec = {
      secretName = "example-com-tls"

      issuerRef = {
        name = "vault-issuer"
      }

      commonName = "demo.example.com"

      dnsNames = [
        "demo.example.com"
      ]
    }
  }
}
```

---

# Step 15 — Install Ingress NGINX

```hcl
resource "helm_release" "ingress_nginx" {
  name       = "ingress-nginx"
  namespace  = "ingress-nginx"
  repository = "https://kubernetes.github.io/ingress-nginx"
  chart      = "ingress-nginx"

  create_namespace = true
}
```

---

# Step 16 — Deploy Demo App

```bash
kubectl create deployment web --image=gcr.io/google-samples/hello-app:1.0
kubectl expose deployment web --port=8080
```

---

# Step 17 — Create TLS Ingress

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: example-ingress
spec:
  tls:
    - hosts:
        - demo.example.com
      secretName: example-com-tls
  rules:
    - host: demo.example.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: web
                port:
                  number: 8080
```

---

# Step 18 — Test

Add to hosts file:

```text
<INGRESS_IP> demo.example.com
```

Test:

```bash
curl -kiv https://demo.example.com
```

---

# Step 19 — Verify Auto-Renewal

Check certificate:

```bash
kubectl describe certificate demo-example-com
```

Wait for renewal window and confirm cert-manager reissues certificate automatically.

---

# Common Missing Production Steps (Added)

## Enable HA Vault
Use integrated storage / raft instead of standalone for production.

## Enable TLS on Vault
Do NOT use HTTP in production.

## Restrict Vault Policies
Avoid wildcard paths.

## Use ClusterIssuer
Prefer ClusterIssuer if multiple namespaces need certs.

## Backup Vault Storage
Critical for PKI and secrets durability.

## Monitor cert-manager / Vault
Use Prometheus/Grafana alerts.

---

# Summary

You now have:

- Vault installed on Kubernetes
- Vault acting as internal CA
- cert-manager authenticating to Vault using Kubernetes auth
- Certificates issued automatically
- TLS attached to Ingress
- Automatic certificate renewal enabled

---

# Recommended Next Enhancements

- Replace self-signed root with intermediate CA
- Use external DNS automation
- Use Vault HA with Raft
- Enable mTLS between workloads
