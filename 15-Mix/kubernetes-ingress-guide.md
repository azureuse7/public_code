# Kubernetes Ingress — A Practical Guide

## The Problem: How Do You Expose Services?

When you deploy an app in Kubernetes, it lives inside the cluster — completely isolated from the outside world. You have a few options to expose it:

**Option 1 — ClusterIP (default)**
Only reachable within the cluster. Useless for external traffic.

**Option 2 — NodePort**
Exposes a port on every node's IP. Crude, not production-grade, awkward port numbers (30000–32767).

**Option 3 — LoadBalancer**
Creates a cloud load balancer for each service. Works, but:
- Every service gets its own public IP
- Costs money per IP
- No routing logic — it's just a dumb TCP passthrough
- 10 services = 10 load balancers = 10 public IPs

**Option 4 — Ingress ✅**
One load balancer, one IP, routing traffic to many services based on rules. This is the right answer for HTTP/HTTPS workloads.

---

## What Ingress Actually Is

Ingress is a Kubernetes API object that defines routing rules. It says:

> "If a request comes in for `api.myapp.com/users`, send it to the `users-service`. If it comes in for `api.myapp.com/orders`, send it to the `orders-service`."

```
Internet
   |
   | (one public IP)
   v
[ Ingress ]
   |
   |-- /users  --> users-service:80
   |-- /orders --> orders-service:80
   |-- /auth   --> auth-service:80
```

Ingress can handle:
- **Host-based routing** — `app1.example.com` vs `app2.example.com`
- **Path-based routing** — `/api/v1` vs `/api/v2`
- **TLS termination** — HTTPS certificates, so your services don't need to handle SSL themselves
- **Redirects, rewrites, rate limiting** — depending on the implementation

---

## Ingress is Just a Spec — It Needs a Controller

This is the key thing people miss. The Ingress YAML object is just a set of rules — **it does nothing on its own**. You need an **Ingress Controller** to actually implement those rules.

Think of it like this:
- The **Ingress object** = a traffic rulebook
- The **Ingress Controller** = the traffic warden that reads and enforces the rulebook

---

## What is NGINX Ingress Controller?

NGINX Ingress Controller is the most widely used Ingress Controller. It:
- Watches the Kubernetes API for Ingress objects
- Translates those Ingress rules into NGINX configuration (`nginx.conf`)
- Reloads NGINX automatically whenever rules change
- Proxies incoming HTTP/HTTPS traffic to the correct backend services

Under the hood, it's literally an NGINX reverse proxy — but one that configures itself automatically based on your Kubernetes Ingress objects.

```
Internet
   |
   v
Cloud Load Balancer (1 public IP)
   |
   v
NGINX Ingress Controller Pod
   |  (reads your Ingress YAML, acts as reverse proxy)
   |
   |-- Host: app1.com  --> service-a:80
   |-- Host: app2.com  --> service-b:80
   |-- /api/v1         --> service-c:80
```

---

## How It Looks in Practice on AKS

### 1. Install NGINX Ingress Controller via Helm

```bash
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm repo update

helm install ingress-nginx ingress-nginx/ingress-nginx \
  --namespace ingress-nginx \
  --create-namespace \
  --set controller.service.annotations."service\.beta\.kubernetes\.io/azure-load-balancer-health-probe-request-path"=/healthz
```

This deploys:
- An NGINX controller Deployment (the actual proxy pods)
- A Service of type `LoadBalancer` — which tells AKS to provision an Azure Load Balancer with a public (or internal) IP

### 2. Deploy Your App

```yaml
# Your app deployment + service (ClusterIP is fine here)
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-app
  namespace: default
spec:
  replicas: 2
  selector:
    matchLabels:
      app: my-app
  template:
    metadata:
      labels:
        app: my-app
    spec:
      containers:
        - name: my-app
          image: your-registry/my-app:latest
          ports:
            - containerPort: 8080
---
apiVersion: v1
kind: Service
metadata:
  name: my-app-svc
  namespace: default
spec:
  selector:
    app: my-app
  ports:
    - port: 80
      targetPort: 8080
  type: ClusterIP   # internal only — Ingress handles external access
```

