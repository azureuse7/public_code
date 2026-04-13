# AKS Ingress: Complete End-to-End Guide

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [How a Request Flows End-to-End](#2-how-a-request-flows-end-to-end)
3. [Azure Load Balancer](#3-azure-load-balancer)
4. [NGINX Ingress Controller](#4-nginx-ingress-controller)
5. [cert-manager and Let's Encrypt](#5-cert-manager-and-lets-encrypt)
6. [ExternalDNS and Azure DNS](#6-externaldns-and-azure-dns)
7. [HashiCorp Vault — Secret Injection](#7-hashicorp-vault--secret-injection)
8. [Putting It All Together — Full Deployment](#8-putting-it-all-together--full-deployment)
9. [Troubleshooting Reference](#9-troubleshooting-reference)

---

## 1. Architecture Overview

 The diagram below represents the full request lifecycle.

```
Internet
   |
   |  DNS lookup: myapp.example.com -> 52.154.156.139
   v
Azure DNS / private DNS
   |  A record: myapp -> 52.154.156.139   <- managed by ExternalDNS
   v
Azure Load Balancer (public or internal)
   |  TCP passthrough on port 443 / 80
   v
NGINX Ingress Controller (Pod in ingress-basic namespace)
   |  TLS termination using cert managed by cert-manager
   |  Route: Host=myapp.example.com, Path=/api -> api-service:80
   v
ClusterIP Service (api-service)
   |
   v
Application Pod
   |  Vault Agent sidecar injects secrets from HashiCorp Vault
   |  as environment variables or mounted files at startup
   v
App reads DB_PASSWORD, API_KEY, etc. from /vault/secrets/
```

### Why ClusterIP (Not LoadBalancer)?

Your applications use `ClusterIP` services. This means they are **not exposed to the internet**. Only the NGINX Ingress Controller (which runs inside the cluster) can reach them. This is the correct pattern:

```
Internet → Azure LB → NGINX → ClusterIP Service → Pod
                        ↑
               Only this component
               needs a public IP
```

If you gave each app a `LoadBalancer` service, you would need a separate Azure Load Balancer (and public IP) per app, which is wasteful and difficult to manage TLS for.

### Component Responsibilities

| Component | Where it lives | What it does |
|---|---|---|
| **Azure DNS Zone** | Azure (managed service) | Authoritative DNS for your domain; stores A/TXT/CNAME records |
| **ExternalDNS** | Kubernetes pod | Watches Ingress/Service resources; creates/deletes DNS records in Azure DNS automatically |
| **Azure Load Balancer** | Azure (managed service) | Exposes a public IP; forwards TCP traffic to Ingress Controller pods |
| **NGINX Ingress Controller** | Kubernetes pod | Terminates TLS; evaluates Ingress rules; proxies to backend Services |
| **cert-manager** | Kubernetes pod | Watches Certificate/Ingress resources; requests TLS certs from Let's Encrypt; renews automatically |
| **Let's Encrypt** | External (internet) | Free CA; issues DV certificates via ACME protocol |
| **ClusterIP Service** | Kubernetes | Internal DNS name for a group of pods; load balances inside the cluster |
| **HashiCorp Vault** | External or Kubernetes pod | Stores secrets; Vault Agent sidecar injects secrets into application pods |
| **Vault Agent Injector** | Kubernetes pod (webhook) | Mutating webhook that intercepts pod creation and adds a Vault Agent sidecar |

---

## 2. How a Request Flows End-to-End

 Here is what happens when a user visits `https://myapp.example.com/api/users`.

### Phase 1 — DNS Resolution

1. The user's browser queries their local DNS resolver for `myapp.example.com`
2. The resolver follows the delegation chain to Azure DNS (because you delegated `example.com` to Azure's nameservers)
3. Azure DNS returns the A record: `52.154.156.139`
4. This record was created automatically by **ExternalDNS** when the Ingress resource was applied to the cluster

### Phase 2 — TCP Connection to Azure Load Balancer

5. The browser opens a TCP connection to `52.154.156.139:443`
6. **Azure Load Balancer** receives the connection and forwards it (via its backend pool) to one of the NGINX Ingress Controller pods running on the cluster nodes

### Phase 3 — TLS Handshake at the Ingress Controller

7. NGINX performs the TLS handshake, presenting the certificate for `myapp.example.com`
8. This certificate is stored as a Kubernetes Secret — it was obtained and is automatically renewed by **cert-manager** from **Let's Encrypt**
9. The encrypted tunnel is now established between the browser and NGINX

### Phase 4 — HTTP Routing

10. NGINX decrypts the HTTP request and inspects the `Host` header (`myapp.example.com`) and the path (`/api/users`)
11. NGINX evaluates its Ingress rules and matches: Host=`myapp.example.com`, Path prefix=`/api`
12. NGINX forwards the (now plaintext) request to the ClusterIP service `api-service` on port 80

### Phase 5 — Pod Processing with Vault Secrets

13. The request reaches the application pod
14. At pod startup time, the **Vault Agent sidecar** (injected by the **Vault Agent Injector** webhook) authenticated to Vault and wrote secrets to `/vault/secrets/config`
15. The application reads its database password, API keys, etc. from those files and processes the request

### Phase 6 — Response

16. The response travels back through the same path: pod -> ClusterIP -> NGINX -> TLS encrypt -> Load Balancer -> internet -> browser

---

## 3. Azure Load Balancer

When you create a Kubernetes Service of type `LoadBalancer` in AKS, Azure automatically provisions an **Azure Load Balancer** (Standard SKU) and assigns it a IP. The NGINX Ingress Controller uses exactly this mechanism — its Helm chart creates a `LoadBalancer` Service, which triggers Azure to provision the external IP.

The Load Balancer operates at **Layer 4 (TCP/UDP)**. It does not inspect HTTP headers or perform TLS — it simply forwards TCP packets to the correct node. All HTTP-level intelligence happens inside NGINX.

If you want the ingress to be private only, you annotate the Service so AKS creates an **internal** load balancer instead of a public one. AKS also supports a health-probe path annotation, and `/healthz` is a common value for NGINX-based ingress controllers.

This load balancer operates at **Layer 4 (TCP/UDP)** — it forwards raw TCP connections without inspecting HTTP content. It does not understand host headers, URL paths, or TLS SNI.

This is why you still need an Ingress Controller — to handle the **Layer 7** concerns (HTTP routing, TLS termination, path matching).

```
Azure Load Balancer = Layer 4 (TCP port forwarding)
NGINX Ingress       = Layer 7 (HTTP routing, TLS)
```
### Why a Static IP

By default, AKS assigns a dynamic public IP to the Load Balancer. This is problematic because:
- DNS records would need to be updated every time the IP changes
- Firewall rules and allow-lists would break

A static IP solves this permanently.

### Provisioning a Static IP

The static IP **must** be created inside the **node resource group** — the resource group that AKS manages for you (usually `MC_<rg>_<cluster>_<region>`). If you create it in your own resource group, AKS cannot assign it to the Load Balancer.

Code removed 

### How the Load Balancer Backend Pool Works

When the NGINX Ingress Controller Helm chart creates a `LoadBalancer` Service with a specific IP, AKS:

1. Creates an Azure Load Balancer frontend IP configuration pointing to your static IP
2. Creates a backend pool containing the **virtual machine scale set (VMSS)** nodes that run Ingress Controller pods
3. Creates load balancing rules forwarding port 80 and 443 from the frontend IP to the node ports
4. Creates health probes against the node ports to detect pod failures

```
Public IP: 52.154.156.139
      |
      v
Load Balancer Frontend (52.154.156.139:443)
      |
      v  Load Balancing Rule (port 443 -> NodePort 32443)
      |
      v
VMSS Backend Pool (Node1:32443, Node2:32443, Node3:32443)
      |
      v
NGINX Pod (listening on 32443 via NodePort -> container port 443)
```

### `externalTrafficPolicy: Local` — Why It Matters

```yaml
# This setting is critical for preserving the original client IP
controller.service.externalTrafficPolicy=Local
```

Without this, the Load Balancer can forward traffic to any node, and the source IP is replaced with the node IP (SNAT). With `Local`, traffic is only forwarded to nodes that are actually running an Ingress Controller pod — preserving the real client IP in the `X-Forwarded-For` header.

---

## 4. NGINX Ingress Controller



An **Ingress resource** is just Kubernetes configuration that says, “for host X and path Y, send traffic to Service Z.” An **Ingress controller** is the actual software that watches those Ingress objects and enforces the routing.

This is the reverse proxy layer. It watches Kubernetes for `Ingress` objects and translates them into runtime routing configuration

The NGINX Ingress Controller is a Kubernetes controller that:
1. Watches all `Ingress` resources in the cluster
2. Dynamically generates an NGINX configuration (`nginx.conf`) from those resources
3. Reloads NGINX when Ingress resources change (zero-downtime reload)
4. Handles TLS termination using certificates stored as Kubernetes Secrets
5. Forwards decrypted traffic to backend ClusterIP Services

### Installing via Helm

Code removed

# Verify the controller pods are running
kubectl get pods -n ingress-basic

# Verify the LoadBalancer service has your static IP
kubectl get svc -n ingress-basic

```

### Understanding the Ingress Resource

An `Ingress` is a Kubernetes API object that defines HTTP routing rules. NGINX reads these and builds its routing table.

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: myapp-ingress
  namespace: production
  annotations:
    # Tell Kubernetes which Ingress Controller handles this resource
    kubernetes.io/ingress.class: nginx

    # Tell cert-manager which ClusterIssuer to use for TLS certificates
    cert-manager.io/cluster-issuer: letsencrypt-prod

    # Rewrite the path before forwarding to backend
    # e.g. /api/users becomes /users when it reaches the backend pod
    nginx.ingress.kubernetes.io/rewrite-target: /$2

    # Enable HTTPS redirect — any HTTP request gets 301 to HTTPS
    nginx.ingress.kubernetes.io/ssl-redirect: "true"

    # Set proxy timeouts for long-running requests
    nginx.ingress.kubernetes.io/proxy-read-timeout: "600"
    nginx.ingress.kubernetes.io/proxy-send-timeout: "600"

    # Limit request body size (default 1m — increase for file uploads)
    nginx.ingress.kubernetes.io/proxy-body-size: "50m"

    # Rate limiting — max 100 requests per minute per IP
    nginx.ingress.kubernetes.io/limit-rps: "100"

    # CORS headers
    nginx.ingress.kubernetes.io/enable-cors: "true"
    nginx.ingress.kubernetes.io/cors-allow-origin: "https://myapp.example.com"

spec:
  # TLS configuration — cert-manager will create/renew this certificate
  tls:
  - hosts:
    - myapp.example.com
    - api.example.com
    # Name of the Kubernetes Secret where the certificate will be stored
    secretName: myapp-tls-secret

  rules:
  # Rule 1 — main application on its own subdomain
  - host: myapp.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: frontend-clusterip-service
            port:
              number: 80

  # Rule 2 — API backend on a separate subdomain
  - host: api.example.com
    http:
      paths:
      - path: /users(/|$)(.*)
        pathType: ImplementationSpecific
        backend:
          service:
            name: users-api-clusterip-service
            port:
              number: 8080
      - path: /orders(/|$)(.*)
        pathType: ImplementationSpecific
        backend:
          service:
            name: orders-api-clusterip-service
            port:
              number: 8080
```

### Path Types Explained

| `pathType` | Behaviour | Example |
|---|---|---|
| `Prefix` | Matches any path beginning with the given prefix | `/api` matches `/api`, `/api/users`, `/api/v2/data` |
| `Exact` | Only matches the exact path | `/api` only matches `/api` — not `/api/users` |
| `ImplementationSpecific` | Delegates to the controller — NGINX uses regex | Enables capture groups for rewrite rules |

### Default Backend

If no Ingress rule matches the request (wrong hostname or unrecognised path), NGINX returns a 404. You can customise this by deploying a **default backend** service:

```yaml
spec:
  defaultBackend:
    service:
      name: custom-404-service
      port:
        number: 80
```

### How NGINX Reloads Without Dropping Connections

When an Ingress resource is created, updated, or deleted, the Ingress Controller:
1. Generates a new `nginx.conf`
2. Runs `nginx -t` to validate the configuration
3. Sends `SIGHUP` to the NGINX master process
4. NGINX master forks new worker processes with the new config
5. Old worker processes finish handling existing connections, then exit

This is entirely zero-downtime — no connections are dropped during a config reload.

---

## 5. cert-manager and Let's Encrypt

### What cert-manager Does

cert-manager is a Kubernetes controller that automates the full lifecycle of TLS certificates:

cert-manager watches annotated `Ingress` resources and can create the corresponding `Certificate` resource automatically.

**The three moving parts:**

**1. The cert-manager installation** — runs as pods in your cluster, watching for `Certificate` and `Ingress` resources.

**2. A `ClusterIssuer` (or `Issuer`)** — tells cert-manager *where* to get certificates from and use This could be your internal PKI (e.g. a Vault CA, an ADCS CA), or Let's Encrypt for public-facing services. You define this once and all your apps share it.

**3. A `Certificate` object (or an Ingress annotation)** — tells cert-manager *what* certificate you need (which hostname, which issuer). cert-manager then does the work: contacts your CA, gets the cert signed, and stores it as a Kubernetes `Secret`. It also watches expiry and auto-renews before it lapses.

- **Requests** certificates from a Certificate Authority (CA) — in our case, Let's Encrypt
- **Proves domain ownership** using the ACME protocol (HTTP-01 or DNS-01 challenges)
- **Stores** issued certificates as Kubernetes Secrets
- **Monitors** expiry and automatically renews certificates 30 days before they expire
- **Distributes** certificates to the Ingress Controller via the Secret reference in the Ingress spec

**Two ways to trigger cert-manager from an Ingress:**

- **Explicit `Certificate` object** — you write the `Certificate` YAML yourself; gives you full control over SANs, duration, renewal thresholds.
- **Ingress annotation** (`cert-manager.io/cluster-issuer`) — cert-manager detects the annotation on your `Ingress` and auto-creates the `Certificate` for you. Less to write, slightly less control.

For internal PKI (Vault or similar), the explicit `Certificate` approach is cleaner because you can control the issuer reference precisely.

---


### Installing cert-manager

Code removed




### ClusterIssuer — Staging vs Production

Always test with the **staging** issuer first. Let's Encrypt's production endpoint has strict rate limits (5 failed validations per domain per hour). The staging issuer is nearly identical but issues untrusted certificates — perfect for testing your setup without risking a rate limit lockout.

### Option A — Internal CA via Vault (recommended)

```yaml
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: internal-ca-issuer
spec:
  vault:
    server: https://vault.internal.example.com
    path: pki/sign/my-role          # your Vault PKI role
    auth:
      kubernetes:
        role: cert-manager
        mountPath: /v1/auth/kubernetes
        secretRef:
          name: vault-token
          key: token
```

```bash
# Apply both issuers
kubectl apply -f cluster-issuer-staging.yaml
kubectl apply -f cluster-issuer-prod.yaml

# Verify the issuers are ready
kubectl get clusterissuer
# NAME                  READY   AGE
# letsencrypt-staging   True    10s
# letsencrypt-prod      True    10s

# If READY is False, describe to see the error
kubectl describe clusterissuer letsencrypt-prod
```

### How cert-manager Integrates with Ingress

When you add the annotation `cert-manager.io/cluster-issuer: letsencrypt-prod` to an Ingress resource, cert-manager's **ingress-shim** component detects it and automatically creates a `Certificate` resource. You never need to create `Certificate` resources manually for Ingress-driven TLS.

The lifecycle is:

```
Ingress (with cert-manager annotation)
   |
   v  cert-manager ingress-shim detects annotation
Certificate resource (auto-created by cert-manager)
   |
   v  cert-manager controller watches Certificate resources
CertificateRequest resource (created per renewal cycle)
   |
   v
Order resource (created by cert-manager's ACME issuer)
   |
   v
Challenge resource (created to prove domain ownership)
   |  cert-manager creates a temporary Ingress rule
   |  Let's Encrypt calls /.well-known/acme-challenge/<token>
   |  cert-manager's solver pod responds with the token
   v
Certificate issued -> stored in Kubernetes Secret (e.g. myapp-tls-secret)
   |
   v
NGINX Ingress Controller reads the Secret and serves TLS
```

### Inspecting Certificate Status

```bash
# List all certificates across all namespaces
kubectl get certificate --all-namespaces
# NAMESPACE    NAME               READY   SECRET             AGE
# production   myapp-tls-secret   True    myapp-tls-secret   2d

# See the full lifecycle of a certificate
kubectl describe certificate myapp-tls-secret -n production

# See the Order and Challenge resources for troubleshooting
kubectl get order -n production
kubectl get challenge -n production

# If a challenge is stuck, describe it
kubectl describe challenge <challenge-name> -n production

# Check cert-manager controller logs
kubectl logs -n cert-manager \
  $(kubectl get pods -n cert-manager -l app=cert-manager -o jsonpath='{.items[0].metadata.name}')
```

### Automatic Renewal

cert-manager checks certificate expiry every 10 minutes by default and begins renewal when a certificate is within **30 days of expiry**. Let's Encrypt certificates are valid for 90 days, giving a comfortable 60-day window before renewal begins.

```yaml
apiVersion: cert-manager.io/v1
kind: Certificate
metadata:
  name: myapp-tls-cert
  namespace: default          # must match the namespace of your Ingress
spec:
  secretName: myapp-tls-cert  # cert-manager creates this Secret; Ingress references it
  duration: 8760h             # 1 year
  renewBefore: 720h           # auto-renew 30 days before expiry
  issuerRef:
    name: internal-ca-issuer  # the ClusterIssuer you defined in step 0b
    kind: ClusterIssuer
  dnsNames:
    - myapp.example.internal
```

What cert-manager does when you apply this:

1. Detects the `Certificate` object
2. Contacts `internal-ca-issuer` to request a signed cert for `myapp.example.internal`
3. Stores the result as a `Secret` named `myapp-tls-cert` containing `tls.crt` and `tls.key`
4. Watches the cert's expiry and re-runs the process before `renewBefore` is reached

---

## 6. ExternalDNS and Azure DNS

### What ExternalDNS Does

ExternalDNS is a Kubernetes controller that bridges the gap between Kubernetes and your DNS provider. Without it, every time you deploy a new application with an Ingress resource, you would need to manually log into Azure DNS and create an A record. ExternalDNS eliminates this entirely.

It works by:
1. Watching Ingress and Service resources for `host` fields and hostnames
2. Comparing the desired DNS state (from Ingress resources) with the actual state (in Azure DNS)
3. Creating, updating, or deleting DNS records to reconcile the difference
4. Adding a `TXT` ownership record alongside each A record so it can track which records it manages

### DNS Zone Setup

Before deploying ExternalDNS, you need an Azure DNS Zone delegated from your domain registrar.

```bash
# Create a resource group for DNS zones
az group create --name dns-zones --location eastus

# Create the DNS zone
az network dns zone create \
  --resource-group dns-zones \
  --name example.com

# Get the nameservers Azure assigned to your zone
az network dns zone show \
  --resource-group dns-zones \
  --name example.com \
  --query nameServers \
  --output table

# Output example:
# ns1-04.azure-dns.com.
# ns2-04.azure-dns.net.
# ns3-04.azure-dns.org.
# ns4-04.azure-dns.info.
```

Take these four nameservers to your domain registrar and replace the existing NS records. Once propagated (up to 48 hours, usually minutes), Azure DNS is authoritative for your domain.

```bash
# Verify delegation has propagated (query Google's public DNS)
nslookup -type=NS example.com 8.8.8.8
```

### MSI Authentication Setup

ExternalDNS needs permission to modify your DNS Zone. Using MSI avoids storing credentials in Kubernetes Secrets.

```bash
# Step 1 — Create a User-Assigned Managed Identity
az identity create \
  --name aks-externaldns-identity \
  --resource-group aks-rg1

# Step 2 — Get the identity's Client ID and Principal ID
CLIENT_ID=$(az identity show \
  --name aks-externaldns-identity \
  --resource-group aks-rg1 \
  --query clientId --output tsv)

PRINCIPAL_ID=$(az identity show \
  --name aks-externaldns-identity \
  --resource-group aks-rg1 \
  --query principalId --output tsv)

# Step 3 — Get the DNS Zone resource ID
DNS_ZONE_ID=$(az network dns zone show \
  --name example.com \
  --resource-group dns-zones \
  --query id --output tsv)

# Step 4 — Assign DNS Zone Contributor role to the identity
# "DNS Zone Contributor" is more restrictive than "Contributor" — prefer it
az role assignment create \
  --assignee $PRINCIPAL_ID \
  --role "DNS Zone Contributor" \
  --scope $DNS_ZONE_ID

# Step 5 — Assign the identity to the AKS node VMSS
NODE_RG=$(az aks show \
  --resource-group aks-rg1 \
  --name aksdemo1 \
  --query nodeResourceGroup --output tsv)

VMSS_NAME=$(az vmss list \
  --resource-group $NODE_RG \
  --query "[0].name" --output tsv)

IDENTITY_ID=$(az identity show \
  --name aks-externaldns-identity \
  --resource-group aks-rg1 \
  --query id --output tsv)

az vmss identity assign \
  --resource-group $NODE_RG \
  --name $VMSS_NAME \
  --identities $IDENTITY_ID
```

### `azure.json` Configuration File

```bash
# Get your tenant and subscription IDs
TENANT_ID=$(az account show --query tenantId --output tsv)
SUBSCRIPTION_ID=$(az account show --query id --output tsv)

cat > azure.json << EOF
{
  "tenantId": "${TENANT_ID}",
  "subscriptionId": "${SUBSCRIPTION_ID}",
  "resourceGroup": "dns-zones",
  "useManagedIdentityExtension": true,
  "userAssignedIdentityID": "${CLIENT_ID}"
}
EOF

# Create the Kubernetes Secret from this file
kubectl create secret generic azure-dns-config \
  --from-file=azure.json \
  --namespace kube-system
```

### ExternalDNS Deployment Manifest

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: external-dns
  namespace: kube-system

---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: external-dns
rules:
- apiGroups: [""]
  resources: ["services", "endpoints", "pods", "nodes"]
  verbs: ["get", "watch", "list"]
- apiGroups: ["extensions", "networking.k8s.io"]
  resources: ["ingresses"]
  verbs: ["get", "watch", "list"]

---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: external-dns-viewer
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: external-dns
subjects:
- kind: ServiceAccount
  name: external-dns
  namespace: kube-system

---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: external-dns
  namespace: kube-system
spec:
  strategy:
    # Recreate ensures only one instance runs — prevents split-brain DNS updates
    type: Recreate
  selector:
    matchLabels:
      app: external-dns
  template:
    metadata:
      labels:
        app: external-dns
    spec:
      serviceAccountName: external-dns
      containers:
      - name: external-dns
        image: registry.k8s.io/external-dns/external-dns:v0.14.0
        args:
        - --source=ingress              # Watch Ingress resources
        - --source=service              # Also watch LoadBalancer Services
        - --domain-filter=example.com  # Only manage records for this domain
        - --provider=azure             # Use Azure DNS
        - --azure-resource-group=dns-zones  # Resource group with DNS zones
        - --txt-owner-id=aks-cluster-1      # Unique ID to track owned records
        - --log-level=info
        volumeMounts:
        - name: azure-config-file
          mountPath: /etc/kubernetes
          readOnly: true
      volumes:
      - name: azure-config-file
        secret:
          secretName: azure-dns-config
```

### What `txt-owner-id` Does

When ExternalDNS creates an A record for `myapp.example.com`, it also creates a companion TXT record:

```
myapp.example.com       A    52.154.156.139
myapp.example.com  TXT  "heritage=external-dns,external-dns/owner=aks-cluster-1,..."
```

The TXT record means: "ExternalDNS instance `aks-cluster-1` owns this A record." This prevents multiple ExternalDNS instances (e.g. dev and prod clusters) from deleting each other's records. Each cluster should have a unique `txt-owner-id`.

### Verifying ExternalDNS

```bash
# Watch ExternalDNS logs in real time
kubectl logs -f \
  $(kubectl get pods -n kube-system -l app=external-dns -o jsonpath='{.items[0].metadata.name}') \
  -n kube-system

# After deploying an Ingress with a hostname, you should see:
# time="..." level=info msg="Updating A record named 'myapp' to '52.154.156.139' for Azure DNS zone 'example.com'."

# Verify the record was created in Azure DNS
az network dns record-set a list \
  --resource-group dns-zones \
  --zone-name example.com \
  --output table

# Test DNS resolution
nslookup myapp.example.com 8.8.8.8
```

---

## 7. HashiCorp Vault — Secret Injection

### The Problem Vault Solves

Without Vault, application secrets (database passwords, API keys, TLS certificates for mTLS) are typically stored as Kubernetes Secrets encoded in base64. This is **not encrypted at rest** by default, can be read by anyone with cluster access, and is difficult to rotate centrally.

HashiCorp Vault provides:
- Encrypted secret storage
- Dynamic secrets (Vault generates a database credential on demand, with a TTL)
- Fine-grained access control (who can read which secret)
- Automatic secret rotation
- Full audit log of every secret access

### Vault Architecture in AKS

```
Application Pod
+-- App Container
|   +-- reads /vault/secrets/config (mounted file)
|       contains: DB_PASSWORD=abc123, API_KEY=xyz
|
+-- Vault Agent Sidecar (injected by webhook)
    +-- Init mode: fetches secrets BEFORE app starts
    +-- Sidecar mode: keeps running, refreshes dynamic secrets

         | Kubernetes Auth (ServiceAccount JWT)
         v
    HashiCorp Vault
    +-- KV Secret Engine:       kv/data/production/myapp
    +-- Database Secret Engine: generates ephemeral DB credentials
    +-- PKI Secret Engine:      issues internal TLS certificates
```

### Installing Vault on AKS

```bash
# Add the HashiCorp Helm repository
helm repo add hashicorp https://helm.releases.hashicorp.com
helm repo update

# Install Vault in HA mode with integrated Raft storage
helm install vault hashicorp/vault \
  --namespace vault \
  --create-namespace \
  --set server.ha.enabled=true \
  --set server.ha.raft.enabled=true \
  --set server.ha.replicas=3 \
  --set injector.enabled=true \
  --set ui.enabled=true \
  --set ui.serviceType=ClusterIP

# Wait for pods to appear
kubectl get pods -n vault
# NAME                                  READY   STATUS
# vault-0                               0/1     Running   <- not ready until initialised
# vault-1                               0/1     Running
# vault-2                               0/1     Running
# vault-agent-injector-xxxxxxxxxxxx     1/1     Running   <- the mutating webhook
```

### Initialising and Unsealing Vault

```bash
# Initialise Vault — generates unseal keys and root token
kubectl exec vault-0 -n vault -- vault operator init \
  -key-shares=5 \
  -key-threshold=3 \
  -format=json > vault-init.json

# IMPORTANT: Store vault-init.json securely — these are the master keys
# In production, use Azure Key Vault to auto-unseal (see below)

# Unseal using 3 of the 5 keys
kubectl exec vault-0 -n vault -- vault operator unseal \
  $(jq -r '.unseal_keys_b64[0]' vault-init.json)

kubectl exec vault-0 -n vault -- vault operator unseal \
  $(jq -r '.unseal_keys_b64[1]' vault-init.json)

kubectl exec vault-0 -n vault -- vault operator unseal \
  $(jq -r '.unseal_keys_b64[2]' vault-init.json)

# Join vault-1 and vault-2 to the Raft cluster
kubectl exec vault-1 -n vault -- vault operator raft join \
  http://vault-0.vault-internal:8200

kubectl exec vault-2 -n vault -- vault operator raft join \
  http://vault-0.vault-internal:8200

# Unseal vault-1 and vault-2 the same way (three keys each)
```

### Auto-Unseal with Azure Key Vault (Recommended for Production)

Instead of manually unsealing after every restart, configure Vault to use Azure Key Vault for auto-unseal. The AKS cluster's managed identity needs `Key Vault Crypto Officer` on the Azure Key Vault.

```yaml
# vault-values.yaml — pass to helm install with -f vault-values.yaml
server:
  ha:
    enabled: true
    replicas: 3
    raft:
      enabled: true
      config: |
        ui = true
        listener "tcp" {
          tls_disable = 1
          address     = "[::]:8200"
          cluster_address = "[::]:8201"
        }
        storage "raft" {
          path = "/vault/data"
        }
        # Auto-unseal using Azure Key Vault
        seal "azurekeyvault" {
          tenant_id      = "YOUR_TENANT_ID"
          vault_name     = "your-akv-name"
          key_name       = "vault-unseal-key"
        }
        service_registration "kubernetes" {}
```

### Configuring Kubernetes Authentication

Vault needs to verify that pods requesting secrets are actually running in your AKS cluster. This is done via the **Kubernetes auth method**, which uses the pod's ServiceAccount JWT token as proof of identity.

```bash
# Log into Vault with root token
ROOT_TOKEN=$(jq -r '.root_token' vault-init.json)
kubectl exec vault-0 -n vault -- vault login $ROOT_TOKEN

# Enable the Kubernetes auth method
kubectl exec vault-0 -n vault -- vault auth enable kubernetes

# Configure Kubernetes auth
kubectl exec vault-0 -n vault -- vault write auth/kubernetes/config \
  kubernetes_host="https://$(kubectl get svc kubernetes -o jsonpath='{.spec.clusterIP}'):443" \
  kubernetes_ca_cert=@/var/run/secrets/kubernetes.io/serviceaccount/ca.crt \
  token_reviewer_jwt=@/var/run/secrets/kubernetes.io/serviceaccount/token

# Enable the KV v2 secrets engine
kubectl exec vault-0 -n vault -- vault secrets enable -path=kv kv-v2

# Write application secrets
kubectl exec vault-0 -n vault -- vault kv put kv/production/myapp \
  DB_PASSWORD="super-secret-password" \
  API_KEY="abc123xyz" \
  REDIS_PASSWORD="redis-secret"

# Create a Vault policy — defines what the app is allowed to read
kubectl exec vault-0 -n vault -- vault policy write myapp-policy - << 'EOF'
path "kv/data/production/myapp" {
  capabilities = ["read"]
}
EOF

# Create a Kubernetes auth role
# Binds: ServiceAccount "myapp-sa" in namespace "production" -> policy "myapp-policy"
kubectl exec vault-0 -n vault -- vault write auth/kubernetes/role/myapp-role \
  bound_service_account_names=myapp-sa \
  bound_service_account_namespaces=production \
  policies=myapp-policy \
  ttl=1h
```

### The Vault Agent Injector

The **Vault Agent Injector** is a Kubernetes **mutating admission webhook**. When a pod is created with specific annotations, the webhook intercepts the pod creation request and injects a Vault Agent sidecar container automatically — before the pod is scheduled.

```
kubectl apply pod manifest
         |
         v
Kubernetes API Server
         | calls MutatingWebhookConfiguration
         v
Vault Agent Injector
         | detects vault.hashicorp.com/agent-inject: "true"
         | mutates the pod spec — adds init container + sidecar
         v
Modified pod spec sent back to API Server
         |
         v
Pod scheduled on node
         |
         v  startup sequence
+-----------------------------------------------------------+
|  1. vault-agent-init (init container)                    |
|     - Authenticates to Vault using the pod's SA token    |
|     - Fetches secrets from kv/production/myapp           |
|     - Renders them to /vault/secrets/config              |
|     - Exits (init container completes successfully)      |
|                                                          |
|  2. App container starts                                 |
|     - /vault/secrets/config is already populated        |
|     - App sources this file to get env vars              |
|                                                          |
|  3. vault-agent sidecar (runs alongside app)             |
|     - Keeps the Vault token renewed                      |
|     - Re-fetches dynamic secrets before they expire      |
+-----------------------------------------------------------+
```

### Application Deployment with Vault Annotations

```yaml
# file: myapp-deployment.yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: myapp-sa
  namespace: production

---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp
  namespace: production
spec:
  replicas: 2
  selector:
    matchLabels:
      app: myapp
  template:
    metadata:
      labels:
        app: myapp
      annotations:
        # Enable secret injection — this triggers the mutating webhook
        vault.hashicorp.com/agent-inject: "true"

        # Which Vault role to authenticate as
        vault.hashicorp.com/role: "myapp-role"

        # Inject secrets from this path into /vault/secrets/config
        vault.hashicorp.com/agent-inject-secret-config: "kv/data/production/myapp"

        # Template the secrets into shell export format
        vault.hashicorp.com/agent-inject-template-config: |
          {{- with secret "kv/data/production/myapp" -}}
          export DB_PASSWORD="{{ .Data.data.DB_PASSWORD }}"
          export API_KEY="{{ .Data.data.API_KEY }}"
          export REDIS_PASSWORD="{{ .Data.data.REDIS_PASSWORD }}"
          {{- end }}

        # Vault server address (internal cluster DNS)
        vault.hashicorp.com/address: "http://vault.vault.svc.cluster.local:8200"

        # Set to "true" to disable the sidecar (inject once at startup only)
        # Use "false" if you have dynamic secrets that need refreshing
        vault.hashicorp.com/agent-pre-populate-only: "false"

    spec:
      serviceAccountName: myapp-sa
      containers:
      - name: myapp
        image: your-registry/myapp:1.0.0
        command: ["/bin/sh", "-c"]
        args:
        - |
          source /vault/secrets/config
          exec ./myapp
        ports:
        - containerPort: 8080
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        readinessProbe:
          httpGet:
            path: /healthz
            port: 8080
          initialDelaySeconds: 10
          periodSeconds: 5
```

### Using Vault for Database Dynamic Secrets

Instead of storing a static database password, Vault can generate a **temporary credential** valid for a short TTL. When the TTL expires, Vault automatically revokes the credential — even if the pod was deleted abruptly.

```bash
# Enable the database secrets engine
kubectl exec vault-0 -n vault -- vault secrets enable database

# Configure Vault to connect to your PostgreSQL database
kubectl exec vault-0 -n vault -- vault write database/config/mypostgres \
  plugin_name=postgresql-database-plugin \
  allowed_roles="myapp-db-role" \
  connection_url="postgresql://{{username}}:{{password}}@postgres.production.svc:5432/mydb?sslmode=disable" \
  username="vault-admin" \
  password="admin-password"

# Create a Vault role with SQL to create ephemeral users
kubectl exec vault-0 -n vault -- vault write database/roles/myapp-db-role \
  db_name=mypostgres \
  creation_statements="CREATE ROLE \"{{name}}\" WITH LOGIN PASSWORD '{{password}}' \
    VALID UNTIL '{{expiration}}'; GRANT SELECT ON ALL TABLES IN SCHEMA public TO \"{{name}}\";" \
  default_ttl="1h" \
  max_ttl="24h"

# Update the Vault policy to also allow database creds
kubectl exec vault-0 -n vault -- vault policy write myapp-policy - << 'EOF'
path "kv/data/production/myapp" {
  capabilities = ["read"]
}
path "database/creds/myapp-db-role" {
  capabilities = ["read"]
}
EOF
```

With dynamic secrets, each pod gets its own unique database credential. When the pod terminates or the TTL expires, the credential is automatically revoked at the database level.

---

## 8. Putting It All Together — Full Deployment

This section shows the complete deployment sequence and all manifests needed to bring up a production-grade application in AKS.

### Deployment Order

The order matters — each layer depends on the one below it:

```
1.  Azure DNS Zone                    (az CLI)
2.  Managed Identity + Role Assignment (az CLI)
3.  AKS Cluster                       (az CLI / Terraform)
4.  Static Public IP                  (az CLI)
5.  NGINX Ingress Controller          (Helm)
6.  cert-manager                      (Helm)
7.  ClusterIssuers                    (kubectl apply)
8.  Vault                             (Helm + operator init)
9.  ExternalDNS                       (kubectl apply)
10. Application namespace + RBAC      (kubectl apply)
11. Application Deployment + Service + Ingress (kubectl apply)
```

### Step 1 — Infrastructure (Azure CLI)

```bash
#!/bin/bash
set -euo pipefail

RG="aks-rg1"
DNS_RG="dns-zones"
CLUSTER="aksdemo1"
DOMAIN="example.com"
LOCATION="eastus"

# Resource groups
az group create --name $RG --location $LOCATION
az group create --name $DNS_RG --location $LOCATION

# AKS cluster with managed identity and Azure CNI
az aks create \
  --resource-group $RG \
  --name $CLUSTER \
  --node-count 3 \
  --node-vm-size Standard_D4s_v3 \
  --enable-managed-identity \
  --network-plugin azure \
  --generate-ssh-keys

# Get kubeconfig
az aks get-credentials --resource-group $RG --name $CLUSTER

# DNS zone
az network dns zone create --resource-group $DNS_RG --name $DOMAIN

# Static IP in node resource group
NODE_RG=$(az aks show --resource-group $RG --name $CLUSTER \
  --query nodeResourceGroup --output tsv)

STATIC_IP=$(az network public-ip create \
  --resource-group $NODE_RG \
  --name myAKSPublicIPForIngress \
  --sku Standard \
  --allocation-method static \
  --query publicIp.ipAddress --output tsv)

echo "Static IP: $STATIC_IP"
echo "Update your domain registrar NS records to:"
az network dns zone show --resource-group $DNS_RG --name $DOMAIN \
  --query nameServers --output table
```

### Step 2 — Install Core Controllers (Helm)

```bash
# NGINX Ingress Controller
helm install ingress-nginx ingress-nginx/ingress-nginx \
  --namespace ingress-basic \
  --create-namespace \
  --set controller.replicaCount=2 \
  --set controller.service.loadBalancerIP="$STATIC_IP" \
  --set controller.service.externalTrafficPolicy=Local \
  --set controller.nodeSelector."kubernetes\.io/os"=linux \
  --set defaultBackend.nodeSelector."kubernetes\.io/os"=linux

# cert-manager
helm install cert-manager jetstack/cert-manager \
  --namespace cert-manager \
  --create-namespace \
  --version v1.13.0 \
  --set installCRDs=true

# Vault
helm install vault hashicorp/vault \
  --namespace vault \
  --create-namespace \
  --set injector.enabled=true \
  --set server.ha.enabled=true \
  --set server.ha.raft.enabled=true \
  --set server.ha.replicas=3
```

### Step 3 — cert-manager ClusterIssuers

```yaml
# file: cluster-issuers.yaml
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-staging
spec:
  acme:
    server: https://acme-staging-v02.api.letsencrypt.org/directory
    email: ops@example.com
    privateKeySecretRef:
      name: letsencrypt-staging-key
    solvers:
    - http01:
        ingress:
          class: nginx

---
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: ops@example.com
    privateKeySecretRef:
      name: letsencrypt-prod-key
    solvers:
    - http01:
        ingress:
          class: nginx
```

### Step 4 — ExternalDNS

```yaml
# file: external-dns.yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: external-dns
  namespace: kube-system
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: external-dns
rules:
- apiGroups: [""]
  resources: ["services", "endpoints", "pods", "nodes"]
  verbs: ["get", "watch", "list"]
- apiGroups: ["extensions", "networking.k8s.io"]
  resources: ["ingresses"]
  verbs: ["get", "watch", "list"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: external-dns-viewer
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: external-dns
subjects:
- kind: ServiceAccount
  name: external-dns
  namespace: kube-system
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: external-dns
  namespace: kube-system
spec:
  strategy:
    type: Recreate
  selector:
    matchLabels:
      app: external-dns
  template:
    metadata:
      labels:
        app: external-dns
    spec:
      serviceAccountName: external-dns
      containers:
      - name: external-dns
        image: registry.k8s.io/external-dns/external-dns:v0.14.0
        args:
        - --source=ingress
        - --source=service
        - --domain-filter=example.com
        - --provider=azure
        - --azure-resource-group=dns-zones
        - --txt-owner-id=aksdemo1
        volumeMounts:
        - name: azure-config-file
          mountPath: /etc/kubernetes
          readOnly: true
      volumes:
      - name: azure-config-file
        secret:
          secretName: azure-dns-config
```

### Step 5 — Application Namespace and Vault Configuration

```yaml
# file: production-ns.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: production
---
apiVersion: v1
kind: ServiceAccount
metadata:
  name: myapp-sa
  namespace: production
```

```bash
# Configure Vault for the application (after Vault is initialised and unsealed)
export VAULT_ADDR='http://localhost:8200'
kubectl port-forward vault-0 8200:8200 -n vault &

vault login $(jq -r '.root_token' vault-init.json)

vault auth enable kubernetes
vault write auth/kubernetes/config \
  kubernetes_host="https://$(kubectl get svc kubernetes -o jsonpath='{.spec.clusterIP}'):443"

vault secrets enable -path=kv kv-v2
vault kv put kv/production/myapp \
  DB_PASSWORD="$(openssl rand -base64 32)" \
  API_KEY="$(openssl rand -hex 32)"

vault policy write myapp-policy - << 'EOF'
path "kv/data/production/myapp" {
  capabilities = ["read"]
}
EOF

vault write auth/kubernetes/role/myapp-role \
  bound_service_account_names=myapp-sa \
  bound_service_account_namespaces=production \
  policies=myapp-policy \
  ttl=1h
```

### Step 6 — Application Manifests (Deployment + Service + Ingress)

```yaml
# file: myapp-all.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp
  namespace: production
spec:
  replicas: 2
  selector:
    matchLabels:
      app: myapp
  template:
    metadata:
      labels:
        app: myapp
      annotations:
        vault.hashicorp.com/agent-inject: "true"
        vault.hashicorp.com/role: "myapp-role"
        vault.hashicorp.com/agent-inject-secret-config: "kv/data/production/myapp"
        vault.hashicorp.com/agent-inject-template-config: |
          {{- with secret "kv/data/production/myapp" -}}
          export DB_PASSWORD="{{ .Data.data.DB_PASSWORD }}"
          export API_KEY="{{ .Data.data.API_KEY }}"
          {{- end }}
        vault.hashicorp.com/address: "http://vault.vault.svc.cluster.local:8200"
    spec:
      serviceAccountName: myapp-sa
      containers:
      - name: myapp
        image: your-registry/myapp:1.0.0
        command: ["/bin/sh", "-c"]
        args: ["source /vault/secrets/config && exec ./myapp"]
        ports:
        - containerPort: 8080
        readinessProbe:
          httpGet:
            path: /healthz
            port: 8080
          initialDelaySeconds: 10
          periodSeconds: 5
        livenessProbe:
          httpGet:
            path: /healthz
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10

---
apiVersion: v1
kind: Service
metadata:
  name: myapp-clusterip-service
  namespace: production
spec:
  type: ClusterIP
  selector:
    app: myapp
  ports:
  - port: 80
    targetPort: 8080

---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: myapp-ingress
  namespace: production
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/proxy-body-size: "10m"
spec:
  tls:
  - hosts:
    - myapp.example.com
    secretName: myapp-tls-secret
  rules:
  - host: myapp.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: myapp-clusterip-service
            port:
              number: 80
```

### Step 7 — Apply and Verify Everything

```bash
# Apply in order
kubectl apply -f cluster-issuers.yaml
kubectl apply -f external-dns.yaml
kubectl apply -f production-ns.yaml
kubectl apply -f myapp-all.yaml

# --- VERIFICATION CHECKLIST ---

# 1. Ingress Controller running with correct external IP
kubectl get svc -n ingress-basic
# EXTERNAL-IP should be your static IP

# 2. cert-manager pods running
kubectl get pods -n cert-manager

# 3. ClusterIssuers ready
kubectl get clusterissuer

# 4. ExternalDNS running
kubectl get pods -n kube-system -l app=external-dns

# 5. Application pods running — 3 containers each (vault-agent-init, vault-agent, myapp)
kubectl get pods -n production

# 6. Certificate issued
kubectl get certificate -n production
# READY should be True

# 7. DNS record created in Azure DNS
az network dns record-set a list -g dns-zones -z example.com --output table

# 8. Ingress has an address
kubectl get ingress -n production

# 9. End-to-end HTTPS test
curl -v https://myapp.example.com/healthz
```

---

## 9. Troubleshooting Reference

### Certificate Not Becoming Ready

```bash
# 1. Describe the certificate to see events and conditions
kubectl describe certificate myapp-tls-secret -n production

# 2. Check if an Order was created (ACME certificate request)
kubectl get order -n production
kubectl describe order <order-name> -n production

# 3. Check if a Challenge was created (domain ownership proof)
kubectl get challenge -n production
kubectl describe challenge <challenge-name> -n production

# Common causes and fixes:
#
# "DNS record not yet propagated"
#   -> ExternalDNS hasn't created the A record yet, or DNS hasn't propagated
#   -> Wait 2-3 minutes and check: nslookup myapp.example.com 8.8.8.8
#
# "too many certificates already issued"
#   -> Hit Let's Encrypt rate limit — switch to letsencrypt-staging temporarily
#
# "ClusterIssuer not found"
#   -> kubectl apply -f cluster-issuers.yaml was not run
#
# Force a re-request by deleting the TLS Secret
kubectl delete secret myapp-tls-secret -n production
# cert-manager will automatically request a new certificate
```

### ExternalDNS Not Creating Records

```bash
# Watch ExternalDNS logs
kubectl logs -f -n kube-system \
  $(kubectl get pods -n kube-system -l app=external-dns \
    -o jsonpath='{.items[0].metadata.name}')

# Common causes and fixes:
#
# "error getting token" or "401 Unauthorized"
#   -> MSI not assigned to VMSS
#   -> Re-run: az vmss identity assign ...
#
# "403 Forbidden"
#   -> DNS Zone Contributor role not assigned to the MSI
#   -> Re-run: az role assignment create ...
#
# "azure: resource group 'dns-zones' not found"
#   -> Wrong resourceGroup in azure.json — check the spelling
#
# Records created but not resolving
#   -> Domain delegation not complete — check NS records at registrar
#   -> nslookup -type=NS example.com 8.8.8.8 should return Azure nameservers
```

### Vault Agent Not Injecting Secrets

```bash
# Check if the injector webhook is registered
kubectl get mutatingwebhookconfiguration | grep vault

# Check pod events — look for "vault-agent-init" init container
kubectl describe pod <pod-name> -n production

# Check Vault Agent init container logs
kubectl logs <pod-name> -n production -c vault-agent-init

# Check Vault Agent sidecar logs
kubectl logs <pod-name> -n production -c vault-agent

# Check the injector itself for errors
kubectl logs -n vault \
  $(kubectl get pods -n vault -l app.kubernetes.io/name=vault-agent-injector \
    -o jsonpath='{.items[0].metadata.name}')

# Common causes and fixes:
#
# "error authenticating: service account not found in role"
#   -> ServiceAccount name or namespace doesn't match vault write auth/kubernetes/role/...
#   -> Verify: vault read auth/kubernetes/role/myapp-role
#
# "no handler for route"
#   -> Vault is sealed — unseal it
#
# "permission denied" when reading the secret path
#   -> The Vault policy doesn't include that path
#   -> vault policy read myapp-policy
#
# Annotations present but no sidecar injected
#   -> Check the namespace is not excluded from injection
#   -> Verify vault.hashicorp.com/agent-inject: "true" is on the pod spec (not Deployment metadata)
```

### NGINX Not Routing Traffic

```bash
# Check Ingress Controller logs
kubectl logs -n ingress-basic \
  $(kubectl get pods -n ingress-basic -l app.kubernetes.io/name=ingress-nginx \
    -o jsonpath='{.items[0].metadata.name}') | tail -50

# Check the Ingress resource has an address
kubectl get ingress -n production
# ADDRESS should match your static IP

# Check that backend endpoints exist (pods are matched by service selector)
kubectl get endpoints myapp-clusterip-service -n production
# If "No resources found" or endpoints list is empty:
# -> Service selector labels don't match pod labels
# -> kubectl get pods -n production --show-labels

# Test routing from a debug pod inside the cluster
kubectl run curl-test --image=curlimages/curl --rm -it --restart=Never -- \
  curl -H "Host: myapp.example.com" http://$(kubectl get svc -n ingress-basic \
    ingress-nginx-controller -o jsonpath='{.spec.clusterIP}')/healthz
```

### Load Balancer Stuck in Pending

```bash
# Check service events
kubectl describe svc ingress-nginx-controller -n ingress-basic

# Verify the static IP exists in the correct resource group
az network public-ip list --resource-group $NODE_RG --output table

# Common causes:
#
# "User does not have permissions to create/update resource"
#   -> AKS managed identity lacks permission to use the public IP
#   -> Grant "Network Contributor" on the node resource group to the AKS identity
#
# Static IP in wrong resource group (your RG vs node RG)
#   -> Delete and recreate the IP in the correct node resource group
```

---

## Summary — Full Component Interaction Map

```
                         +-------------------------------------------+
                         |              AZURE CLOUD                  |
  User Browser --DNS-->  |  Azure DNS Zone (example.com)             |
       |                 |       ^ auto-managed by ExternalDNS       |
       |                 |                                           |
       +--TCP 443-->     |  Azure Load Balancer (52.154.156.139)     |
                         |       | routes to NodePort                |
                         +-------+-----------------------------------+
                                 |
                         +-------v-----------------------------------+
                         |         KUBERNETES CLUSTER                |
                         |                                           |
                         |  NGINX Ingress Controller                 |
                         |  +-- TLS termination (cert from Secret)   |
                         |  +-- Host/Path routing rules              |
                         |  +-- Proxies to ClusterIP Service         |
                         |              |                            |
                         |  cert-manager (watches Ingress)           |
                         |  +-- Requests cert from Let's Encrypt     |
                         |  +-- Stores cert as Kubernetes Secret     |
                         |  +-- Auto-renews 30 days before expiry    |
                         |                                           |
                         |  ExternalDNS (watches Ingress)            |
                         |  +-- Creates A records in Azure DNS Zone  |
                         |  +-- Uses MSI for authentication          |
                         |  +-- Deletes records when Ingress removed |
                         |                                           |
                         |  Application Pod                          |
                         |  +-- vault-agent-init (init container)    |
                         |  |   fetches secrets before app starts    |
                         |  +-- vault-agent (sidecar)                |
                         |  |   refreshes dynamic secrets            |
                         |  +-- myapp container                      |
                         |       sources /vault/secrets/config       |
                         |              |                            |
                         |  HashiCorp Vault (HA, 3 replicas)         |
                         |  +-- KV engine: static secrets            |
                         |  +-- Database engine: dynamic DB creds    |
                         |  +-- PKI engine: internal TLS certs       |
                         |  +-- Kubernetes auth via SA JWT token      |
                         |                                           |
                         +-------------------------------------------+
```
