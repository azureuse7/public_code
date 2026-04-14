# HashiCorp Vault as a Certificate Authority on Kubernetes — Complete Terraform Guide

> **Audience:** Platform / Cloud Engineers managing AKS or EKS clusters.  
> **What you'll build:** A fully automated, Terraform-managed PKI pipeline where HashiCorp Vault acts as an internal Certificate Authority (CA), cert-manager requests and renews TLS certificates, and NGINX Ingress terminates HTTPS for workloads.

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [Prerequisites](#2-prerequisites)
3. [Repository & Terraform Layout](#3-repository--terraform-layout)
4. [Step 1 — Install Vault via Terraform (Helm)](#4-step-1--install-vault-via-terraform-helm)
5. [Step 2 — Initialise and Unseal Vault](#5-step-2--initialise-and-unseal-vault)
6. [Step 3 — Configure Vault PKI Engine via Terraform](#6-step-3--configure-vault-pki-engine-via-terraform)
7. [Step 4 — Enable Kubernetes Auth in Vault via Terraform](#7-step-4--enable-kubernetes-auth-in-vault-via-terraform)
8. [Step 5 — Install cert-manager via Terraform (Helm)](#8-step-5--install-cert-manager-via-terraform-helm)
9. [Step 6 — Configure the cert-manager Issuer via Terraform](#9-step-6--configure-the-cert-manager-issuer-via-terraform)
10. [Step 7 — Issue a Certificate via Terraform](#10-step-7--issue-a-certificate-via-terraform)
11. [Step 8 — Install NGINX Ingress Controller via Terraform](#11-step-8--install-nginx-ingress-controller-via-terraform)
12. [Step 9 — Deploy a Demo App and TLS Ingress](#12-step-9--deploy-a-demo-app-and-tls-ingress)
13. [Step 10 — Verify End-to-End TLS](#13-step-10--verify-end-to-end-tls)
14. [Certificate Renewal — How It Works](#14-certificate-renewal--how-it-works)
15. [Troubleshooting](#15-troubleshooting)
16. [Security Hardening Notes](#16-security-hardening-notes)

---

## 1. Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        Kubernetes Cluster                        │
│                                                                  │
│  ┌──────────────┐    TokenReview API    ┌────────────────────┐  │
│  │  cert-manager│◄─────────────────────►│  HashiCorp Vault   │  │
│  │  (issuer SA) │                       │  PKI Engine (CA)   │  │
│  └──────┬───────┘                       └────────────────────┘  │
│         │ Creates/Renews                                         │
│         ▼                                                        │
│  ┌──────────────┐       TLS Secret      ┌────────────────────┐  │
│  │  Certificate │──────────────────────►│  NGINX Ingress     │  │
│  │  Resource    │                       │  Controller        │  │
│  └──────────────┘                       └────────┬───────────┘  │
│                                                   │ HTTPS        │
│                                          ┌────────▼───────────┐  │
│                                          │   Demo Web App     │  │
│                                          └────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

### Component Roles

| Component | Role |
|---|---|
| **HashiCorp Vault** | Acts as the internal PKI Certificate Authority. Stores the root CA and issues short-lived leaf certificates via its PKI secrets engine. |
| **Vault Kubernetes Auth** | Allows Kubernetes workloads (like cert-manager) to authenticate with Vault using their Service Account JWT token, without needing static secrets. |
| **cert-manager** | Kubernetes controller that watches `Certificate` CRDs and automatically requests, stores, and renews TLS certificates from Vault. |
| **NGINX Ingress Controller** | Terminates TLS at the ingress layer, reading the certificate from the Kubernetes Secret cert-manager created. |
| **Terraform** | Provisions and configures all of the above declaratively and repeatably. |

---

## 2. Prerequisites

Before starting, ensure the following are available:

```bash
# Verify tools
terraform version      # >= 1.5.0
helm version           # >= 3.12
kubectl version        # >= 1.28
vault version          # >= 1.15 (local CLI for manual verification steps)
```

You will also need:
- A running Kubernetes cluster (AKS, EKS, or local like kind/minikube)
- A `kubeconfig` file pointing to the cluster
- Sufficient RBAC permissions to create namespaces, deployments, secrets, and CRDs
- Internet access to pull Helm charts (or an Artifactory proxy configured)

> **Note for air-gapped environments (e.g. Nationwide):** Replace all `repo` references with your internal Artifactory Helm registry URL and ensure images are mirrored. Add `imagePullSecrets` via your Kyverno mutation policies.

---

## 3. Repository & Terraform Layout

Organise your Terraform workspace as follows:

```
vault-certmanager/
├── providers.tf          # Provider configuration
├── variables.tf          # Input variables
├── terraform.tfvars      # Environment-specific values (do NOT commit secrets)
├── 01-vault-install.tf   # Helm release: Vault
├── 02-vault-pki.tf       # Vault PKI engine, root CA, role, policy
├── 03-vault-k8s-auth.tf  # Vault Kubernetes auth method and role
├── 04-certmanager.tf     # Helm release: cert-manager + RBAC
├── 05-issuer.tf          # cert-manager Issuer and service account
├── 06-certificate.tf     # cert-manager Certificate resource
├── 07-ingress.tf         # Helm release: ingress-nginx + demo app
└── outputs.tf            # Useful outputs
```

---

## providers.tf — Provider Configuration

This file wires together all the providers Terraform needs.

```hcl
terraform {
  required_version = ">= 1.5.0"

  required_providers {
    # Kubernetes provider: manages native Kubernetes resources (Deployments, Services, etc.)
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.27"
    }
    # Helm provider: installs Helm charts as Terraform-managed resources
    helm = {
      source  = "hashicorp/helm"
      version = "~> 2.13"
    }
    # Vault provider: configures Vault secrets engines, auth methods, roles, and policies
    vault = {
      source  = "hashicorp/vault"
      version = "~> 4.2"
    }
    # kubectl provider: applies raw Kubernetes YAML manifests (useful for CRDs cert-manager creates)
    kubectl = {
      source  = "gavinbunney/kubectl"
      version = "~> 1.14"
    }
  }
}

# --- Kubernetes Provider ---
# Reads your current kubeconfig to connect to the cluster.
provider "kubernetes" {
  config_path    = var.kubeconfig_path
  config_context = var.kubeconfig_context
}

# --- Helm Provider ---
provider "helm" {
  kubernetes {
    config_path    = var.kubeconfig_path
    config_context = var.kubeconfig_context
  }
}

# --- Vault Provider ---
# Connects to Vault using a root/admin token (only needed during bootstrap).
# In production, use AppRole or OIDC auth instead of a root token.
provider "vault" {
  address = var.vault_address
  token   = var.vault_root_token
}

# --- kubectl Provider ---
provider "kubectl" {
  config_path    = var.kubeconfig_path
  config_context = var.kubeconfig_context
}
```

---

## variables.tf

```hcl
variable "kubeconfig_path" {
  description = "Path to the kubeconfig file"
  type        = string
  default     = "~/.kube/config"
}

variable "kubeconfig_context" {
  description = "The kubeconfig context to use (leave empty for current-context)"
  type        = string
  default     = ""
}

variable "vault_address" {
  description = "The HTTP address of the Vault server"
  type        = string
  default     = "http://vault.vault.svc.cluster.local:8200"
}

variable "vault_root_token" {
  description = "Vault root or admin token — supply via TF_VAR_vault_root_token env var, never hardcode"
  type        = string
  sensitive   = true
}

variable "vault_namespace" {
  description = "Kubernetes namespace where Vault will be installed"
  type        = string
  default     = "vault"
}

variable "cert_manager_namespace" {
  description = "Kubernetes namespace for cert-manager"
  type        = string
  default     = "cert-manager"
}

variable "ingress_namespace" {
  description = "Kubernetes namespace for NGINX ingress"
  type        = string
  default     = "ingress-nginx"
}

variable "app_domain" {
  description = "The FQDN used for the demo application (must match PKI role allowed_domains)"
  type        = string
  default     = "demo.example.com"
}

variable "vault_chart_version" {
  description = "Helm chart version for Vault"
  type        = string
  default     = "0.27.0"
}

variable "cert_manager_chart_version" {
  description = "Helm chart version for cert-manager"
  type        = string
  default     = "v1.14.5"
}
```

---

## 4. Step 1 — Install Vault via Terraform (Helm)

**Why:** Vault needs to run inside the cluster so that cert-manager can reach it over the cluster-internal network without external connectivity. It also means the Kubernetes auth method can use the cluster's own API server for token verification.

### `01-vault-install.tf`

```hcl
# Create the Vault namespace
resource "kubernetes_namespace" "vault" {
  metadata {
    name = var.vault_namespace
  }
}

# Install Vault using the official HashiCorp Helm chart.
# We use a single-node (dev-like) setup here for demonstration.
# For production, use an HA setup with Raft integrated storage.
resource "helm_release" "vault" {
  name       = "vault"
  repository = "https://helm.releases.hashicorp.com"
  chart      = "vault"
  version    = var.vault_chart_version
  namespace  = kubernetes_namespace.vault.metadata[0].name

  # Wait for Vault pods to become ready before Terraform proceeds
  wait    = true
  timeout = 300

  set {
    name  = "server.dev.enabled"
    # NOTE: dev mode auto-initialises and unseals Vault with a known root token.
    # This is ONLY suitable for local testing. For production, set to false
    # and use the manual init/unseal process described in Step 2.
    value = "false"
  }

  # Use a single replica with Raft (integrated) storage for a simple HA-ready setup
  set {
    name  = "server.ha.enabled"
    value = "false"
  }

  # Expose Vault internally only — no LoadBalancer needed since cert-manager
  # reaches it via ClusterIP DNS: vault.vault.svc.cluster.local:8200
  set {
    name  = "server.service.type"
    value = "ClusterIP"
  }

  # Enable the Vault UI (useful for debugging — disable in production or restrict access)
  set {
    name  = "ui.enabled"
    value = "true"
  }

  depends_on = [kubernetes_namespace.vault]
}
```

> **Production note:** For HA Vault with Raft storage, set `server.ha.enabled=true`, `server.ha.replicas=3`, and configure `server.ha.raft.enabled=true`. Also configure persistent storage via a StorageClass.

---

## 5. Step 2 — Initialise and Unseal Vault

This step **cannot be fully automated in Terraform** on first run because Vault's unseal keys are generated at init time and must be stored securely by the operator. Subsequent unseals can be automated using cloud KMS auto-unseal (AWS KMS or Azure Key Vault).

### Manual Initialisation

```bash
# Port-forward Vault to your local machine
kubectl port-forward -n vault svc/vault 8200:8200 &

export VAULT_ADDR=http://localhost:8200

# Initialise Vault — generates 5 unseal keys, requires 3 to unseal (Shamir's Secret Sharing)
vault operator init \
  -key-shares=5 \
  -key-threshold=3 \
  -format=json > vault-init.json

# CRITICAL: Store vault-init.json securely (e.g. Azure Key Vault, AWS Secrets Manager).
# Never commit it to version control.

# Extract the root token and unseal keys
cat vault-init.json | jq -r '.root_token'
cat vault-init.json | jq -r '.unseal_keys_b64[]'

# Unseal using 3 of the 5 keys
vault operator unseal $(cat vault-init.json | jq -r '.unseal_keys_b64[0]')
vault operator unseal $(cat vault-init.json | jq -r '.unseal_keys_b64[1]')
vault operator unseal $(cat vault-init.json | jq -r '.unseal_keys_b64[2]')

# Verify Vault is unsealed and active
vault status
```

### Auto-Unseal (Production — AWS KMS example)

Add the following to your `helm_release.vault` Helm values for AWS KMS auto-unseal:

```hcl
set {
  name  = "server.extraEnvironmentVars.VAULT_SEAL_TYPE"
  value = "awskms"
}
set {
  name  = "server.extraEnvironmentVars.VAULT_AWSKMS_SEAL_KEY_ID"
  value = "arn:aws:kms:eu-west-2:123456789:key/your-kms-key-id"
}
```

For Azure Key Vault auto-unseal (AKS), use the `azurekeyvault` seal type with the corresponding Key Vault URI and key name.

---

## 6. Step 3 — Configure Vault PKI Engine via Terraform

**Why:** The PKI secrets engine turns Vault into a full Certificate Authority. It stores the root CA private key, issues signed leaf certificates, and manages certificate revocation lists (CRLs). All of this is configured declaratively via the Vault Terraform provider.

### `02-vault-pki.tf`

```hcl
# -----------------------------------------------------------------
# 1. Enable the PKI secrets engine at the path "pki"
# -----------------------------------------------------------------
# The PKI secrets engine is Vault's built-in CA. "path" determines
# where it's mounted — you can have multiple PKI mounts (e.g. one
# for internal services, one for customer-facing certs).
resource "vault_mount" "pki" {
  path                      = "pki"
  type                      = "pki"
  description               = "PKI secrets engine — acts as the internal Certificate Authority"

  # Maximum lease TTL for certificates issued from this mount.
  # 8760h = 1 year. The role's max_ttl cannot exceed this value.
  default_lease_ttl_seconds = 3600
  max_lease_ttl_seconds     = 315360000 # ~10 years for the root CA
}

# -----------------------------------------------------------------
# 2. Generate the Root CA Certificate
# -----------------------------------------------------------------
# This is the self-signed root certificate that sits at the top of
# your PKI trust chain. The private key is generated and stored
# *inside* Vault — it never leaves Vault. This is the key security
# benefit of using Vault as a CA.
resource "vault_pki_secret_backend_root_cert" "root_ca" {
  backend     = vault_mount.pki.path
  type        = "internal"  # Key generated and stored inside Vault

  common_name = "Nationwide Internal Root CA"
  ttl         = "87600h"    # 10 years for the root CA
  key_type    = "rsa"
  key_bits    = 4096        # 4096-bit RSA for root CA (stronger than 2048)
  ou          = "Platform Engineering"
  organization = "Nationwide Building Society"
  country     = "GB"
  locality    = "Swindon"

  depends_on = [vault_mount.pki]
}

# -----------------------------------------------------------------
# 3. Configure CRL and Issuing Certificate URLs
# -----------------------------------------------------------------
# cert-manager needs to know where to find:
#   - The CA certificate (issuing_certificates)
#   - The Certificate Revocation List (crl_distribution_points)
# These are embedded in every issued certificate.
resource "vault_pki_secret_backend_config_urls" "pki_urls" {
  backend = vault_mount.pki.path

  # These URLs must be reachable by certificate consumers (clients validating TLS).
  # In a cluster-internal setup, use the Vault ClusterIP service DNS.
  issuing_certificates    = ["http://vault.${var.vault_namespace}.svc.cluster.local:8200/v1/pki/ca"]
  crl_distribution_points = ["http://vault.${var.vault_namespace}.svc.cluster.local:8200/v1/pki/crl"]

  depends_on = [vault_pki_secret_backend_root_cert.root_ca]
}

# -----------------------------------------------------------------
# 4. Create a PKI Role
# -----------------------------------------------------------------
# A Vault PKI role defines the *constraints* applied to certificates
# issued under it: which domains are allowed, max TTL, key type, etc.
# cert-manager will use this role when requesting certificates.
resource "vault_pki_secret_backend_role" "example_dot_com" {
  backend = vault_mount.pki.path
  name    = "example-dot-com"

  # Allow certificates for example.com and any subdomain (*.example.com)
  allowed_domains  = ["example.com"]
  allow_subdomains = true
  allow_bare_domains = false
  allow_wildcard_certificates = false # Disable wildcards unless needed

  # Key settings
  key_type = "rsa"
  key_bits = 2048

  # Maximum TTL for issued certificates.
  # Short TTLs (minutes/hours) are a security best practice — they limit
  # the blast radius of a compromised certificate. cert-manager handles
  # automatic renewal so short TTLs are manageable.
  max_ttl = "8760h" # 1 year max; cert resources can set shorter values

  # Enforce that the CN must be in allowed_domains
  enforce_hostnames = true
  require_cn        = true

  depends_on = [vault_pki_secret_backend_config_urls.pki_urls]
}

# -----------------------------------------------------------------
# 5. Create a Vault Policy for cert-manager
# -----------------------------------------------------------------
# Vault policies control what authenticated entities are *allowed to do*.
# This policy grants cert-manager the minimum permissions needed:
#   - Read and list the PKI mount
#   - Create/update the PKI role (to request certs)
#   - Sign and issue certificates
resource "vault_policy" "pki" {
  name = "pki-cert-manager"

  policy = <<-EOT
    # Allow listing PKI mounts (needed by cert-manager to discover the backend)
    path "pki*" {
      capabilities = ["read", "list"]
    }

    # Allow cert-manager to use the PKI role to request a certificate
    path "pki/roles/example-dot-com" {
      capabilities = ["create", "update"]
    }

    # Allow cert-manager to submit a CSR and receive a signed certificate
    path "pki/sign/example-dot-com" {
      capabilities = ["create", "update"]
    }

    # Allow cert-manager to directly issue a certificate (bypasses CSR flow)
    path "pki/issue/example-dot-com" {
      capabilities = ["create", "update"]
    }
  EOT

  depends_on = [vault_pki_secret_backend_role.example_dot_com]
}
```

---

## 7. Step 4 — Enable Kubernetes Auth in Vault via Terraform

**Why:** cert-manager needs to authenticate with Vault to request certificates. Rather than using static tokens (which are a security risk), we use Vault's Kubernetes auth method. This allows cert-manager to present its Kubernetes Service Account JWT token to Vault. Vault then calls the Kubernetes TokenReview API to verify the token is legitimate. If valid, Vault issues a short-lived Vault token with the permissions defined by the bound policy.

### `03-vault-k8s-auth.tf`

```hcl
# -----------------------------------------------------------------
# 1. Enable the Kubernetes Auth Method in Vault
# -----------------------------------------------------------------
# This tells Vault: "I want to allow Kubernetes Service Accounts
# to authenticate with me."
resource "vault_auth_backend" "kubernetes" {
  type        = "kubernetes"
  path        = "kubernetes"
  description = "Kubernetes auth method — allows pods to authenticate using their SA JWT tokens"

  depends_on = [vault_policy.pki]
}

# -----------------------------------------------------------------
# 2. Configure the Kubernetes Auth Backend
# -----------------------------------------------------------------
# Vault needs to know *how* to verify incoming Kubernetes JWT tokens.
# It does this by calling the Kubernetes API TokenReview endpoint.
#
# IMPORTANT: The config below reads the token and CA cert from the
# Vault pod's own mounted service account — this is the recommended
# approach as it avoids hardcoding credentials.
#
# For Terraform, we reference these as data sources from the cluster.
data "kubernetes_secret" "vault_sa_token" {
  metadata {
    name      = "vault"
    namespace = var.vault_namespace
  }

  depends_on = [helm_release.vault]
}

resource "vault_kubernetes_auth_backend_config" "k8s_config" {
  backend = vault_auth_backend.kubernetes.path

  # The Kubernetes API server URL — Vault calls this to verify JWTs
  kubernetes_host = "https://kubernetes.default.svc.cluster.local:443"

  # The CA certificate used to verify the Kubernetes API server's TLS cert
  # This is the cluster's CA, available from any pod at the standard path
  kubernetes_ca_cert = base64decode(
    data.kubernetes_secret.vault_sa_token.data["ca.crt"]
  )

  # Vault's own service account JWT — used to call the TokenReview API
  token_reviewer_jwt = data.kubernetes_secret.vault_sa_token.data["token"]

  # Vault will periodically re-read these values to support token rotation
  issuer = "https://kubernetes.default.svc.cluster.local"

  depends_on = [vault_auth_backend.kubernetes]
}

# -----------------------------------------------------------------
# 3. Create a Kubernetes Auth Role for cert-manager
# -----------------------------------------------------------------
# This role binds:
#   - A Kubernetes Service Account name (the cert-manager "issuer" SA)
#   - The namespaces it can live in
#   - The Vault policy it will receive upon successful authentication
#
# When cert-manager presents its JWT token, Vault:
#   1. Calls Kubernetes TokenReview API to verify the JWT is valid
#   2. Checks the SA name and namespace match this role's bindings
#   3. Issues a Vault token with the "pki-cert-manager" policy attached
resource "vault_kubernetes_auth_backend_role" "issuer" {
  backend = vault_auth_backend.kubernetes.path
  role_name = "issuer"

  # The Kubernetes Service Account cert-manager will use to authenticate
  bound_service_account_names      = ["issuer"]

  # cert-manager typically runs in cert-manager namespace; "default" included for demo app
  bound_service_account_namespaces = [var.cert_manager_namespace, "default"]

  # The Vault policy granted upon successful authentication
  token_policies = [vault_policy.pki.name]

  # How long the resulting Vault token is valid
  # cert-manager renews its token before expiry, so 20m is sufficient
  token_ttl = 1200  # 20 minutes in seconds

  depends_on = [vault_kubernetes_auth_backend_config.k8s_config]
}
```

---

## 8. Step 5 — Install cert-manager via Terraform (Helm)

**Why:** cert-manager is the Kubernetes-native certificate controller. It watches `Certificate` custom resources and handles the full lifecycle: requesting certificates from Vault, storing them as Kubernetes Secrets, and automatically renewing them before expiry.

### `04-certmanager.tf`

```hcl
# Create the cert-manager namespace
resource "kubernetes_namespace" "cert_manager" {
  metadata {
    name = var.cert_manager_namespace
  }
}

# Install cert-manager via Helm
# cert-manager installs three components:
#   - cert-manager controller: watches Certificate resources, triggers issuance
#   - webhook: validates and mutates cert-manager CRD objects
#   - cainjector: injects CA bundles into webhook configs and APIService objects
resource "helm_release" "cert_manager" {
  name       = "cert-manager"
  repository = "https://charts.jetstack.io"
  chart      = "cert-manager"
  version    = var.cert_manager_chart_version
  namespace  = kubernetes_namespace.cert_manager.metadata[0].name

  # Install the CRDs (Certificate, Issuer, ClusterIssuer, etc.)
  # Setting this via Helm values ensures CRDs are managed alongside the chart
  set {
    name  = "installCRDs"
    value = "true"
  }

  # Wait for all cert-manager pods to be Running before Terraform continues
  wait    = true
  timeout = 300

  depends_on = [
    kubernetes_namespace.cert_manager,
    vault_kubernetes_auth_backend_role.issuer
  ]
}

# -----------------------------------------------------------------
# Create the "issuer" Service Account
# -----------------------------------------------------------------
# This is the Service Account cert-manager uses when authenticating
# with Vault. It must match the name bound in the Vault auth role.
resource "kubernetes_service_account" "issuer" {
  metadata {
    name      = "issuer"
    namespace = "default"  # Must match vault_kubernetes_auth_backend_role bound namespaces
  }

  depends_on = [helm_release.cert_manager]
}

# -----------------------------------------------------------------
# Create a long-lived Service Account Token Secret
# -----------------------------------------------------------------
# Kubernetes 1.24+ no longer auto-creates long-lived tokens for SAs.
# cert-manager's Vault Issuer requires a static token reference.
# We create one explicitly here.
resource "kubernetes_secret" "issuer_token" {
  metadata {
    name      = "issuer-token"
    namespace = "default"
    annotations = {
      "kubernetes.io/service-account.name" = kubernetes_service_account.issuer.metadata[0].name
    }
  }

  type = "kubernetes.io/service-account-token"

  depends_on = [kubernetes_service_account.issuer]
}
```

---

## 9. Step 6 — Configure the cert-manager Issuer via Terraform

**Why:** The `Issuer` resource tells cert-manager *how* to talk to Vault — which URL to reach it at, which PKI path to use for signing, and how to authenticate (using the service account token we just created).

### `05-issuer.tf`

```hcl
# -----------------------------------------------------------------
# Create the cert-manager Issuer resource
# -----------------------------------------------------------------
# An Issuer is namespace-scoped. Use ClusterIssuer if you want
# certificates to be requestable from any namespace in the cluster.
#
# This resource is a Kubernetes custom resource (CRD), so we use
# the kubectl provider to apply it as raw YAML.
resource "kubectl_manifest" "vault_issuer" {
  yaml_body = yamlencode({
    apiVersion = "cert-manager.io/v1"
    kind       = "Issuer"
    metadata = {
      name      = "vault-issuer"
      namespace = "default"
    }
    spec = {
      vault = {
        # Internal Vault service URL — cert-manager calls this to request certs
        server = "http://vault.${var.vault_namespace}.svc.cluster.local:8200"

        # The Vault PKI path where cert signing happens.
        # Must match the role created in Step 3.
        path = "pki/sign/example-dot-com"

        auth = {
          kubernetes = {
            # The mount path of the Kubernetes auth method in Vault
            mountPath = "/v1/auth/kubernetes"

            # The Vault auth role cert-manager will authenticate as
            role = "issuer"

            # Reference to the service account token secret.
            # cert-manager reads this JWT token and presents it to Vault.
            secretRef = {
              name = kubernetes_secret.issuer_token.metadata[0].name
              key  = "token"
            }
          }
        }
      }
    }
  })

  depends_on = [
    helm_release.cert_manager,
    kubernetes_secret.issuer_token,
    vault_kubernetes_auth_backend_role.issuer
  ]
}
```

### Verify the Issuer

After applying, check the Issuer status:

```bash
kubectl describe issuer vault-issuer -n default
# Look for: Status: True, Reason: VaultVerified
```

---

## 10. Step 7 — Issue a Certificate via Terraform

**Why:** A `Certificate` resource is the declaration of *what* certificate you want. cert-manager reads it, contacts the referenced Issuer (Vault), and stores the issued certificate in a Kubernetes Secret. It also monitors expiry and renews automatically.

### `06-certificate.tf`

```hcl
resource "kubectl_manifest" "demo_certificate" {
  yaml_body = yamlencode({
    apiVersion = "cert-manager.io/v1"
    kind       = "Certificate"
    metadata = {
      name      = "demo-example-com"
      namespace = "default"
    }
    spec = {
      # The Kubernetes Secret where the issued certificate will be stored.
      # This Secret will contain: tls.crt (certificate chain), tls.key (private key), ca.crt (CA cert)
      secretName = "example-com-tls"

      # cert-manager will start renewing the certificate when this much time is left.
      # e.g. if duration=8760h and renewBefore=720h, renewal starts 30 days before expiry.
      duration    = "8760h"   # 1 year
      renewBefore = "720h"    # Begin renewal 30 days before expiry

      # The Common Name embedded in the certificate
      commonName = var.app_domain

      # SAN (Subject Alternative Names) — modern TLS relies on these, not CN
      dnsNames = [var.app_domain]

      # Reference to the Issuer created in Step 6
      issuerRef = {
        name = "vault-issuer"
        kind = "Issuer"
      }

      # Private key settings for the issued certificate (not the CA key)
      privateKey = {
        algorithm = "RSA"
        size      = 2048
        rotationPolicy = "Always"  # Generate a new key on every renewal
      }
    }
  })

  depends_on = [kubectl_manifest.vault_issuer]
}
```

### Verify Certificate Issuance

```bash
# Watch the certificate until it's Ready
kubectl get certificate demo-example-com -n default -w

# Inspect the full certificate status and events
kubectl describe certificate demo-example-com -n default

# Inspect the resulting TLS Secret
kubectl get secret example-com-tls -n default -o yaml

# Decode and inspect the actual certificate
kubectl get secret example-com-tls -n default \
  -o jsonpath='{.data.tls\.crt}' | base64 -d | openssl x509 -noout -text
```

---

## 11. Step 8 — Install NGINX Ingress Controller via Terraform

**Why:** The ingress controller is the gateway that handles incoming HTTPS traffic. It reads the `Ingress` resource to know which hostname maps to which backend service, and reads the TLS secret to terminate the SSL connection.

### `07-ingress.tf`

```hcl
# Create the ingress namespace
resource "kubernetes_namespace" "ingress_nginx" {
  metadata {
    name = var.ingress_namespace
  }
}

# Install ingress-nginx via Helm
resource "helm_release" "ingress_nginx" {
  name       = "ingress-nginx"
  repository = "https://kubernetes.github.io/ingress-nginx"
  chart      = "ingress-nginx"
  namespace  = kubernetes_namespace.ingress_nginx.metadata[0].name

  set {
    name  = "controller.service.type"
    # Use LoadBalancer for cloud clusters (AKS, EKS), NodePort for local
    value = "LoadBalancer"
  }

  # Wait for the ingress controller pod to be Ready
  wait    = true
  timeout = 300

  depends_on = [kubernetes_namespace.ingress_nginx]
}
```

---

## 12. Step 9 — Deploy a Demo App and TLS Ingress

### `07-ingress.tf` (continued)

```hcl
# -----------------------------------------------------------------
# Demo Application Deployment
# -----------------------------------------------------------------
resource "kubernetes_deployment" "web" {
  metadata {
    name      = "web"
    namespace = "default"
    labels    = { app = "web" }
  }

  spec {
    replicas = 2

    selector {
      match_labels = { app = "web" }
    }

    template {
      metadata {
        labels = { app = "web" }
      }

      spec {
        container {
          name  = "web"
          image = "gcr.io/google-samples/hello-app:1.0"
          port {
            container_port = 8080
          }
        }
      }
    }
  }

  depends_on = [helm_release.ingress_nginx]
}

# Expose the application within the cluster
resource "kubernetes_service" "web" {
  metadata {
    name      = "web"
    namespace = "default"
  }

  spec {
    selector = { app = "web" }
    port {
      port        = 8080
      target_port = 8080
    }
    type = "ClusterIP"
  }

  depends_on = [kubernetes_deployment.web]
}

# -----------------------------------------------------------------
# Ingress Resource — Wires TLS to the Application
# -----------------------------------------------------------------
# This Ingress tells NGINX: "For requests to demo.example.com,
# use the TLS cert in the 'example-com-tls' secret, and proxy
# traffic to the 'web' service on port 8080."
resource "kubectl_manifest" "example_ingress" {
  yaml_body = yamlencode({
    apiVersion = "networking.k8s.io/v1"
    kind       = "Ingress"
    metadata = {
      name      = "example-ingress"
      namespace = "default"
      annotations = {
        "kubernetes.io/ingress.class"                  = "nginx"
        "nginx.ingress.kubernetes.io/ssl-redirect"     = "true"
        # Force HTTP → HTTPS redirect
        "nginx.ingress.kubernetes.io/force-ssl-redirect" = "true"
      }
    }
    spec = {
      ingressClassName = "nginx"
      tls = [
        {
          hosts      = [var.app_domain]
          # This secret is created by cert-manager when the Certificate is issued
          secretName = "example-com-tls"
        }
      ]
      rules = [
        {
          host = var.app_domain
          http = {
            paths = [
              {
                path     = "/"
                pathType = "Prefix"
                backend = {
                  service = {
                    name = "web"
                    port = { number = 8080 }
                  }
                }
              }
            ]
          }
        }
      ]
    }
  })

  depends_on = [
    kubectl_manifest.demo_certificate,
    kubernetes_service.web
  ]
}
```

---

## outputs.tf

```hcl
output "vault_service_url" {
  description = "Internal ClusterIP URL for Vault"
  value       = "http://vault.${var.vault_namespace}.svc.cluster.local:8200"
}

output "ingress_load_balancer_ip" {
  description = "External IP of the NGINX Ingress LoadBalancer (may take a minute to provision)"
  value       = helm_release.ingress_nginx.status
}

output "cert_manager_issuer_name" {
  description = "Name of the cert-manager Vault Issuer"
  value       = "vault-issuer"
}

output "tls_secret_name" {
  description = "Name of the Kubernetes Secret containing the issued TLS certificate"
  value       = "example-com-tls"
}
```

---

## 13. Step 10 — Verify End-to-End TLS

### Apply All Terraform

```bash
# Initialise — downloads all providers
terraform init

# Preview what will be created
terraform plan -out=tfplan

# Apply in two stages to handle provider dependency ordering:
# Stage 1: Install Vault and cert-manager infrastructure
terraform apply -target=helm_release.vault \
                -target=helm_release.cert_manager \
                -target=helm_release.ingress_nginx

# After manual Vault init/unseal (Step 2), apply the rest:
terraform apply
```

### Simulate DNS Resolution

```bash
# Get the external IP assigned to the NGINX ingress LoadBalancer
kubectl get svc -n ingress-nginx ingress-nginx-controller

# Add a local hosts entry for testing (replace <EXTERNAL-IP> with actual IP)
echo "<EXTERNAL-IP> demo.example.com" | sudo tee -a /etc/hosts
```

### Test HTTPS

```bash
# Full TLS handshake details — shows certificate validity dates and issuer
curl -kivL https://demo.example.com

# Expected output includes:
#  subject: CN=demo.example.com
#  issuer: CN=Nationwide Internal Root CA
#  start date: <now>
#  expire date: <now + duration>
```

### Check Certificate Events

```bash
# Watch cert-manager controller logs in real time
kubectl logs -n cert-manager \
  -l app=cert-manager \
  -f --tail=50

# Describe the CertificateRequest object created during issuance
kubectl get certificaterequest -n default
kubectl describe certificaterequest <name> -n default
```

---

## 14. Certificate Renewal — How It Works

cert-manager fully automates certificate renewal. Here's the end-to-end flow:

```
Certificate resource created
        │
        ▼
cert-manager creates a CertificateRequest
        │
        ▼
cert-manager generates a private key and CSR
        │
        ▼
cert-manager authenticates with Vault (SA JWT → Vault token)
        │
        ▼
cert-manager submits CSR to Vault PKI (pki/sign/example-dot-com)
        │
        ▼
Vault signs the CSR and returns the certificate
        │
        ▼
cert-manager stores the cert in Kubernetes Secret (example-com-tls)
        │
        ▼
NGINX Ingress reads the updated Secret automatically
        │
        ▼
[renewBefore threshold approached]
        │
        ▼
cert-manager repeats the process ← ─────────────────────────┘
```

Key renewal parameters in the `Certificate` resource:
- `duration`: Total certificate validity period
- `renewBefore`: How far ahead of expiry cert-manager starts renewing
- `privateKey.rotationPolicy: Always`: Generates a fresh key on every renewal (recommended)

---

## 15. Troubleshooting

### Certificate Stuck in `False` / `Issuing` State

```bash
# Check Certificate status and events
kubectl describe certificate demo-example-com -n default

# Check CertificateRequest for Vault error messages
kubectl describe certificaterequest -n default

# Check cert-manager controller logs for detailed errors
kubectl logs -n cert-manager deployment/cert-manager -f
```

**Common causes:**
| Symptom | Likely Cause |
|---|---|
| `403 permission denied` | Vault policy is missing `create/update` on the PKI path |
| `connection refused` | Vault URL is wrong or Vault is sealed |
| `JWT token expired` | SA token too old; recreate the issuer-token secret |
| `Issuer not ready` | Vault Kubernetes auth config is incorrect; check the TokenReview |
| `x509: certificate signed by unknown authority` | cert-manager doesn't trust Vault's CA; add `caBundle` to Issuer spec |

### Vault is Sealed After Pod Restart

Vault does not auto-unseal after a pod restart unless you've configured auto-unseal (AWS KMS / Azure Key Vault). You must run:

```bash
kubectl exec -n vault vault-0 -- vault status
kubectl exec -n vault vault-0 -- vault operator unseal <key1>
kubectl exec -n vault vault-0 -- vault operator unseal <key2>
kubectl exec -n vault vault-0 -- vault operator unseal <key3>
```

### Check Vault PKI from Inside the Cluster

```bash
# Exec into any pod and test the Vault API directly
kubectl run debug --image=curlimages/curl -it --rm --restart=Never -- \
  curl -s http://vault.vault.svc.cluster.local:8200/v1/sys/health | jq
```

---

## 16. Security Hardening Notes

These are important for a production Nationwide environment:

1. **Never use root tokens in Terraform CI/CD.** Use AppRole auth or OIDC with short-lived tokens. Store `vault_root_token` in Azure Key Vault or AWS Secrets Manager, not in `.tfvars` files.

2. **Enable Vault Audit Logging.** All certificate issuance events should be logged:
   ```hcl
   resource "vault_audit" "file" {
     type = "file"
     options = { file_path = "/vault/logs/audit.log" }
   }
   ```

3. **Use `ClusterIssuer` cautiously.** If cross-namespace certificate issuance is needed, use `ClusterIssuer` and restrict it with Kyverno policies to only permit approved namespaces.

4. **Restrict Vault network access.** Apply Kubernetes `NetworkPolicy` to only allow cert-manager pods to reach Vault on port 8200. This aligns with the pentest hardening work done for webhook pods.

5. **Rotate root CA periodically.** Vault supports intermediate CAs — consider using a short-lived intermediate CA signed by a long-lived offline root CA for better security posture.

6. **Use an intermediate CA instead of a root CA.** For production, create a root CA and an intermediate CA mounted separately. cert-manager signs via the intermediate. This limits blast radius if the intermediate is compromised.

   ```hcl
   # Example: separate pki_int mount for intermediate CA
   resource "vault_mount" "pki_int" {
     path = "pki_int"
     type = "pki"
     max_lease_ttl_seconds = 157680000 # 5 years
   }
   ```

7. **Enable Trivy scanning on the Vault and cert-manager images** using your existing Trivy Operator deployment to catch CVEs in these critical infrastructure components.

---

*Document version: 1.0 | Maintainer: Platform Engineering | Last updated: 2026*