### 3. Define the Ingress Rules

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: my-app-ingress
  namespace: default
  annotations:
    # Tell Kubernetes to use the NGINX ingress controller
    kubernetes.io/ingress.class: "nginx"

    # Rewrite the URL path before forwarding to backend
    nginx.ingress.kubernetes.io/rewrite-target: /

    # Force HTTPS redirect
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
spec:
  tls:
    - hosts:
        - myapp.example.internal
      secretName: myapp-tls-cert   # a cert-manager managed secret
  rules:
    - host: myapp.example.internal
      http:
        paths:
          - path: /api
            pathType: Prefix
            backend:
              service:
                name: my-app-svc
                port:
                  number: 80
```

When you apply this, NGINX Ingress Controller immediately picks it up and reconfigures the proxy. **No restarts needed.**

---

## AKS-Specific Behaviour

On AKS, when NGINX Ingress creates its LoadBalancer service, Azure automatically provisions a Load Balancer resource. You can control this with annotations:

```yaml
# Internal (private) load balancer — no public IP
service.beta.kubernetes.io/azure-load-balancer-internal: "true"

# Pin to a specific subnet
service.beta.kubernetes.io/azure-load-balancer-internal-subnet: "aks-ingress-subnet"

# Use a static IP you've pre-allocated
service.beta.kubernetes.io/azure-load-balancer-ipv4: "10.0.1.50"
```

For most production use cases, you'd want an **internal load balancer** — no public exposure, traffic only from within your Azure VNet or via ExpressRoute/VPN.

---

## NGINX Ingress vs Azure Application Gateway Ingress (AGIC)

| Feature | NGINX Ingress | Azure App Gateway (AGIC) |
|---|---|---|
| Where it runs | Inside AKS as a pod | Outside AKS, Azure-managed service |
| Cost | Free (just pod resources) | App Gateway is expensive |
| WAF support | Via ModSecurity plugin | Native Azure WAF |
| TLS termination | Yes (cert-manager) | Yes (Azure Key Vault) |
| Best for | Most workloads, flexibility | When you need native Azure WAF |
| Complexity | Lower | Higher (two things to manage) |

For most platform engineering use cases, **NGINX Ingress is the right default** — simpler, cheaper, and you have full control.

---

## Full Traffic Flow on AKS (End to End)

```
User browser / API client
        |
        | HTTPS request to myapp.example.internal
        v
  Azure Load Balancer
  (provisioned automatically by AKS when you deploy NGINX Ingress)
        |
        | TCP :443
        v
  NGINX Ingress Controller Pod  (running in ingress-nginx namespace)
  - Terminates TLS using cert from Kubernetes Secret
  - Reads Ingress rules
  - Matches host + path
        |
        | HTTP (plain, inside cluster — already decrypted)
        v
  my-app-svc (ClusterIP Service)
        |
        v
  my-app Pod (your actual application)
```

---

## What You Need to Actually Hit It in a Browser

After deploying, a few things must be in place:

**1. Get the load balancer IP**
```bash
kubectl get svc -n ingress-nginx
```
Look for the `EXTERNAL-IP` on the `ingress-nginx-controller` service.

**2. DNS resolution**

The host `myapp.example.internal` won't resolve unless either:
- It's registered in your internal DNS (Azure Private DNS Zone or corporate DNS)
- Or you temporarily add it to `/etc/hosts` (Linux/Mac) or `C:\Windows\System32\drivers\etc\hosts` (Windows):
  ```
  10.0.1.50  myapp.example.internal
  ```

**3. Network access**

If using an internal load balancer, the IP will be a private RFC1918 address. You can only reach it if you're:
- On a machine inside the Azure VNet
- Connected via VPN or ExpressRoute

**4. A valid TLS certificate**

The `myapp-tls-cert` secret referenced in the Ingress needs to exist and be valid, otherwise you'll get a browser TLS error. See the TLS section below, or temporarily remove the `tls:` block for plain HTTP testing.

**Quickest way to test without all of the above:**
```bash
kubectl port-forward svc/my-app-svc 8080:80
```
Then open `http://localhost:8080` in your browser. This skips DNS, TLS, and load balancer entirely — good for a quick sanity check.

