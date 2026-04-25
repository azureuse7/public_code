# Kubernetes Ingress Guide

## What Is Kubernetes Ingress?

Before understanding Ingress, it helps to understand the problem it solves.

When you deploy an application in Kubernetes, it runs inside the cluster and is isolated from the outside world. Kubernetes provides several ways to expose that application, but they are not all equally suitable for production workloads.

## The Problem: How Do You Expose Services?

### Option 1 — ClusterIP

`ClusterIP` is the default service type in Kubernetes.

- Reachable only from inside the cluster
- Good for internal service-to-service communication
- Not useful for direct external access

### Option 2 — NodePort

`NodePort` exposes a port on every node in the cluster.

- Reachable through each node’s IP address
- Uses a high port range such as `30000–32767`
- Works, but is awkward for production use
- Lacks proper routing and traffic management

### Option 3 — LoadBalancer

`LoadBalancer` creates a cloud load balancer for a service.

On AKS, this means Azure provisions an Azure Load Balancer for that service.

This works, but it has drawbacks:

- Every service gets its own load balancer or frontend
- Every externally exposed service may need its own IP
- Costs can grow as services increase
- There is no advanced HTTP routing logic by default
- Ten services can mean ten public or private entry points

### Option 4 — Ingress

`Ingress` is the standard solution for exposing HTTP and HTTPS applications in Kubernetes.

With Ingress, you typically use:

- One entry point
- One load balancer
- One IP address
- Many routing rules for many services

That means you can route traffic based on hostname or URL path instead of creating a separate external endpoint for every service.

## What Ingress Actually Is

Ingress is a Kubernetes API object that defines HTTP and HTTPS routing rules.

For example:

- Requests for `api.example.internal/users` can be sent to `users-service`
- Requests for `api.example.internal/orders` can be sent to `orders-service`

A simple way to think about it:

```text
Internet
   |
   | (one IP)
   v
[ Ingress ]
   |
   |-- /users  --> users-service:80
   |-- /orders --> orders-service:80
   |-- /auth   --> auth-service:80
```

Ingress can handle:

- **Host-based routing** — `app1.example.internal` vs `app2.example.internal`
- **Path-based routing** — `/api/v1` vs `/api/v2`
- **TLS termination** — HTTPS certificates are handled at the ingress layer
- **Redirects, rewrites, and rate limiting** — depending on the controller implementation

## Important: Ingress Is Only a Spec

This is the point many people miss.

The Ingress resource itself is only a set of routing rules. On its own, it does nothing.

You need an **Ingress Controller** to read those rules and implement them.

A useful analogy:

- **Ingress object** = the rulebook
- **Ingress Controller** = the component that reads and enforces the rulebook

Without an Ingress Controller, creating an Ingress resource has no effect.

## What Is the NGINX Ingress Controller?

The **NGINX Ingress Controller** is one of the most widely used Ingress Controllers in Kubernetes.

It does the following:

- Watches the Kubernetes API for Ingress resources
- Translates Ingress rules into NGINX configuration
- Reloads NGINX automatically when rules change
- Proxies incoming HTTP and HTTPS traffic to the correct backend services

Under the hood, it is an NGINX reverse proxy that configures itself dynamically based on Kubernetes resources.

```text
Internet
   |
   v
Azure Load Balancer (1 IP)
   |
   v
NGINX Ingress Controller Pod
   |
   |-- Host: app1.example.com  --> service-a:80
   |-- Host: app2.example.com  --> service-b:80
   |-- /api/v1                 --> service-c:80
```

## How It Looks in Practice on AKS

### 1. Install NGINX Ingress Controller with Helm

```bash
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm repo update

helm install ingress-nginx ingress-nginx/ingress-nginx \
  --namespace ingress-nginx \
  --create-namespace \
  --set controller.service.annotations."service\.beta\.kubernetes\.io/azure-load-balancer-health-probe-request-path"=/healthz
```

This deploys:

- An NGINX controller deployment or set of controller pods
- A `Service` of type `LoadBalancer`
- An Azure Load Balancer provisioned by AKS

