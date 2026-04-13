# EKS — cert-manager & ALB Ingress Setup



## Prerequisites Checklist

Before applying any of the resources below, confirm these are already in place on your EKS cluster:

| Prerequisite | Check command |
|---|---|
| cert-manager installed | `kubectl get pods -n cert-manager` |
| AWS Load Balancer Controller installed | `kubectl get pods -n kube-system \| grep aws-load-balancer` |
| LBC has an IAM role with ALB permissions | Check the service account annotation |
| Worker node subnets tagged for ALB discovery | `kubernetes.io/role/elb=1` on public subnets |

### Install cert-manager (if not already present)

### Install AWS Load Balancer Controller (if not already present)



---

## Apply Order Summary

```bash
# 1. Namespace
kubectl create namespace bdd-namespace

# 2. ClusterIssuer
kubectl apply -f cluster-issuer.yaml

# 3. Certificate
kubectl apply -f cert_alb.yaml

# 4. Backend + Ingress
kubectl apply -f resources/ingress-alb.test.local

# 5. Validate end to end
kubectl get certificate,secret,ingress -n bdd-namespace
```

Once the Ingress `ADDRESS` field is populated, the BDD test will progress through Steps 5–8 without issue.

---

## Resource 1 — ClusterIssuer (`cluster-issuer.yaml`)

The `selfsigned-cluster-issuer` that the BDD test checks for in its pre-flight step (Step 1).
cert-manager uses this issuer to sign all Certificate CRs that reference it.

```yaml
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: selfsigned-cluster-issuer
spec:
  selfSigned: {}
```

```bash
kubectl apply -f cluster-issuer.yaml

# Verify
kubectl get clusterissuer selfsigned-cluster-issuer
# READY should be True
```

---

## Resource 2 — Certificate CR (`cert_alb.yaml`)

Applied by the BDD test in Step 2. cert-manager reads this and automatically populates
the `traefik-sidecar-secret-tls` Secret with a signed `tls.crt` and `tls.key`.

```yaml
apiVersion: cert-manager.io/v1
kind: Certificate
metadata:
  name: traefik-sidecar-cert
  namespace: bdd-namespace        # must match namespace the test reads the Secret from
spec:
  secretName: traefik-sidecar-secret-tls
  duration: 8760h                 # 1 year
  renewBefore: 720h               # renew 30 days before expiry
  commonName: ourservice.local
  dnsNames:
    - ourservice.local
  issuerRef:
    name: selfsigned-cluster-issuer
    kind: ClusterIssuer
```

```bash
# Create the namespace first if it doesn't exist
kubectl create namespace bdd-namespace --dry-run=client -o yaml | kubectl apply -f -

kubectl apply -f cert_alb.yaml

# Verify cert-manager issued it
kubectl get certificate -n bdd-namespace
kubectl get secret traefik-sidecar-secret-tls -n bdd-namespace
# Should contain tls.crt and tls.key
```

---

## Resource 3 — ALB Ingress + Backend (`resources/ingress-alb.test.local`)

Loaded and applied by the BDD test in Step 4. Contains three resources in a single file.

Replace `<YOUR_CLUSTER_NAME>` with your actual EKS cluster name — the BDD test's boto3 query
in Step 6 filters on this tag to locate the ALB in AWS.

```yaml
# Backend Deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ourservice
  namespace: bdd-namespace
spec:
  replicas: 1
  selector:
    matchLabels:
      app: ourservice
  template:
    metadata:
      labels:
        app: ourservice
    spec:
      containers:
        - name: ourservice
          image: nginx:alpine          # simple backend to return 200
          ports:
            - containerPort: 80
---
# ClusterIP Service — ALB target group points here
apiVersion: v1
kind: Service
metadata:
  name: ourservice-svc
  namespace: bdd-namespace
spec:
  selector:
    app: ourservice
  ports:
    - port: 80
      targetPort: 80
  type: ClusterIP
---
# ALB Ingress — AWS Load Balancer Controller watches this
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: ourservice-ingress
  namespace: bdd-namespace
  annotations:
    kubernetes.io/ingress.class: alb

    # Provision an internet-facing ALB (use "internal" for private)
    alb.ingress.kubernetes.io/scheme: internet-facing

    # Target individual pods, not the NodePort
    alb.ingress.kubernetes.io/target-type: ip

    # Health check path — must return 200
    alb.ingress.kubernetes.io/healthcheck-path: /

    # Tag the ALB with your EKS cluster name — Step 6 of the BDD test
    # queries for this tag to find the ALB in AWS
    alb.ingress.kubernetes.io/tags: "kubernetes.io/cluster/<YOUR_CLUSTER_NAME>=owned"
spec:
  rules:
    - host: ourservice.local        # Step 7 sends this as the Host header
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: ourservice-svc
                port:
                  number: 80
```

```bash
kubectl apply -f resources/ingress-alb.test.local

# Watch for the ALB hostname to appear (takes 1–3 minutes)
kubectl get ingress ourservice-ingress -n bdd-namespace -w
# ADDRESS column will populate once the ALB is provisioned
```

---

## BDD Test Step Reference

| Step | What it does | Key resource |
|---|---|---|
| Step 1 | Pre-flight — checks `selfsigned-cluster-issuer` CRD exists | `ClusterIssuer` |
| Step 2 | Applies `cert_alb.yaml` to request a TLS certificate | `Certificate` CR |
| Step 3 | Reads `traefik-sidecar-secret-tls` and validates the X.509 cert | `Secret` |
| Step 4 | Applies `ingress-alb.test.local` (Deployment, Service, Ingress) | Ingress + backend |
| Step 5 | Polls Ingress `.status.loadBalancer.ingress[0].hostname` up to 2 min | Ingress status |
| Step 6 | Queries AWS via boto3 to confirm ALB state is `active` | AWS ALB |
| Step 7 | Sends HTTP GET to ALB DNS with `Host: ourservice.local` header | ALB listener rules |
| Step 8 | Asserts HTTP 200 response — full chain validated | End to end |
| Step 9 | Deletes the `Certificate` CR — cert-manager GCs the Secret | Cleanup |
| Step 10 | Deletes all resources from Step 4 — LBC deprovisions the ALB | Cleanup |

---

## Validation Commands

```bash
# Check ClusterIssuer is ready
kubectl get clusterissuer selfsigned-cluster-issuer

# Check Certificate was issued
kubectl describe certificate traefik-sidecar-cert -n bdd-namespace
# Look for: "Certificate is up to date and has not expired"

# Inspect the TLS Secret cert-manager created
kubectl get secret traefik-sidecar-secret-tls -n bdd-namespace -o yaml

# Check ALB hostname has been assigned
kubectl get ingress ourservice-ingress -n bdd-namespace

# Check LBC logs if ALB is not provisioning
kubectl logs -n kube-system deploy/aws-load-balancer-controller
```