---

## TLS Certificates

### Option A: cert-manager (recommended)

cert-manager is a Kubernetes add-on that automatically creates and renews TLS certificates. Create a `Certificate` object:

```yaml
apiVersion: cert-manager.io/v1
kind: Certificate
metadata:
  name: myapp-tls-cert
  namespace: default
spec:
  secretName: myapp-tls-cert        # this is the secret your Ingress references
  issuerRef:
    name: internal-ca-issuer        # points to your internal CA
    kind: ClusterIssuer
  dnsNames:
    - myapp.example.internal
```

What happens behind the scenes:
1. cert-manager sees this `Certificate` object
2. It contacts the `ClusterIssuer` (your CA — could be internal PKI, Vault, or Let's Encrypt)
3. The CA signs the certificate
4. cert-manager stores the result as a Kubernetes Secret called `myapp-tls-cert`
5. Your Ingress picks it up automatically — no restart needed
6. cert-manager watches expiry and auto-renews before it expires

The Ingress then references the secret name:

```yaml
spec:
  tls:
    - hosts:
        - myapp.example.internal
      secretName: myapp-tls-cert   # cert-manager created this
```

### Option B: Manual Self-Signed (quick testing only)

```bash
# Generate a self-signed cert
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout tls.key \
  -out tls.crt \
  -subj "/CN=myapp.example.internal"

# Create the Kubernetes secret manually
kubectl create secret tls myapp-tls-cert \
  --cert=tls.crt \
  --key=tls.key \
  --namespace=default
```

The secret format Kubernetes expects for TLS:

```
myapp-tls-cert
├── tls.crt   (the certificate)
└── tls.key   (the private key)
```

> ⚠️ Your browser will show a security warning because it's self-signed and not trusted by any CA. Fine for a quick test, not for real use.

---

## Understanding `kubectl port-forward`

```bash
kubectl port-forward svc/my-app-svc 8080:80
```

| Part | Meaning |
|---|---|
| `svc/my-app-svc` | Target a Service object called `my-app-svc` |
| `8080` | Port on your local machine |
| `80` | Port on the Service inside the cluster |

**What it creates:**

```
Your laptop (localhost:8080)
        |
        | encrypted kubectl tunnel (through kube-apiserver)
        v
  Kubernetes API Server
        |
        v
  my-app-svc (ClusterIP :80)
        |
        v
  my-app Pod (:8080)
```

The `kubectl` process on your machine acts as a local proxy — completely bypassing:
- ❌ Cloud Load Balancer
- ❌ NGINX Ingress Controller
- ❌ TLS / cert-manager
- ❌ DNS

**Why this is useful:**

It answers a very specific question — *"Is my app itself working?"* — independent of all the networking infrastructure around it. If your app works on `localhost:8080` but not through the Ingress, the problem is in the Ingress/DNS/TLS layer, not your app. That isolation is invaluable when debugging.

**Useful variants:**

```bash
# Forward directly to a pod instead of a service
kubectl port-forward pod/my-app-7d6f9b-xkq2p 8080:8080

# Forward multiple ports at once
kubectl port-forward svc/my-app-svc 8080:80 9090:9090
```

> ⚠️ `port-forward` only works while the command is running — `Ctrl+C` kills the tunnel. It is for debugging only, never for real traffic.