### 2. Deploy Your Application

Your application does **not** need its own external load balancer.

A `ClusterIP` service is enough, because the Ingress Controller will handle external access.

```yaml
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
          image: my-registry.example.com/my-app:latest
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
  type: ClusterIP
```

### 3. Define the Ingress Rules

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: my-app-ingress
  namespace: default
  annotations:
    kubernetes.io/ingress.class: "nginx"
    nginx.ingress.kubernetes.io/rewrite-target: /
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
spec:
  tls:
    - hosts:
        - myapp.example.internal
      secretName: myapp-tls-cert
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

When you apply this resource, the NGINX Ingress Controller detects it and updates its configuration automatically.

No manual NGINX edits are required.

## AKS-Specific Behaviour

On AKS, when the NGINX Ingress Controller service is of type `LoadBalancer`, Azure automatically provisions an Azure Load Balancer.

You can influence this behaviour with annotations on the controller service.

### Internal Load Balancer

Use this when the ingress should only be reachable from inside your network.

```yaml
service.beta.kubernetes.io/azure-load-balancer-internal: "true"
```

### Pin to a Specific Subnet

```yaml
service.beta.kubernetes.io/azure-load-balancer-internal-subnet: "aks-ingress-subnet"
```

### Use a Specific Static Private IP

```yaml
service.beta.kubernetes.io/azure-load-balancer-ipv4: "10.0.1.50"
```

In many enterprise environments, an **internal load balancer** is the preferred option so the application is only reachable from inside the virtual network, VPN, or private connectivity path.

## NGINX Ingress vs Azure Application Gateway Ingress Controller

On AKS, you may also come across **Application Gateway Ingress Controller (AGIC)**.

Here is the high-level difference:

| Feature | NGINX Ingress | Azure Application Gateway / AGIC |
|---|---|---|
| Where it runs | Inside AKS as pods | Outside AKS as an Azure-managed service |
| Cost | Mostly pod and node resources | Additional Application Gateway cost |
| WAF support | Available through add-ons and extra config | Native Azure WAF support |
| TLS termination | Yes | Yes |
| Complexity | Lower | Higher |
| Best fit | Most workloads, flexibility, simpler operations | Native Azure integration and WAF-heavy use cases |

For many platform teams, NGINX Ingress is the simpler and more flexible default.

## End-to-End Traffic Flow on AKS

```text
User browser / API client
        |
        | HTTPS request to myapp.example.internal
        v
Azure Load Balancer
(provisioned automatically by AKS)
        |
        | TCP :443
        v
NGINX Ingress Controller Pod
- Terminates TLS using cert from Kubernetes Secret
- Reads Ingress rules
- Matches host and path
        |
        | HTTP inside the cluster
        v
my-app-svc (ClusterIP Service)
        |
        v
my-app Pod
```

## What You Need Before You Can Reach the App in a Browser

The guide above describes the Kubernetes resources, but a few supporting pieces must exist before the application is actually reachable.

### 1. The Load Balancer IP

After deploying the controller, get the ingress service details:

```bash
kubectl get svc -n ingress-nginx
```

Look for the `EXTERNAL-IP` of the `ingress-nginx-controller` service.

### 2. DNS Resolution

The hostname used in the Ingress, such as `myapp.example.internal`, must resolve to that load balancer IP.

This can be done through:

- Internal DNS
- Azure Private DNS
- Corporate DNS
- A temporary hosts file entry for testing

Example hosts file entry:

```text
10.0.1.50  myapp.example.internal
```

### 3. Network Access

If you use an internal load balancer, the IP will be private.

You can only reach it from:

- A machine inside the Azure VNet
- A machine connected by VPN
- A machine connected through ExpressRoute or equivalent private network access

### 4. A Valid TLS Certificate

The secret referenced in the Ingress must exist.

If the secret is missing or invalid, the browser will show a TLS error.

For a production setup, this is usually managed by `cert-manager`.

## Quickest Way to Test the App Without Ingress

