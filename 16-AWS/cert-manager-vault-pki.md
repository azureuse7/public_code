# cert-manager + HashiCorp Vault PKI Integration

> This document explains how cert-manager delegates certificate signing to HashiCorp Vault's PKI secrets engine — covering the architecture, authentication flow, certificate issuance lifecycle, and all pre-requisites.

---

## Table of Contents

1. [Overview](#overview)
2. [The ClusterIssuer YAML explained](#the-clusterissuer-yaml-explained)
3. [Vault PKI Engine (the CA side)](#vault-pki-engine-the-ca-side)
4. [Vault Kubernetes Authentication](#vault-kubernetes-authentication)
5. [Full Certificate Issuance Flow](#full-certificate-issuance-flow)
6. [What the PKI Role Enforces](#what-the-pki-role-enforces)
7. [Pre-requisites (Admin Setup)](#pre-requisites-admin-setup)
8. [Why Vault instead of a simple CA?](#why-vault-instead-of-a-simple-ca)
9. [Field Reference Summary](#field-reference-summary)

---

## Overview

In Kubernetes, workloads require TLS certificates constantly — for Ingress termination, for mTLS between services, for internal APIs. Someone must *sign* those certificates. That authority is a **Certificate Authority (CA)**.

By default, cert-manager can act as its own CA — it holds a root CA private key inside a Kubernetes Secret. This works, but carries several risks and limitations:

- The root CA private key lives in Kubernetes, increasing blast radius if the cluster is compromised
- No centralised audit log of what got signed
- Separate CA hierarchy from non-Kubernetes workloads

**With Vault as the issuer**, cert-manager outsources all certificate signing to Vault's PKI secrets engine. Vault *is* the CA; cert-manager is a client that submits Certificate Signing Requests (CSRs). The private key is generated inside Kubernetes and **never leaves the cluster**.

### High-level flow

```
Your App / Ingress
      │  requests cert via Certificate resource
      ▼
cert-manager (watches Certificate resources)
      │  generates private key + CSR in-cluster
      ▼
Authenticates to Vault using Kubernetes ServiceAccount token
      │
      ▼
POSTs CSR to Vault PKI engine (pki/sign/my-role)
      │
      ▼
Vault validates CSR against role policy, signs with Intermediate CA
      │
      ▼
cert-manager stores signed cert + private key in Kubernetes Secret
      │
      ▼
Ingress controller / pod mounts the Secret automatically
```

---

## The ClusterIssuer YAML explained

```yaml
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: internal-ca-issuer
spec:
  vault:
    server: https://vault.internal.example.com     # Vault API endpoint
    path: pki/sign/my-role                         # Vault PKI role endpoint
    auth:
      kubernetes:
        role: cert-manager                         # Vault auth role name
        mountPath: /v1/auth/kubernetes             # Where K8s auth is mounted in Vault
        secretRef:
          name: vault-token                        # K8s Secret holding the SA token
          key: token
```

| Field | Purpose |
|---|---|
| `spec.vault.server` | The Vault cluster URL cert-manager sends all API calls to |
| `spec.vault.path` | The PKI sign endpoint — `<mount>/sign/<role>`. The role is the policy enforcement point |
| `auth.kubernetes.role` | The Vault auth role cert-manager claims — maps to an allowed ServiceAccount + namespace |
| `auth.kubernetes.mountPath` | The path where Vault's Kubernetes auth method is mounted |
| `auth.kubernetes.secretRef` | The Kubernetes Secret containing the ServiceAccount JWT used to authenticate to Vault |

---

## Vault PKI Engine (the CA side)

Vault's PKI secrets engine functions as a full CA service. It is organised in layers:

```
Root CA  (self-signed, kept offline or in HSM)
    │
    └── signs ──▶  Intermediate CA  (used for day-to-day signing)
                        │
                        └── PKI secrets engine mounted at pki/
                                │
                                ├── Role: my-role  (policy: allowed domains, max TTL, key type)
                                │
                                └── Endpoint: pki/sign/my-role  (accepts CSRs, returns signed cert)
```

### Root CA

The trust anchor for your organisation. Everything trusts this certificate. Typically kept offline (air-gapped) or backed by an HSM. You do not use this for day-to-day signing.

### Intermediate CA

Signed by the Root CA and used for all active certificate issuance. If it is ever compromised, you revoke and re-issue the Intermediate without touching the Root. This is standard PKI hygiene.

### PKI secrets engine mount (`pki/`)

In Vault, secrets engines are mounted at a path — similar to a filesystem mount. Your PKI engine lives at `pki/`. All API calls are relative to this mount point.

### PKI Role (`my-role`)

A named configuration inside the PKI engine that defines the *rules* of what can be signed:

```hcl
vault write pki/roles/my-role \
  allowed_domains="internal.example.com" \
  allow_subdomains=true \
  allow_bare_domains=false \
  max_ttl="720h" \
  ttl="72h" \
  key_type="rsa" \
  key_bits=2048 \
  require_cn=true \
  allow_ip_sans=false \
  server_flag=true \
  client_flag=false
```

This is your **policy enforcement point**. cert-manager cannot issue a certificate that violates these constraints — Vault will reject the request with a 400 error.

### Sign endpoint (`pki/sign/my-role`)

The API path cert-manager POSTs CSRs to. Vault validates the CSR against the role, signs it with the Intermediate CA, and returns the signed certificate. The key distinction:

- `pki/sign/<role>` — cert-manager provides the CSR (private key stays in Kubernetes ✅)
- `pki/issue/<role>` — Vault generates both the key and cert (private key travels over the network ⚠️)

**Always use `sign/` not `issue/` with cert-manager.**

---

## Vault Kubernetes Authentication

Before Vault will sign anything, cert-manager must *authenticate*. The Kubernetes auth method leverages the trust Kubernetes already has in its own ServiceAccount tokens.

### Authentication steps

```
Step 1: Kubernetes injects a JWT ServiceAccount token into the cert-manager pod
        (at /var/run/secrets/kubernetes.io/serviceaccount/token)

Step 2: cert-manager POSTs to Vault's login endpoint
        POST /v1/auth/kubernetes/login
        { "jwt": "<SA token>", "role": "cert-manager" }

Step 3: Vault calls the Kubernetes TokenReview API
        POST /apis/authentication.k8s.io/v1/tokenreviews
        Kubernetes confirms: "Yes, this JWT is valid. It belongs to
        ServiceAccount cert-manager in namespace cert-manager."

Step 4: Vault checks its auth role binding
        Is SA 'cert-manager' in namespace 'cert-manager' bound to
        Vault role 'cert-manager'? → Yes

Step 5: Vault issues a short-lived Vault token scoped to the pki-sign-policy
        cert-manager receives this token and uses it for the CSR submission
```

### The Vault auth role (pre-created by the platform/Vault admin)

```hcl
vault write auth/kubernetes/role/cert-manager \
  bound_service_account_names=cert-manager \
  bound_service_account_namespaces=cert-manager \
  policies=pki-sign-policy \
  ttl=1h
```

This role says:
- Only the `cert-manager` ServiceAccount in the `cert-manager` namespace can use this role
- The resulting Vault token is granted the `pki-sign-policy` permissions
- The Vault token expires after 1 hour

### The Vault policy (pre-created by the platform/Vault admin)

```hcl
# pki-sign-policy
path "pki/sign/my-role" {
  capabilities = ["create", "update"]
}
```

cert-manager is granted only the minimum required permission — it can POST to the sign endpoint and nothing else. It cannot read other secrets, manage the PKI engine, or access other paths.

---

## Full Certificate Issuance Flow

### Example scenario

You deploy an Ingress for `api.internal.example.com`:

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  annotations:
    cert-manager.io/cluster-issuer: internal-ca-issuer
spec:
  tls:
  - hosts:
    - api.internal.example.com
    secretName: api-tls-secret
  rules:
  - host: api.internal.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: api-service
            port:
              number: 8080
```

### Step-by-step

**Step 1 — cert-manager detects the Ingress**

cert-manager watches for the `cert-manager.io/cluster-issuer` annotation and automatically creates a `Certificate` resource:

```yaml
apiVersion: cert-manager.io/v1
kind: Certificate
metadata:
  name: api-tls-secret
  namespace: default
spec:
  secretName: api-tls-secret
  issuerRef:
    name: internal-ca-issuer
    kind: ClusterIssuer
  dnsNames:
  - api.internal.example.com
```

**Step 2 — Private key and CSR generated in-cluster**

cert-manager generates a 2048-bit RSA private key (or EC P-256, depending on your configuration) entirely within Kubernetes memory. It creates a CSR — a file containing:
- The requested subject (`CN=api.internal.example.com`)
- The public key
- A signature proving ownership of the corresponding private key

The private key **never leaves Kubernetes**.

**Step 3 — Authenticate to Vault**

cert-manager reads the ServiceAccount token from the `vault-token` Secret and POSTs to Vault:

```
POST https://vault.internal.example.com/v1/auth/kubernetes/login
Content-Type: application/json

{
  "jwt": "eyJhbGciOiJSUzI1NiIsInR5cCI6...",
  "role": "cert-manager"
}
```

Vault validates the JWT against the Kubernetes TokenReview API, checks the role binding, and returns a short-lived Vault token (e.g. `s.abc123xyz...`).

**Step 4 — Submit CSR to Vault**

cert-manager POSTs the CSR to the sign endpoint:

```
POST https://vault.internal.example.com/v1/pki/sign/my-role
X-Vault-Token: s.abc123xyz...
Content-Type: application/json

{
  "csr": "-----BEGIN CERTIFICATE REQUEST-----\nMIIC...\n-----END CERTIFICATE REQUEST-----",
  "common_name": "api.internal.example.com",
  "ttl": "72h"
}
```

Vault validates:
- Is `api.internal.example.com` covered by the role's `allowed_domains`?
- Is `72h` within the role's `max_ttl`?
- Does the CSR signature verify against the public key?

If all checks pass, Vault signs the CSR with the Intermediate CA.

**Step 5 — Vault returns the signed certificate**

```json
{
  "data": {
    "certificate": "-----BEGIN CERTIFICATE-----\nMIID...\n-----END CERTIFICATE-----",
    "issuing_ca": "-----BEGIN CERTIFICATE-----\nMIID...\n-----END CERTIFICATE-----",
    "ca_chain": [
      "-----BEGIN CERTIFICATE-----\nMIID...\n-----END CERTIFICATE-----"
    ],
    "serial_number": "1a:2b:3c:4d:...",
    "expiration": 1720000000
  }
}
```

**Step 6 — cert-manager stores the result**

cert-manager creates (or updates) the Kubernetes Secret `api-tls-secret`:

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: api-tls-secret
  namespace: default
type: kubernetes.io/tls
data:
  tls.crt: <base64(signed cert + intermediate chain)>
  tls.key: <base64(private key — never left K8s)>
```

The Ingress controller automatically mounts this Secret and terminates TLS with the issued certificate.

**Step 7 — Automatic renewal**

cert-manager monitors the certificate expiry. By default, it renews at 2/3 of the certificate's lifetime (e.g. for a 72-hour cert, renewal starts at ~48 hours). The entire flow above repeats automatically — no human intervention required.

---

## What the PKI Role Enforces

Using the role configuration from the example above, here is what Vault will accept and reject:

| Request | Result | Reason |
|---|---|---|
| `api.internal.example.com` | ✅ Allowed | Subdomain of `internal.example.com` |
| `db.internal.example.com` | ✅ Allowed | Subdomain of `internal.example.com` |
| `internal.example.com` | ❌ Rejected | `allow_bare_domains=false` |
| `evil.com` | ❌ Rejected | Not in `allowed_domains` |
| TTL of 8760h (1 year) | ❌ Rejected | Exceeds `max_ttl=720h` |
| IP SAN `10.0.0.5` | ❌ Rejected | `allow_ip_sans=false` |
| Client certificate | ❌ Rejected | `client_flag=false` |

cert-manager has no way to bypass these checks — they are enforced server-side by Vault.

---

## Pre-requisites (Admin Setup)

The `ClusterIssuer` YAML assumes the following has already been configured by the Vault and platform admin. The `ClusterIssuer` will fail silently or error until all of these are in place.

### 1. Enable the PKI secrets engine

```bash
vault secrets enable pki
vault secrets tune -max-lease-ttl=87600h pki
```

### 2. Generate the Root CA

```bash
vault write pki/root/generate/internal \
  common_name="My Internal Root CA" \
  ttl=87600h
```

### 3. Create the Intermediate CA (recommended)

```bash
# Enable a separate mount for the intermediate
vault secrets enable -path=pki_int pki
vault secrets tune -max-lease-ttl=43800h pki_int

# Generate intermediate CSR
vault write pki_int/intermediate/generate/internal \
  common_name="My Internal Intermediate CA" \
  ttl=43800h

# Sign the intermediate with the root
vault write pki/root/sign-intermediate \
  csr=<intermediate_csr> \
  common_name="My Internal Intermediate CA" \
  ttl=43800h

# Import the signed intermediate back
vault write pki_int/intermediate/set-signed \
  certificate=<signed_cert>
```

### 4. Create the PKI role

```bash
vault write pki/roles/my-role \
  allowed_domains="internal.example.com" \
  allow_subdomains=true \
  allow_bare_domains=false \
  max_ttl="720h" \
  ttl="72h" \
  key_type="rsa" \
  key_bits=2048 \
  require_cn=true \
  allow_ip_sans=false \
  server_flag=true \
  client_flag=false
```

### 5. Create the Vault policy

```bash
vault policy write pki-sign-policy - <<EOF
path "pki/sign/my-role" {
  capabilities = ["create", "update"]
}
EOF
```

### 6. Enable the Kubernetes auth method

```bash
vault auth enable kubernetes

vault write auth/kubernetes/config \
  kubernetes_host="https://your-k8s-api.internal:443" \
  kubernetes_ca_cert=@/path/to/k8s-ca.pem \
  token_reviewer_jwt=@/path/to/reviewer-token
```

### 7. Create the Vault auth role bound to cert-manager

```bash
vault write auth/kubernetes/role/cert-manager \
  bound_service_account_names=cert-manager \
  bound_service_account_namespaces=cert-manager \
  policies=pki-sign-policy \
  ttl=1h
```

### 8. Create the Kubernetes Secret for the token

```bash
# For clusters using long-lived SA tokens:
kubectl create secret generic vault-token \
  -n cert-manager \
  --from-literal=token=$(kubectl create token cert-manager -n cert-manager)

# Or create a long-lived SA token Secret (older clusters):
kubectl apply -f - <<EOF
apiVersion: v1
kind: Secret
metadata:
  name: vault-token
  namespace: cert-manager
  annotations:
    kubernetes.io/service-account.name: cert-manager
type: kubernetes.io/service-account-token
EOF
```

---

## Why Vault instead of a simple CA?

| Feature | cert-manager built-in CA | Vault PKI issuer |
|---|---|---|
| CA key location | Kubernetes Secret | Vault (optionally HSM-backed) |
| Cross-platform PKI | No (K8s only) | Yes (K8s, VMs, bare metal all share the same CA) |
| Audit log per signing request | No | Yes (Vault audit log) |
| Policy enforcement on issuance | No | Yes (role: allowed domains, TTL, key type) |
| Dynamic short-lived certs | Manual | Native — short TTLs + auto-renewal |
| Revocation (CRL / OCSP) | No | Yes |
| Compromise blast radius | Cluster-wide | Scoped to Intermediate CA only |
| Multi-team access control | No | Yes (Vault policies per team) |

---

## Field Reference Summary

```yaml
spec:
  vault:
    server: https://vault.internal.example.com
    # The Vault cluster API endpoint. cert-manager makes HTTPS calls here.

    path: pki/sign/my-role
    # <pki-mount>/sign/<role-name>
    # - pki/        → the PKI secrets engine mount point
    # - sign/       → use 'sign' so the private key stays in Kubernetes
    # - my-role     → the Vault PKI role that enforces issuance policy

    auth:
      kubernetes:
        role: cert-manager
        # The Vault auth role that maps a Kubernetes ServiceAccount to
        # Vault policies. Created in advance by the Vault admin.

        mountPath: /v1/auth/kubernetes
        # Where the Kubernetes auth method is mounted in Vault.
        # Default: /v1/auth/kubernetes (matches 'vault auth enable kubernetes')

        secretRef:
          name: vault-token
          key: token
          # The Kubernetes Secret containing the ServiceAccount JWT.
          # cert-manager presents this to Vault to prove its identity.
```

---

*Document covers: cert-manager `ClusterIssuer` with Vault PKI, Kubernetes auth method, CSR-based signing flow, and platform setup.*