Before debugging DNS, TLS, or load balancers, test the application directly with `kubectl port-forward`.

```bash
kubectl port-forward svc/my-app-svc 8080:80
```

Then open:

```text
http://localhost:8080
```

This bypasses:

- Azure Load Balancer
- NGINX Ingress Controller
- DNS
- TLS and certificates

It is a fast way to answer the question:

**“Is the application itself working?”**

If it works with port-forwarding but not through Ingress, the problem is likely in the DNS, TLS, or Ingress layer rather than the application.

## Creating a Valid TLS Certificate

There are two common approaches.

### Option A — cert-manager (Recommended)

`cert-manager` is the standard Kubernetes tool for automatically issuing and renewing certificates.

Example `Certificate` resource:

```yaml
apiVersion: cert-manager.io/v1
kind: Certificate
metadata:
  name: myapp-tls-cert
  namespace: default
spec:
  secretName: myapp-tls-cert
  issuerRef:
    name: internal-ca-issuer
    kind: ClusterIssuer
  dnsNames:
    - myapp.example.internal
```

What happens behind the scenes:

1. `cert-manager` sees the `Certificate` resource
2. It contacts the configured issuer or certificate authority
3. The certificate is generated and signed
4. The resulting key and certificate are stored as a Kubernetes TLS secret
5. The Ingress uses that secret automatically
6. `cert-manager` renews it before expiry

The Ingress only needs to reference the secret:

```yaml
spec:
  tls:
    - hosts:
        - myapp.example.internal
      secretName: myapp-tls-cert
```

### Option B — Manual Self-Signed Certificate (Testing Only)

For quick testing, you can generate a self-signed certificate manually.

```bash
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout tls.key \
  -out tls.crt \
  -subj "/CN=myapp.example.internal"

kubectl create secret tls myapp-tls-cert \
  --cert=tls.crt \
  --key=tls.key \
  --namespace=default
```

Kubernetes expects the TLS secret to contain:

```text
myapp-tls-cert
├── tls.crt
└── tls.key
```

This is acceptable for a short-term test, but browsers will warn that the certificate is not trusted.

## What `kubectl port-forward` Is Actually Doing

This is one of the most useful debugging tools in Kubernetes.

Command:

```bash
kubectl port-forward svc/my-app-svc 8080:80
```

Meaning:

| Part | Meaning |
|---|---|
| `svc/my-app-svc` | Target the service named `my-app-svc` |
| `8080` | Local port on your machine |
| `80` | Port on the service inside the cluster |

Traffic flow:

```text
Your laptop (localhost:8080)
        |
        | kubectl tunnel through the Kubernetes API
        v
Kubernetes API Server
        |
        v
my-app-svc (ClusterIP :80)
        |
        v
my-app Pod (:8080)
```

This means `kubectl` acts like a local proxy and forwards your traffic through the Kubernetes control plane to the target service.

### Why This Is Useful

It helps isolate the problem.

If the application works through port-forwarding but fails through the Ingress, then:

- The app is probably healthy
- The issue is likely in Ingress rules, DNS, networking, or TLS

### Important Notes

- It only works while the command is running
- Pressing `Ctrl+C` stops the tunnel
- It is for testing and debugging, not production traffic

You can also forward directly to a pod:

```bash
kubectl port-forward pod/my-app-7d6f9b-xkq2p 8080:8080
```

You can forward multiple ports at once:

```bash
kubectl port-forward svc/my-app-svc 8080:80 9090:9090
```

## Summary

Ingress is the Kubernetes-native way to expose HTTP and HTTPS services using a shared entry point.

At a high level:

- `Service` objects expose your application internally
- `Ingress` defines routing rules
- An `Ingress Controller` enforces those rules
- On AKS, the controller usually sits behind an Azure Load Balancer
- TLS can be terminated at the ingress layer using a Kubernetes TLS secret

For most HTTP and HTTPS workloads on AKS, this gives you a clean, scalable, and cost-effective way to route traffic to many services through a single ingress layer.
