# EKS Ingress — Full End-to-End Guide
## AWS Load Balancer Controller · NGINX Ingress · ACM · cert-manager · HashiCorp Vault

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [Prerequisites and EKS Cluster Setup](#2-prerequisites-and-eks-cluster-setup)
3. [AWS Load Balancer Controller](#3-aws-load-balancer-controller)
4. [How AWS Load Balancers Connect to EKS](#4-how-aws-load-balancers-connect-to-eks)
5. [Install NGINX Ingress Controller on EKS](#5-install-nginx-ingress-controller-on-eks)
6. [Deploy Backend Applications](#6-deploy-backend-applications)
7. [Ingress Routing — Path and Host Based](#7-ingress-routing--path-and-host-based)
8. [TLS Option A — AWS Certificate Manager (ACM)](#8-tls-option-a--aws-certificate-manager-acm)
9. [TLS Option B — cert-manager with Let's Encrypt](#9-tls-option-b--cert-manager-with-lets-encrypt)
10. [HashiCorp Vault on EKS](#10-hashicorp-vault-on-eks)
11. [Vault Agent Injector with EKS Workloads](#11-vault-agent-injector-with-eks-workloads)
12. [cert-manager with Vault PKI Backend](#12-cert-manager-with-vault-pki-backend)
13. [ExternalDNS on EKS with Route 53](#13-externaldns-on-eks-with-route-53)
14. [Network Policies on EKS](#14-network-policies-on-eks)
15. [Full End-to-End Deployment Walkthrough](#15-full-end-to-end-deployment-walkthrough)
16. [Troubleshooting Reference](#16-troubleshooting-reference)
17. [EKS vs AKS — Key Differences Summary](#17-eks-vs-aks--key-differences-summary)
18. [Component Summary](#18-component-summary)

---

## 1. Architecture Overview

EKS differs from AKS in how it integrates with cloud load balancers, DNS, and IAM. Understanding the AWS-specific components before writing any YAML is essential.

### High-Level Architecture

```
Internet
    │
    ▼
┌─────────────────────────────────────────────────────────┐
│   AWS Application Load Balancer (ALB) — Layer 7         │
│   OR                                                    │
│   AWS Network Load Balancer (NLB) — Layer 4             │
│                                                         │
│   Provisioned automatically by:                         │
│   AWS Load Balancer Controller (running in EKS)         │
└──────────────────────┬──────────────────────────────────┘
                       │
          ┌────────────┴────────────┐
          │  Two integration modes  │
          └────────────┬────────────┘
                       │
          ┌────────────▼────────────┐
          │                         │
    ┌─────▼──────┐           ┌──────▼─────┐
    │  Mode 1:   │           │  Mode 2:   │
    │  ALB acts  │           │  NLB acts  │
    │  as Layer 7 │          │  as Layer 4 │
    │  Ingress   │           │  in front  │
    │  directly  │           │  of NGINX  │
    │  (no NGINX)│           │  Ingress   │
    └─────┬──────┘           └──────┬─────┘
          │                         │
          │                   ┌─────▼──────────────┐
          │                   │ NGINX Ingress       │
          │                   │ Controller          │
          │                   │ (Deployment in      │
          │                   │  ingress-basic ns)  │
          │                   └─────┬───────────────┘
          │                         │
          └──────────┬──────────────┘
                     │ routes to ClusterIP Services
                     ▼
          ┌────────────────────┐
          │  Backend App Pods  │
          │  (ClusterIP Svc)   │
          └────────────────────┘
```

### Full Stack with All Components

```
Internet
    │
    ▼
Route 53 (DNS)
    │  A record: app1.yourdomain.com → ALB/NLB endpoint
    ▼
AWS ALB or NLB
    │
    ▼
NGINX Ingress Controller  ◄──── reads TLS certs from K8s Secrets
    │                            (cert-manager populates these Secrets)
    │  routes based on
    │  host + path rules
    ├──────────────────────────────────────────┐
    ▼                                          ▼
App1 ClusterIP Service                App2 ClusterIP Service
    │                                          │
    ▼                                          ▼
App1 Pods                             App2 Pods
    │                                          │
    └──────────────┬───────────────────────────┘
                   │ both read secrets from
                   ▼
         HashiCorp Vault (on EKS)
         ├── PKI engine  → TLS certificates for cert-manager
         ├── KV engine   → app runtime secrets
         └── K8s auth    → authenticates pods via IRSA or ServiceAccount JWT

cert-manager
    ├── ClusterIssuer: Let's Encrypt (public certs via ACME)
    ├── ClusterIssuer: Vault PKI    (private/internal certs)
    └── Watches Ingress → creates Certificate → populates K8s Secret

ExternalDNS
    └── Watches Ingress → creates/updates Route 53 records automatically

AWS IAM / IRSA (IAM Roles for Service Accounts)
    └── Grants Kubernetes pods permissions to call AWS APIs
        (used by: AWS LB Controller, ExternalDNS, cert-manager DNS-01)
```

### Request Lifecycle (HTTPS, NGINX mode)

```
1.  Browser resolves app1.yourdomain.com
    → Route 53 returns NLB DNS name or static IP
2.  TCP:443 hits AWS NLB
    → NLB forwards raw TCP to a node's NodePort
3.  kube-proxy routes NodePort → NGINX pod
4.  NGINX reads TLS cert from Secret app1-tls-secret
    (this Secret was populated by cert-manager, which got the cert from
     Vault PKI or Let's Encrypt)
5.  NGINX terminates TLS
    → inspects HTTP Host header: app1.yourdomain.com
    → matches Ingress rule
    → proxies plain HTTP to app1-clusterip-service:80
6.  ClusterIP service selects an App1 pod
7.  App1 pod reads DB credentials from /vault/secrets/db-config
    (written there by vault-agent sidecar at pod startup)
8.  App1 responds → NGINX → NLB → browser
```

---

## 2. Prerequisites and EKS Cluster Setup

### Tools Required



---

## 3. AWS Load Balancer Controller

### What Is the AWS Load Balancer Controller?

The AWS Load Balancer Controller (LBC) is a Kubernetes controller that runs inside EKS and watches for two types of resources:

- **Ingress resources** — provisions an **AWS Application Load Balancer (ALB)**
- **Services of type LoadBalancer** — provisions an **AWS Network Load Balancer (NLB)**

It is the AWS equivalent of AKS's Cloud Controller Manager load balancer integration, but with significantly more features and configuration options exposed via annotations.

```
Without AWS LBC:
  Service (type: LoadBalancer) → Classic Load Balancer (deprecated, Layer 4 only)

With AWS LBC:
  Service (type: LoadBalancer) → Network Load Balancer (Layer 4, better performance)
  Ingress                      → Application Load Balancer (Layer 7, HTTP-aware)
```

### Why You Need IRSA for AWS LBC

The AWS LBC must call AWS APIs (to create/delete ALBs, NLBs, Target Groups, etc.). In EKS, AWS permissions are granted to pods using **IRSA — IAM Roles for Service Accounts**. This maps a Kubernetes ServiceAccount to an AWS IAM Role, so pods get AWS credentials without storing access keys anywhere.

```
Pod (with ServiceAccount: aws-load-balancer-controller)
    │
    │  presents K8s ServiceAccount JWT token
    ▼
AWS STS AssumeRoleWithWebIdentity
    │
    │  JWT validated against EKS OIDC provider
    ▼
IAM Role: AWSLoadBalancerControllerRole
    │
    │  has inline policy: AWSLoadBalancerControllerIAMPolicy
    ▼
Can call: elasticloadbalancing:*, ec2:Describe*, iam:CreateServiceLinkedRole, etc.
```

### Step 1: Create the IAM Policy for AWS LBC

```bash
# Download the official IAM policy document from AWS
curl -O https://raw.githubusercontent.com/kubernetes-sigs/aws-load-balancer-controller/v2.7.0/docs/install/iam_policy.json

# Create the IAM policy in your AWS account
aws iam create-policy \
  --policy-name AWSLoadBalancerControllerIAMPolicy \
  --policy-document file://iam_policy.json

# Note the policy ARN from the output:
# arn:aws:iam::111122223333:policy/AWSLoadBalancerControllerIAMPolicy
```

### Step 2: Create the IRSA Role for AWS LBC

```bash
# Set variables
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
CLUSTER_NAME=eks-demo
REGION=eu-west-2

# Create the IAM service account — eksctl handles the role creation and annotation
eksctl create iamserviceaccount \
  --cluster=$CLUSTER_NAME \
  --namespace=kube-system \
  --name=aws-load-balancer-controller \
  --role-name=AWSLoadBalancerControllerRole \
  --attach-policy-arn=arn:aws:iam::${ACCOUNT_ID}:policy/AWSLoadBalancerControllerIAMPolicy \
  --approve \
  --region=$REGION

# Verify the ServiceAccount was created with the IAM role annotation
kubectl describe serviceaccount aws-load-balancer-controller -n kube-system
# Annotations:
#   eks.amazonaws.com/role-arn: arn:aws:iam::111122223333:role/AWSLoadBalancerControllerRole
#                               ^^^^ This annotation is what enables IRSA
```

### Step 3: Install AWS LBC via Helm

```bash
# Add the EKS Helm repository
helm repo add eks https://aws.github.io/eks-charts
helm repo update

# Get your VPC ID (required by the controller)
VPC_ID=$(aws eks describe-cluster \
  --name $CLUSTER_NAME \
  --region $REGION \
  --query "cluster.resourcesVpcConfig.vpcId" \
  --output text)

# Install AWS Load Balancer Controller
helm install aws-load-balancer-controller eks/aws-load-balancer-controller \
  --namespace kube-system \
  --set clusterName=$CLUSTER_NAME \
  --set serviceAccount.create=false \
  --set serviceAccount.name=aws-load-balancer-controller \
  --set region=$REGION \
  --set vpcId=$VPC_ID \
  --set replicaCount=2

# Verify controller pods are running
kubectl get pods -n kube-system -l app.kubernetes.io/name=aws-load-balancer-controller
# NAME                                            READY   STATUS
# aws-load-balancer-controller-xxxxxxxxx-xxxxx   1/1     Running
# aws-load-balancer-controller-xxxxxxxxx-yyyyy   1/1     Running
```

---

## 4. How AWS Load Balancers Connect to EKS

### Mode 1: ALB as Direct Ingress Controller (Instance or IP Target Mode)

In this mode, the AWS LBC creates an ALB directly from an `Ingress` resource. No NGINX is involved.

```yaml
# ALB Ingress — the ALB IS the Ingress Controller
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: alb-direct-ingress
  namespace: apps
  annotations:
    # This annotation is what tells AWS LBC to handle this Ingress
    kubernetes.io/ingress.class: alb
    # Internet-facing ALB (use "internal" for private ALB)
    alb.ingress.kubernetes.io/scheme: internet-facing
    # IP target mode: ALB routes directly to pod IPs (no NodePort hop)
    # Requires VPC CNI so pods have routable VPC IPs
    alb.ingress.kubernetes.io/target-type: ip
    # ACM certificate ARN for HTTPS
    alb.ingress.kubernetes.io/certificate-arn: arn:aws:acm:eu-west-2:111122223333:certificate/abc-123
    # Redirect HTTP to HTTPS
    alb.ingress.kubernetes.io/actions.ssl-redirect: |
      {"Type":"redirect","RedirectConfig":{"Protocol":"HTTPS","Port":"443","StatusCode":"HTTP_301"}}
    # ALB listen on both 80 and 443
    alb.ingress.kubernetes.io/listen-ports: '[{"HTTP":80},{"HTTPS":443}]'
    # Health check path
    alb.ingress.kubernetes.io/healthcheck-path: /healthz
    # Subnet tags — ALB discovers subnets with this tag
    # Your public subnets need tag: kubernetes.io/role/elb = 1
    # Your private subnets need tag: kubernetes.io/role/internal-elb = 1
spec:
  ingressClassName: alb
  rules:
    - host: app1.yourdomain.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: app1-clusterip-service
                port:
                  number: 80
```

**ALB Target Mode comparison:**

| Mode | How ALB reaches pods | Requires | Pros |
|---|---|---|---|
| `instance` | ALB → Node:NodePort → kube-proxy → Pod | Nothing special | Simple |
| `ip` | ALB → Pod IP directly | VPC CNI, pods with routable IPs | Lower latency, preserves client IP |

### Mode 2: NLB in Front of NGINX (Recommended for Complex Routing)

This is the most flexible architecture. A Network Load Balancer handles the TCP layer and forwards to NGINX, which handles HTTP layer routing:

```
Internet → NLB (TCP:443) → Node:NodePort → NGINX pod → ClusterIP Service → App pod
```

NGINX is provisioned by its own Helm chart, and exposed via an NLB-backed `LoadBalancer` Service.

### Tag Your Subnets (Critical Step)

The AWS LBC discovers subnets by looking for specific tags. Without these tags, it cannot create load balancers.

```bash
# Get your subnet IDs
aws ec2 describe-subnets \
  --filters "Name=vpc-id,Values=$VPC_ID" \
  --query 'Subnets[*].{ID:SubnetId,AZ:AvailabilityZone,Public:MapPublicIpOnLaunch}' \
  --output table

# Tag public subnets (for internet-facing ALB/NLB)
aws ec2 create-tags \
  --resources subnet-public-1a subnet-public-1b subnet-public-1c \
  --tags Key=kubernetes.io/role/elb,Value=1 \
         Key=kubernetes.io/cluster/eks-demo,Value=shared

# Tag private subnets (for internal ALB/NLB)
aws ec2 create-tags \
  --resources subnet-private-1a subnet-private-1b subnet-private-1c \
  --tags Key=kubernetes.io/role/internal-elb,Value=1 \
         Key=kubernetes.io/cluster/eks-demo,Value=shared
```

---

## 5. Install NGINX Ingress Controller on EKS

### Why NGINX on EKS?

The AWS ALB native Ingress is powerful but has limitations compared to NGINX:

- No native support for Lua-based custom rules
- No native sticky sessions by cookie (only by ALB stickiness)
- cert-manager HTTP-01 challenge routing is more complex with ALB
- No native NGINX-specific features (rate limiting, custom headers, rewrite rules)

For most production setups where TLS is terminated at the NGINX level and certificates come from cert-manager, **NGINX in front of an NLB** is the recommended pattern.

### Install NGINX with NLB Backend

```bash
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm repo update

helm install ingress-nginx ingress-nginx/ingress-nginx \
  --namespace ingress-basic \
  --set controller.replicaCount=2 \
  --set controller.nodeSelector."kubernetes\.io/os"=linux \
  --set defaultBackend.nodeSelector."kubernetes\.io/os"=linux \
  --set controller.service.externalTrafficPolicy=Local \
  --set controller.service.type=LoadBalancer \
  --set controller.service.annotations."service\.beta\.kubernetes\.io/aws-load-balancer-type"="external" \
  --set controller.service.annotations."service\.beta\.kubernetes\.io/aws-load-balancer-nlb-target-type"="ip" \
  --set controller.service.annotations."service\.beta\.kubernetes\.io/aws-load-balancer-scheme"="internet-facing" \
  --set controller.service.annotations."service\.beta\.kubernetes\.io/aws-load-balancer-cross-zone-load-balancing-enabled"="true"
```

### NLB Service Annotations Explained

```yaml
# These annotations go on the Service object that NGINX creates
annotations:
  # "external" means: use the new AWS LBC-provisioned NLB
  # (vs "nlb" which uses the legacy in-tree provider)
  service.beta.kubernetes.io/aws-load-balancer-type: "external"

  # "ip" target mode: NLB routes directly to pod IPs
  # Requires VPC CNI — pods must have routable VPC IPs
  service.beta.kubernetes.io/aws-load-balancer-nlb-target-type: "ip"

  # "internet-facing" creates a public NLB with public IPs
  # Use "internal" for a private NLB (VPN/Direct Connect only)
  service.beta.kubernetes.io/aws-load-balancer-scheme: "internet-facing"

  # Distributes traffic across all AZs, not just the one receiving the request
  service.beta.kubernetes.io/aws-load-balancer-cross-zone-load-balancing-enabled: "true"

  # (Optional) Use a static Elastic IP for a predictable IP address
  # service.beta.kubernetes.io/aws-load-balancer-eip-allocations: "eipalloc-xxx,eipalloc-yyy"

  # (Optional) TLS termination at NLB level (before NGINX)
  # service.beta.kubernetes.io/aws-load-balancer-ssl-cert: "arn:aws:acm:..."
  # service.beta.kubernetes.io/aws-load-balancer-ssl-ports: "443"
  # service.beta.kubernetes.io/aws-load-balancer-backend-protocol: "ssl"
```

### Verify NGINX on EKS

```bash
# Wait for the NLB to be provisioned — EXTERNAL-IP will be an AWS DNS name, not an IP
kubectl get service -n ingress-basic -w
# NAME                       TYPE           CLUSTER-IP    EXTERNAL-IP
# ingress-nginx-controller   LoadBalancer   10.100.x.x    xxxxxxxx.elb.eu-west-2.amazonaws.com

# On EKS, EXTERNAL-IP is an NLB DNS hostname, not a static IP
# This hostname resolves to multiple NLB IPs depending on AZ

# Smoke test (replace with your NLB hostname)
NLB_HOST=$(kubectl get service ingress-nginx-controller -n ingress-basic \
  -o jsonpath='{.status.loadBalancer.ingress[0].hostname}')

curl -I http://$NLB_HOST
# HTTP/1.1 404 Not Found
# Server: nginx  ← NGINX is alive
```

> **EKS vs AKS difference:** On AKS, the `EXTERNAL-IP` is a real IP address. On EKS, it is an AWS DNS hostname (`xxx.elb.region.amazonaws.com`). This means your DNS records must use a **CNAME** pointing to the NLB hostname, or you use Route 53 **Alias records** which resolve the hostname automatically.

---

## 6. Deploy Backend Applications

### ServiceAccounts (Required for Vault IRSA)

```yaml
# File: apps/serviceaccounts.yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: app1-sa
  namespace: apps
  annotations:
    # IRSA annotation — maps this K8s SA to an AWS IAM Role
    # Used if your app needs direct AWS API access
    # For Vault auth, Vault uses the K8s SA JWT directly (no IRSA needed)
    eks.amazonaws.com/role-arn: arn:aws:iam::111122223333:role/App1Role
---
apiVersion: v1
kind: ServiceAccount
metadata:
  name: app2-sa
  namespace: apps
```

### Application Deployments

```yaml
# File: apps/app1.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: app1-deployment
  namespace: apps
  labels:
    app: app1
spec:
  replicas: 2
  selector:
    matchLabels:
      app: app1
  template:
    metadata:
      labels:
        app: app1
      annotations:
        # Vault Agent Injector annotations (populated in section 11)
        vault.hashicorp.com/agent-inject: "true"
        vault.hashicorp.com/role: "app1-role"
        vault.hashicorp.com/agent-inject-secret-config: "secret/data/apps/app1"
        vault.hashicorp.com/agent-inject-template-config: |
          {{- with secret "secret/data/apps/app1" -}}
          export DB_HOST="{{ .Data.data.db_host }}"
          export DB_PASSWORD="{{ .Data.data.db_password }}"
          export API_KEY="{{ .Data.data.api_key }}"
          {{- end }}
    spec:
      serviceAccountName: app1-sa
      containers:
        - name: app1
          image: stacksimplify/kube-nginxapp1:1.0.0
          ports:
            - containerPort: 80
          resources:
            requests:
              memory: "64Mi"
              cpu: "50m"
            limits:
              memory: "128Mi"
              cpu: "100m"
          readinessProbe:
            httpGet:
              path: /
              port: 80
            initialDelaySeconds: 5
            periodSeconds: 10
          livenessProbe:
            httpGet:
              path: /
              port: 80
            initialDelaySeconds: 10
            periodSeconds: 15
---
apiVersion: v1
kind: Service
metadata:
  name: app1-clusterip-service
  namespace: apps
spec:
  type: ClusterIP
  selector:
    app: app1
  ports:
    - port: 80
      targetPort: 80
```

```yaml
# File: apps/app2.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: app2-deployment
  namespace: apps
  labels:
    app: app2
spec:
  replicas: 2
  selector:
    matchLabels:
      app: app2
  template:
    metadata:
      labels:
        app: app2
    spec:
      serviceAccountName: app2-sa
      containers:
        - name: app2
          image: stacksimplify/kube-nginxapp2:1.0.0
          ports:
            - containerPort: 80
          resources:
            requests:
              memory: "64Mi"
              cpu: "50m"
---
apiVersion: v1
kind: Service
metadata:
  name: app2-clusterip-service
  namespace: apps
spec:
  type: ClusterIP
  selector:
    app: app2
  ports:
    - port: 80
      targetPort: 80
```

---

## 7. Ingress Routing — Path and Host Based

### Understanding IngressClass on EKS

EKS may have multiple Ingress Controllers running simultaneously:
- `nginx` — handled by NGINX Ingress Controller
- `alb` — handled by AWS Load Balancer Controller

The `ingressClassName` field (or legacy `kubernetes.io/ingress.class` annotation) determines which controller processes a given Ingress resource.

```bash
# Verify which IngressClasses are available
kubectl get ingressclass
# NAME    CONTROLLER                            PARAMETERS   AGE
# alb     ingress.k8s.aws/alb                  <none>       10m
# nginx   k8s.io/ingress-nginx                 <none>       5m
```

### Path Based Routing (NGINX)

```yaml
# File: ingress/path-based-ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: path-based-ingress
  namespace: apps
  annotations:
    kubernetes.io/ingress.class: "nginx"
    nginx.ingress.kubernetes.io/rewrite-target: /$2
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/use-regex: "true"
    # EKS-specific: proxy body size for larger uploads
    nginx.ingress.kubernetes.io/proxy-body-size: "10m"
    # Preserve real client IP (important when behind NLB)
    nginx.ingress.kubernetes.io/use-forwarded-headers: "true"
    nginx.ingress.kubernetes.io/compute-full-forwarded-for: "true"
spec:
  ingressClassName: nginx
  rules:
    - http:
        paths:
          - path: /app1(/|$)(.*)
            pathType: Prefix
            backend:
              service:
                name: app1-clusterip-service
                port:
                  number: 80
          - path: /app2(/|$)(.*)
            pathType: Prefix
            backend:
              service:
                name: app2-clusterip-service
                port:
                  number: 80
```

### Host Based Routing (NGINX)

```yaml
# File: ingress/host-based-ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: host-based-ingress
  namespace: apps
  annotations:
    kubernetes.io/ingress.class: "nginx"
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
spec:
  ingressClassName: nginx
  rules:
    - host: app1.yourdomain.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: app1-clusterip-service
                port:
                  number: 80
    - host: app2.yourdomain.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: app2-clusterip-service
                port:
                  number: 80
```

### Host Based Routing (Native ALB via AWS LBC)

```yaml
# File: ingress/alb-host-based-ingress.yaml
# This provisions an ALB directly — no NGINX involved
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: alb-host-ingress
  namespace: apps
  annotations:
    kubernetes.io/ingress.class: alb
    alb.ingress.kubernetes.io/scheme: internet-facing
    alb.ingress.kubernetes.io/target-type: ip
    alb.ingress.kubernetes.io/listen-ports: '[{"HTTP": 80}, {"HTTPS": 443}]'
    alb.ingress.kubernetes.io/certificate-arn: arn:aws:acm:eu-west-2:111122223333:certificate/abc
    alb.ingress.kubernetes.io/ssl-redirect: "443"
    # Group multiple Ingress resources onto a single ALB (cost saving)
    alb.ingress.kubernetes.io/group.name: production
spec:
  ingressClassName: alb
  rules:
    - host: app1.yourdomain.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: app1-clusterip-service
                port:
                  number: 80
    - host: app2.yourdomain.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: app2-clusterip-service
                port:
                  number: 80
```

---

## 8. TLS Option A — AWS Certificate Manager (ACM)

### What Is ACM?

AWS Certificate Manager (ACM) is an AWS-managed service that provisions, manages, and renews TLS certificates automatically. ACM certificates are **free** and **auto-renewed**. However, they can only be used with AWS load balancers (ALB, NLB, CloudFront) — you cannot export the private key or use them inside Kubernetes Secrets for NGINX.

This means:
- If TLS terminates at the ALB → use ACM ✅
- If TLS terminates at NGINX → use cert-manager ✅ (ACM cannot be used here)

### Request an ACM Certificate

```bash
# Option 1: DNS validation (recommended — fully automated with Route 53)
aws acm request-certificate \
  --domain-name yourdomain.com \
  --subject-alternative-names "*.yourdomain.com" \
  --validation-method DNS \
  --region eu-west-2

# Note the CertificateArn from the output
CERT_ARN=$(aws acm list-certificates \
  --region eu-west-2 \
  --query 'CertificateSummaryList[?DomainName==`yourdomain.com`].CertificateArn' \
  --output text)

# Get the DNS validation record to add to Route 53
aws acm describe-certificate \
  --certificate-arn $CERT_ARN \
  --region eu-west-2 \
  --query 'Certificate.DomainValidationOptions[0].ResourceRecord'
# {
#   "Name": "_abc123.yourdomain.com.",
#   "Type": "CNAME",
#   "Value": "_def456.acm-validations.aws."
# }

# Add the CNAME record to Route 53 (ACM validates automatically once added)
# Then wait for Status to become "ISSUED"
aws acm describe-certificate \
  --certificate-arn $CERT_ARN \
  --region eu-west-2 \
  --query 'Certificate.Status'
# "ISSUED"
```

### Use ACM Certificate on an ALB Ingress

```yaml
# File: ingress/acm-alb-ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: acm-ingress
  namespace: apps
  annotations:
    kubernetes.io/ingress.class: alb
    alb.ingress.kubernetes.io/scheme: internet-facing
    alb.ingress.kubernetes.io/target-type: ip
    alb.ingress.kubernetes.io/listen-ports: '[{"HTTP": 80}, {"HTTPS": 443}]'
    # This is where ACM plugs in — the certificate ARN
    alb.ingress.kubernetes.io/certificate-arn: arn:aws:acm:eu-west-2:111122223333:certificate/abc-123
    # Redirect all HTTP traffic to HTTPS
    alb.ingress.kubernetes.io/ssl-redirect: "443"
    # ALB will use the ACM cert to terminate TLS before forwarding to pods
    # Pods receive plain HTTP on port 80
    alb.ingress.kubernetes.io/backend-protocol: HTTP
    alb.ingress.kubernetes.io/healthcheck-path: /healthz
    alb.ingress.kubernetes.io/healthcheck-interval-seconds: "30"
spec:
  ingressClassName: alb
  rules:
    - host: app1.yourdomain.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: app1-clusterip-service
                port:
                  number: 80
```

### Use ACM Certificate on an NLB Service (TLS Pass-Through to NGINX)

```yaml
# File: ingress/nginx-nlb-acm-service.yaml
# This configures the NLB to terminate TLS using ACM
# NGINX receives decrypted HTTP on port 80
apiVersion: v1
kind: Service
metadata:
  name: ingress-nginx-controller
  namespace: ingress-basic
  annotations:
    service.beta.kubernetes.io/aws-load-balancer-type: "external"
    service.beta.kubernetes.io/aws-load-balancer-nlb-target-type: "ip"
    service.beta.kubernetes.io/aws-load-balancer-scheme: "internet-facing"
    # NLB-level TLS termination using ACM
    service.beta.kubernetes.io/aws-load-balancer-ssl-cert: arn:aws:acm:eu-west-2:111122223333:certificate/abc-123
    # NLB only terminates TLS on port 443; port 80 passes through
    service.beta.kubernetes.io/aws-load-balancer-ssl-ports: "443"
    # NLB decrypts and forwards plain HTTP to NGINX
    service.beta.kubernetes.io/aws-load-balancer-backend-protocol: "http"
```

---

## 9. TLS Option B — cert-manager with Let's Encrypt

When NGINX terminates TLS (the most flexible option), cert-manager handles certificate issuance. The flow is identical to AKS except for DNS-01 challenge configuration, which uses Route 53 instead of Azure DNS.

### Install cert-manager

```bash
helm repo add jetstack https://charts.jetstack.io
helm repo update

helm install cert-manager jetstack/cert-manager \
  --namespace cert-manager \
  --version v1.14.0 \
  --set installCRDs=true \
  --set global.leaderElection.namespace=cert-manager

kubectl get pods -n cert-manager
# All 3 pods should be 1/1 Running
```

### IRSA for cert-manager (DNS-01 Challenge with Route 53)

The HTTP-01 challenge requires no AWS permissions. But the **DNS-01 challenge** (needed for wildcard certificates) requires cert-manager to create DNS records in Route 53.

```bash
# Create IAM policy for Route 53 DNS-01 challenge
cat > cert-manager-route53-policy.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "route53:GetChange",
      "Resource": "arn:aws:route53:::change/*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "route53:ChangeResourceRecordSets",
        "route53:ListResourceRecordSets"
      ],
      "Resource": "arn:aws:route53:::hostedzone/*"
    },
    {
      "Effect": "Allow",
      "Action": "route53:ListHostedZonesByName",
      "Resource": "*"
    }
  ]
}
EOF

aws iam create-policy \
  --policy-name CertManagerRoute53Policy \
  --policy-document file://cert-manager-route53-policy.json

# Create IRSA for cert-manager
eksctl create iamserviceaccount \
  --cluster=$CLUSTER_NAME \
  --namespace=cert-manager \
  --name=cert-manager \
  --role-name=CertManagerRole \
  --attach-policy-arn=arn:aws:iam::${ACCOUNT_ID}:policy/CertManagerRoute53Policy \
  --approve \
  --override-existing-serviceaccounts \
  --region=$REGION
```

### ClusterIssuer — HTTP-01 (No AWS Permissions Needed)

```yaml
# File: cert-manager/cluster-issuer-http01.yaml
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-production
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: your-email@yourdomain.com
    privateKeySecretRef:
      name: letsencrypt-production-account-key
    solvers:
      - http01:
          ingress:
            class: nginx
```

### ClusterIssuer — DNS-01 with Route 53 (For Wildcard Certificates)

```yaml
# File: cert-manager/cluster-issuer-dns01.yaml
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-production-dns
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: your-email@yourdomain.com
    privateKeySecretRef:
      name: letsencrypt-dns-account-key
    solvers:
      - dns01:
          route53:
            region: eu-west-2
            # The hosted zone ID for your domain in Route 53
            hostedZoneID: Z1234567890ABCDEF
            # cert-manager uses IRSA — the ServiceAccount has the IAM role attached
            # No access key needed; the IRSA annotation handles authentication
```

### TLS Ingress with cert-manager

```yaml
# File: ingress/tls-ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: tls-ingress
  namespace: apps
  annotations:
    kubernetes.io/ingress.class: "nginx"
    cert-manager.io/cluster-issuer: "letsencrypt-production"
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/force-ssl-redirect: "true"
spec:
  ingressClassName: nginx
  tls:
    - hosts:
        - app1.yourdomain.com
      secretName: app1-tls-secret
    - hosts:
        - app2.yourdomain.com
      secretName: app2-tls-secret
  rules:
    - host: app1.yourdomain.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: app1-clusterip-service
                port:
                  number: 80
    - host: app2.yourdomain.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: app2-clusterip-service
                port:
                  number: 80
```

### How ACME HTTP-01 Challenge Works on EKS

```
1. cert-manager creates a temporary pod serving the ACME token
2. cert-manager creates a temporary Ingress rule:
   path: /.well-known/acme-challenge/<token>
   backend: cm-acme-http-solver pod

3. Let's Encrypt makes HTTP GET to:
   http://app1.yourdomain.com/.well-known/acme-challenge/<token>
   Path:  DNS → Route 53 → NLB DNS → NLB → NGINX → cm-acme-http-solver pod

4. Important: NLB DNS name must resolve BEFORE the challenge runs
   (Let's Encrypt cannot reach an NLB that doesn't exist yet)

5. cert-manager gets confirmation → issues certificate
6. Certificate and private key stored in Secret app1-tls-secret
7. NGINX loads the Secret → serves HTTPS
```

---

## 10. HashiCorp Vault on EKS

### Deploy Vault with Persistent Storage (EBS)

On EKS, Vault uses EBS volumes for persistent storage. The EBS CSI driver must be installed (configured in the cluster setup).

```yaml
# File: vault/vault-values.yaml
# Helm values for Vault HA on EKS
global:
  enabled: true

injector:
  enabled: true
  replicas: 2
  # Affinity to spread injector pods across AZs
  affinity:
    podAntiAffinity:
      requiredDuringSchedulingIgnoredDuringExecution:
        - labelSelector:
            matchExpressions:
              - key: app.kubernetes.io/name
                operator: In
                values:
                  - vault-agent-injector
          topologyKey: topology.kubernetes.io/zone

server:
  ha:
    enabled: true
    replicas: 3
    raft:
      enabled: true
      setNodeId: true
      config: |
        ui = true

        listener "tcp" {
          address     = "[::]:8200"
          tls_disable = 1
        }

        storage "raft" {
          path    = "/vault/data"
          retry_join {
            leader_api_addr = "http://vault-0.vault-internal:8200"
          }
          retry_join {
            leader_api_addr = "http://vault-1.vault-internal:8200"
          }
          retry_join {
            leader_api_addr = "http://vault-2.vault-internal:8200"
          }
        }

        service_registration "kubernetes" {}

  # EBS volume for Vault data
  dataStorage:
    enabled: true
    size: 10Gi
    storageClass: gp2   # EBS gp2 storage class (available in EKS by default)
    accessMode: ReadWriteOnce

  # Spread Vault pods across availability zones
  affinity:
    podAntiAffinity:
      requiredDuringSchedulingIgnoredDuringExecution:
        - labelSelector:
            matchExpressions:
              - key: app.kubernetes.io/name
                operator: In
                values:
                  - vault
          topologyKey: topology.kubernetes.io/zone

  # Vault UI service
  ui:
    enabled: true
    serviceType: ClusterIP
```

```bash
helm install vault hashicorp/vault \
  --namespace vault \
  --values vault/vault-values.yaml

# Wait for pods to start
kubectl get pods -n vault -w
```

### Initialise and Unseal Vault

```bash
# Initialise (run once per cluster)
kubectl exec -n vault vault-0 -- vault operator init \
  -key-shares=5 \
  -key-threshold=3 \
  -format=json > vault-init.json

# Store these securely! Consider AWS Secrets Manager or KMS-encrypted S3
VAULT_ROOT_TOKEN=$(cat vault-init.json | jq -r '.root_token')
UNSEAL_KEY_1=$(cat vault-init.json | jq -r '.unseal_keys_b64[0]')
UNSEAL_KEY_2=$(cat vault-init.json | jq -r '.unseal_keys_b64[1]')
UNSEAL_KEY_3=$(cat vault-init.json | jq -r '.unseal_keys_b64[2]')

# Unseal vault-0
kubectl exec -n vault vault-0 -- vault operator unseal $UNSEAL_KEY_1
kubectl exec -n vault vault-0 -- vault operator unseal $UNSEAL_KEY_2
kubectl exec -n vault vault-0 -- vault operator unseal $UNSEAL_KEY_3

# Join and unseal vault-1
kubectl exec -n vault vault-1 -- vault operator raft join http://vault-0.vault-internal:8200
kubectl exec -n vault vault-1 -- vault operator unseal $UNSEAL_KEY_1
kubectl exec -n vault vault-1 -- vault operator unseal $UNSEAL_KEY_2
kubectl exec -n vault vault-1 -- vault operator unseal $UNSEAL_KEY_3

# Join and unseal vault-2
kubectl exec -n vault vault-2 -- vault operator raft join http://vault-0.vault-internal:8200
kubectl exec -n vault vault-2 -- vault operator unseal $UNSEAL_KEY_1
kubectl exec -n vault vault-2 -- vault operator unseal $UNSEAL_KEY_2
kubectl exec -n vault vault-2 -- vault operator unseal $UNSEAL_KEY_3

# Verify cluster health
kubectl exec -n vault vault-0 -- vault operator raft list-peers
```

### Auto-Unseal with AWS KMS (Production Recommendation)

In production, you should not manually unseal Vault on every restart. AWS KMS auto-unseal solves this:

```bash
# Create a KMS key for Vault auto-unseal
KMS_KEY_ID=$(aws kms create-key \
  --description "Vault auto-unseal key" \
  --region $REGION \
  --query 'KeyMetadata.KeyId' \
  --output text)

# Create alias for easier reference
aws kms create-alias \
  --alias-name alias/vault-unseal \
  --target-key-id $KMS_KEY_ID \
  --region $REGION
```

```yaml
# vault-values-autounseal.yaml — update the Vault config section
server:
  ha:
    config: |
      ui = true

      listener "tcp" {
        address     = "[::]:8200"
        tls_disable = 1
      }

      # AWS KMS auto-unseal — Vault unseals itself using KMS on every restart
      seal "awskms" {
        region     = "eu-west-2"
        kms_key_id = "alias/vault-unseal"
        # Uses IRSA — no access key needed if Vault ServiceAccount has IAM role
      }

      storage "raft" {
        path = "/vault/data"
        # ... retry_join blocks as before
      }
```

```bash
# Create IRSA for Vault to access KMS
cat > vault-kms-policy.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "kms:Encrypt",
        "kms:Decrypt",
        "kms:DescribeKey"
      ],
      "Resource": "arn:aws:kms:${REGION}:${ACCOUNT_ID}:key/${KMS_KEY_ID}"
    }
  ]
}
EOF

aws iam create-policy \
  --policy-name VaultKMSPolicy \
  --policy-document file://vault-kms-policy.json

eksctl create iamserviceaccount \
  --cluster=$CLUSTER_NAME \
  --namespace=vault \
  --name=vault \
  --role-name=VaultRole \
  --attach-policy-arn=arn:aws:iam::${ACCOUNT_ID}:policy/VaultKMSPolicy \
  --approve \
  --region=$REGION
```

### Configure Vault Kubernetes Auth Method

```bash
# Port-forward for local access
kubectl port-forward -n vault svc/vault 8200:8200 &
export VAULT_ADDR=http://127.0.0.1:8200
export VAULT_TOKEN=$VAULT_ROOT_TOKEN

# Enable Kubernetes auth
vault auth enable kubernetes

# Get EKS cluster API server URL
K8S_HOST=$(kubectl config view --raw -o jsonpath='{.clusters[0].cluster.server}')

# Configure Kubernetes auth
# On EKS, the issuer is the OIDC provider URL
OIDC_ISSUER=$(aws eks describe-cluster \
  --name $CLUSTER_NAME \
  --region $REGION \
  --query "cluster.identity.oidc.issuer" \
  --output text)

vault write auth/kubernetes/config \
  kubernetes_host="$K8S_HOST" \
  kubernetes_ca_cert=@<(kubectl config view --raw \
    -o jsonpath='{.clusters[0].cluster.certificate-authority-data}' | base64 -d) \
  issuer="$OIDC_ISSUER"

# Enable KV v2 secrets engine
vault secrets enable -path=secret kv-v2

# Write application secrets
vault kv put secret/apps/app1 \
  db_host="mydb.cluster-abc.eu-west-2.rds.amazonaws.com:5432" \
  db_name="app1db" \
  db_password="supersecret123" \
  api_key="sk-live-abcdef1234567890"

vault kv put secret/apps/app2 \
  redis_host="mycluster.abc.ng.0001.euw2.cache.amazonaws.com" \
  redis_password="redispassword123"

# Create Vault policies
vault policy write app1-policy - <<EOF
path "secret/data/apps/app1" {
  capabilities = ["read"]
}
path "secret/metadata/apps/app1" {
  capabilities = ["list"]
}
EOF

vault policy write app2-policy - <<EOF
path "secret/data/apps/app2" {
  capabilities = ["read"]
}
path "secret/metadata/apps/app2" {
  capabilities = ["list"]
}
EOF

vault policy write cert-manager-policy - <<EOF
path "pki_int/sign/yourdomain-com" {
  capabilities = ["create", "update"]
}
path "pki_int/issue/yourdomain-com" {
  capabilities = ["create", "update"]
}
EOF

# Create Kubernetes auth roles
vault write auth/kubernetes/role/app1-role \
  bound_service_account_names=app1-sa \
  bound_service_account_namespaces=apps \
  policies=app1-policy \
  ttl=1h

vault write auth/kubernetes/role/app2-role \
  bound_service_account_names=app2-sa \
  bound_service_account_namespaces=apps \
  policies=app2-policy \
  ttl=1h

vault write auth/kubernetes/role/cert-manager-role \
  bound_service_account_names=cert-manager \
  bound_service_account_namespaces=cert-manager \
  policies=cert-manager-policy \
  ttl=20m
```

---

## 11. Vault Agent Injector with EKS Workloads

### How the Vault Agent Injector Works on EKS

The Vault Agent Injector is a **Mutating Admission Webhook** deployed as part of the Vault Helm chart. When a pod is created:

```
1. kubectl apply → Kubernetes API server
   ↓
2. API server sends AdmissionReview webhook to:
   vault-agent-injector.vault.svc:443
   ↓
3. Injector checks for vault.hashicorp.com/agent-inject: "true" annotation
   ↓
4. Injector patches the pod spec to add:
   ├── Init container: vault-agent-init
   │     (runs BEFORE the app container)
   │     (authenticates to Vault, writes secrets to shared volume, exits)
   ├── Sidecar container: vault-agent
   │     (keeps running, refreshes secrets before TTL expires)
   └── Volume: /vault/secrets (tmpfs — in-memory, never hits disk)
   ↓
5. Pod starts:
   a. vault-agent-init authenticates using the pod's K8s ServiceAccount JWT
      POST http://vault.vault.svc.cluster.local:8200/v1/auth/kubernetes/login
      { "jwt": "<ServiceAccount JWT>", "role": "app1-role" }
   b. Vault validates the JWT against the EKS OIDC provider
   c. Vault returns a Vault token with app1-policy attached
   d. vault-agent-init reads secret/data/apps/app1
   e. Renders the template → writes to /vault/secrets/config
   f. Exits 0
   g. App container starts and reads /vault/secrets/config
   h. vault-agent sidecar stays running and refreshes on expiry
```

### Complete Annotated Deployment Example

```yaml
# File: apps/app1-with-vault.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: app1-deployment
  namespace: apps
spec:
  replicas: 2
  selector:
    matchLabels:
      app: app1
  template:
    metadata:
      labels:
        app: app1
      annotations:
        # ── Core injection settings ──────────────────────────────────────
        # Enable the injector
        vault.hashicorp.com/agent-inject: "true"

        # Vault address — use internal cluster DNS
        vault.hashicorp.com/address: "http://vault.vault.svc.cluster.local:8200"

        # The Vault role to authenticate as
        vault.hashicorp.com/role: "app1-role"

        # ── Secret injection ─────────────────────────────────────────────
        # Injects secret at /vault/secrets/db-config
        vault.hashicorp.com/agent-inject-secret-db-config: "secret/data/apps/app1"

        # Template for the secret file format
        vault.hashicorp.com/agent-inject-template-db-config: |
          {{- with secret "secret/data/apps/app1" -}}
          # Database configuration
          DB_HOST={{ .Data.data.db_host }}
          DB_NAME={{ .Data.data.db_name }}
          DB_PASSWORD={{ .Data.data.db_password }}
          API_KEY={{ .Data.data.api_key }}
          {{- end }}

        # ── Sidecar lifecycle settings ────────────────────────────────────
        # Run vault-agent-init as init container first, then vault-agent as sidecar
        vault.hashicorp.com/agent-inject-init-first: "true"

        # Keep sidecar running for dynamic refresh (false = init-only mode)
        vault.hashicorp.com/agent-pre-populate-only: "false"

        # Log level for vault-agent
        vault.hashicorp.com/log-level: "info"

        # Resource limits for vault-agent containers
        vault.hashicorp.com/agent-requests-cpu: "50m"
        vault.hashicorp.com/agent-requests-mem: "64Mi"
        vault.hashicorp.com/agent-limits-cpu: "100m"
        vault.hashicorp.com/agent-limits-mem: "128Mi"

    spec:
      serviceAccountName: app1-sa
      containers:
        - name: app1
          image: stacksimplify/kube-nginxapp1:1.0.0
          ports:
            - containerPort: 80
          # The secret file is available before the app container starts
          # because vault-agent-init runs first as an init container
          volumeMounts:
            # /vault/secrets is automatically mounted by the injector
            # No explicit volumeMount needed — it's injected automatically
          env:
            # You can also source the file to get env vars
            - name: VAULT_SECRETS_PATH
              value: /vault/secrets/db-config
```

### Verify Injection on EKS

```bash
kubectl apply -f apps/serviceaccounts.yaml
kubectl apply -f apps/app1-with-vault.yaml

# Pod should have 3 containers: vault-agent-init (init), app1, vault-agent
kubectl get pods -n apps
kubectl describe pod -n apps -l app=app1

# Check containers list
kubectl get pod -n apps -l app=app1 \
  -o jsonpath='{.items[0].spec.initContainers[*].name}{"\n"}{.items[0].spec.containers[*].name}'
# vault-agent-init
# app1 vault-agent

# Verify the secret was written
kubectl exec -n apps deploy/app1-deployment -c app1 -- cat /vault/secrets/db-config
# DB_HOST=mydb.cluster-abc.eu-west-2.rds.amazonaws.com:5432
# DB_NAME=app1db
# DB_PASSWORD=supersecret123
# API_KEY=sk-live-abcdef1234567890

# Check vault-agent-init logs (should show successful auth and secret fetch)
kubectl logs -n apps -l app=app1 -c vault-agent-init

# Check vault-agent sidecar logs
kubectl logs -n apps -l app=app1 -c vault-agent
```

---

## 12. cert-manager with Vault PKI Backend

### Configure Vault PKI

```bash
# Enable Root PKI
vault secrets enable pki
vault secrets tune -max-lease-ttl=87600h pki

# Generate Root CA
vault write -field=certificate pki/root/generate/internal \
  common_name="Your Org Root CA" \
  issuer_name="root-2024" \
  ttl=87600h > root_ca.crt

# Configure Root CA URLs
vault write pki/config/urls \
  issuing_certificates="http://vault.vault.svc.cluster.local:8200/v1/pki/ca" \
  crl_distribution_points="http://vault.vault.svc.cluster.local:8200/v1/pki/crl"

# Enable Intermediate PKI (best practice — never issue directly from root CA)
vault secrets enable -path=pki_int pki
vault secrets tune -max-lease-ttl=26280h pki_int

# Generate intermediate CSR
vault write -format=json pki_int/intermediate/generate/internal \
  common_name="Your Org Intermediate CA" \
  issuer_name="intermediate-2024" \
  | jq -r '.data.csr' > intermediate.csr

# Sign intermediate with root CA
vault write -format=json pki/root/sign-intermediate \
  issuer_ref="root-2024" \
  csr=@intermediate.csr \
  format=pem_bundle \
  ttl=26280h \
  | jq -r '.data.certificate' > intermediate.cert.pem

# Import signed intermediate certificate
vault write pki_int/intermediate/set-signed \
  certificate=@intermediate.cert.pem

# Configure intermediate CA URLs
vault write pki_int/config/urls \
  issuing_certificates="http://vault.vault.svc.cluster.local:8200/v1/pki_int/ca" \
  crl_distribution_points="http://vault.vault.svc.cluster.local:8200/v1/pki_int/crl"

# Create a PKI role for your domain
vault write pki_int/roles/yourdomain-com \
  issuer_ref="intermediate-2024" \
  allowed_domains="yourdomain.com,svc.cluster.local" \
  allow_subdomains=true \
  allow_wildcard_certificates=true \
  max_ttl=720h \
  key_type=rsa \
  key_bits=2048 \
  require_cn=false
```

### Create Vault ClusterIssuer for cert-manager

```yaml
# File: cert-manager/vault-cluster-issuer.yaml
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: vault-issuer
spec:
  vault:
    # Internal cluster DNS for Vault
    server: http://vault.vault.svc.cluster.local:8200
    # PKI signing path
    path: pki_int/sign/yourdomain-com
    auth:
      kubernetes:
        role: cert-manager-role
        mountPath: /v1/auth/kubernetes
        serviceAccountRef:
          name: cert-manager
```

```bash
kubectl apply -f cert-manager/vault-cluster-issuer.yaml

kubectl get clusterissuer vault-issuer
# NAME           READY   AGE
# vault-issuer   True    30s
```

### TLS Ingress Using Vault PKI

```yaml
# File: ingress/vault-tls-ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: vault-tls-ingress
  namespace: apps
  annotations:
    kubernetes.io/ingress.class: "nginx"
    cert-manager.io/cluster-issuer: "vault-issuer"
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
spec:
  ingressClassName: nginx
  tls:
    - hosts:
        - app1.yourdomain.com
      secretName: app1-vault-tls-secret
  rules:
    - host: app1.yourdomain.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: app1-clusterip-service
                port:
                  number: 80
```

### Direct Certificate Resource

```yaml
# File: cert-manager/app1-certificate.yaml
apiVersion: cert-manager.io/v1
kind: Certificate
metadata:
  name: app1-certificate
  namespace: apps
spec:
  secretName: app1-vault-tls-secret
  duration: 720h
  renewBefore: 168h
  subject:
    organizations:
      - "Your Organisation"
  isCA: false
  privateKey:
    algorithm: RSA
    encoding: PKCS1
    size: 2048
  dnsNames:
    - app1.yourdomain.com
  issuerRef:
    name: vault-issuer
    kind: ClusterIssuer
    group: cert-manager.io
```

```bash
kubectl apply -f cert-manager/app1-certificate.yaml

# Watch certificate issuance
kubectl get certificate -n apps -w
# NAME               READY   SECRET                 AGE
# app1-certificate   False   app1-vault-tls-secret  10s
# app1-certificate   True    app1-vault-tls-secret  20s

# Verify the certificate contents
kubectl get secret app1-vault-tls-secret -n apps \
  -o jsonpath='{.data.tls\.crt}' | base64 -d | \
  openssl x509 -text -noout | grep -E "Subject:|DNS:|Not After|Issuer"
```

---

## 13. ExternalDNS on EKS with Route 53

ExternalDNS watches Ingress and Service resources and automatically creates/updates Route 53 DNS records. On EKS, it authenticates to Route 53 via IRSA.

### Create IRSA for ExternalDNS

```bash
# IAM policy for Route 53 record management
cat > externaldns-policy.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "route53:ChangeResourceRecordSets"
      ],
      "Resource": [
        "arn:aws:route53:::hostedzone/*"
      ]
    },
    {
      "Effect": "Allow",
      "Action": [
        "route53:ListHostedZones",
        "route53:ListResourceRecordSets",
        "route53:ListTagsForResource"
      ],
      "Resource": ["*"]
    }
  ]
}
EOF

aws iam create-policy \
  --policy-name ExternalDNSPolicy \
  --policy-document file://externaldns-policy.json

eksctl create iamserviceaccount \
  --cluster=$CLUSTER_NAME \
  --namespace=external-dns \
  --name=external-dns \
  --role-name=ExternalDNSRole \
  --attach-policy-arn=arn:aws:iam::${ACCOUNT_ID}:policy/ExternalDNSPolicy \
  --approve \
  --region=$REGION
```

### Deploy ExternalDNS

```yaml
# File: external-dns/externaldns-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: external-dns
  namespace: external-dns
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
      serviceAccountName: external-dns   # Has IRSA annotation → AWS credentials
      containers:
        - name: external-dns
          image: registry.k8s.io/external-dns/external-dns:v0.14.0
          args:
            # Watch both Ingress and Service resources
            - --source=service
            - --source=ingress
            # Only manage records in your hosted zone
            - --domain-filter=yourdomain.com
            # AWS Route 53 provider
            - --provider=aws
            # AWS region
            - --aws-region=eu-west-2
            # Route 53 hosted zone ID (optional, improves performance)
            - --aws-zone-id=Z1234567890ABCDEF
            # Only create records, never delete (safer for production)
            # Remove this to also delete records when Ingress is deleted
            - --policy=upsert-only
            # TXT records for ownership tracking
            - --registry=txt
            - --txt-owner-id=eks-demo
            - --txt-prefix=externaldns-
          env:
            - name: AWS_DEFAULT_REGION
              value: eu-west-2
          resources:
            requests:
              memory: "50Mi"
              cpu: "50m"
            limits:
              memory: "100Mi"
              cpu: "100m"
---
apiVersion: v1
kind: ServiceAccount
metadata:
  name: external-dns
  namespace: external-dns
  annotations:
    # IRSA annotation — populated by eksctl iamserviceaccount command
    eks.amazonaws.com/role-arn: arn:aws:iam::111122223333:role/ExternalDNSRole
---
# RBAC for ExternalDNS to read Ingress and Service resources
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
  name: external-dns
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: external-dns
subjects:
  - kind: ServiceAccount
    name: external-dns
    namespace: external-dns
```

```bash
kubectl apply -f external-dns/

# Watch ExternalDNS logs — it should detect Ingress resources and create records
kubectl logs -n external-dns deploy/external-dns -f
# time="2024-01-01T00:00:00Z" level=info msg="Updating A record named 'app1' to '...' for Route53 zone 'yourdomain.com'."

# Verify records were created in Route 53
aws route53 list-resource-record-sets \
  --hosted-zone-id Z1234567890ABCDEF \
  --query "ResourceRecordSets[?Name=='app1.yourdomain.com.']"
```

### ExternalDNS with NLB (CNAME vs Alias)

On EKS, the NLB EXTERNAL-IP is a DNS hostname, not an IP. ExternalDNS handles this automatically by creating Route 53 **Alias records** which point to the NLB hostname at zero cost (no extra DNS lookup).

```
NGINX Service EXTERNAL-IP: xxxx.elb.eu-west-2.amazonaws.com
ExternalDNS creates:
  app1.yourdomain.com → ALIAS → xxxx.elb.eu-west-2.amazonaws.com
  app2.yourdomain.com → ALIAS → xxxx.elb.eu-west-2.amazonaws.com
  (both point to the same NLB, NGINX routes internally)
```

---

## 14. Network Policies on EKS

### CNI Considerations

Network Policies on EKS require a CNI plugin that supports them:

| CNI | Network Policy Support | Notes |
|---|---|---|
| VPC CNI (default) | Limited — requires separate policy engine | Install Calico as policy engine alongside VPC CNI |
| Calico (full install) | Full support | Best for fine-grained policy |
| Cilium | Full support + L7 | Most advanced, eBPF-based |

For most EKS setups, VPC CNI with Calico for policy enforcement is standard.

```bash
# Install Calico for network policy enforcement (policy engine only, not CNI)
kubectl apply -f https://raw.githubusercontent.com/aws/amazon-vpc-cni-k8s/master/config/master/calico-operator.yaml
kubectl apply -f https://raw.githubusercontent.com/aws/amazon-vpc-cni-k8s/master/config/master/calico-crs.yaml
```

### Default Deny All

```yaml
# File: network-policies/default-deny.yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-all
  namespace: apps
spec:
  podSelector: {}
  policyTypes:
    - Ingress
    - Egress
```

### Allow NGINX → Apps

```yaml
# File: network-policies/allow-nginx-to-apps.yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-ingress-controller
  namespace: apps
spec:
  podSelector:
    matchLabels:
      app: app1
  policyTypes:
    - Ingress
  ingress:
    - from:
        - namespaceSelector:
            matchLabels:
              kubernetes.io/metadata.name: ingress-basic
          podSelector:
            matchLabels:
              app.kubernetes.io/name: ingress-nginx
      ports:
        - protocol: TCP
          port: 80
```

### Allow Apps → Vault

```yaml
# File: network-policies/allow-apps-to-vault.yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-egress-to-vault
  namespace: apps
spec:
  podSelector:
    matchLabels:
      app: app1
  policyTypes:
    - Egress
  egress:
    - to:
        - namespaceSelector:
            matchLabels:
              kubernetes.io/metadata.name: vault
          podSelector:
            matchLabels:
              app.kubernetes.io/name: vault
      ports:
        - protocol: TCP
          port: 8200
```

### Allow DNS Egress (Essential)

```yaml
# File: network-policies/allow-dns.yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-dns-egress
  namespace: apps
spec:
  podSelector: {}
  policyTypes:
    - Egress
  egress:
    - ports:
        - protocol: UDP
          port: 53
        - protocol: TCP
          port: 53
```

### Allow Vault Agent Injector Webhook

The Vault Agent Injector is a mutating webhook — the API server must reach it:

```yaml
# File: network-policies/allow-vault-injector-webhook.yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-webhook-ingress
  namespace: vault
spec:
  podSelector:
    matchLabels:
      app.kubernetes.io/name: vault-agent-injector
  policyTypes:
    - Ingress
  ingress:
    - ports:
        - protocol: TCP
          port: 8080   # vault-agent-injector listens on 8080
```

### Allow cert-manager → Vault

```yaml
# File: network-policies/allow-cert-manager-to-vault.yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-cert-manager-to-vault
  namespace: cert-manager
spec:
  podSelector:
    matchLabels:
      app: cert-manager
  policyTypes:
    - Egress
  egress:
    - to:
        - namespaceSelector:
            matchLabels:
              kubernetes.io/metadata.name: vault
      ports:
        - protocol: TCP
          port: 8200
```

---

## 15. Full End-to-End Deployment Walkthrough

### Phase 1: EKS Cluster and Foundations

```bash
# Create cluster
eksctl create cluster -f cluster/eks-cluster.yaml
aws eks get-credentials --region $REGION --name $CLUSTER_NAME

# Create and label namespaces
for ns in ingress-basic cert-manager vault apps external-dns; do
  kubectl create namespace $ns
  kubectl label namespace $ns kubernetes.io/metadata.name=$ns
done

# Tag subnets
aws ec2 create-tags \
  --resources <PUBLIC_SUBNET_IDS> \
  --tags Key=kubernetes.io/role/elb,Value=1 \
         Key=kubernetes.io/cluster/eks-demo,Value=shared

aws ec2 create-tags \
  --resources <PRIVATE_SUBNET_IDS> \
  --tags Key=kubernetes.io/role/internal-elb,Value=1 \
         Key=kubernetes.io/cluster/eks-demo,Value=shared

# Checkpoint
kubectl get nodes
# All nodes Ready
```

### Phase 2: AWS Load Balancer Controller

```bash
# IAM policy
aws iam create-policy \
  --policy-name AWSLoadBalancerControllerIAMPolicy \
  --policy-document file://iam_policy.json

# IRSA
eksctl create iamserviceaccount \
  --cluster=$CLUSTER_NAME \
  --namespace=kube-system \
  --name=aws-load-balancer-controller \
  --role-name=AWSLoadBalancerControllerRole \
  --attach-policy-arn=arn:aws:iam::${ACCOUNT_ID}:policy/AWSLoadBalancerControllerIAMPolicy \
  --approve \
  --region=$REGION

# Helm install
helm install aws-load-balancer-controller eks/aws-load-balancer-controller \
  --namespace kube-system \
  --set clusterName=$CLUSTER_NAME \
  --set serviceAccount.create=false \
  --set serviceAccount.name=aws-load-balancer-controller \
  --set region=$REGION \
  --set vpcId=$VPC_ID

# Checkpoint
kubectl get pods -n kube-system -l app.kubernetes.io/name=aws-load-balancer-controller
# Both pods Running
```

### Phase 3: NGINX Ingress Controller + NLB

```bash
helm install ingress-nginx ingress-nginx/ingress-nginx \
  --namespace ingress-basic \
  --set controller.replicaCount=2 \
  --set controller.service.externalTrafficPolicy=Local \
  --set controller.service.annotations."service\.beta\.kubernetes\.io/aws-load-balancer-type"="external" \
  --set controller.service.annotations."service\.beta\.kubernetes\.io/aws-load-balancer-nlb-target-type"="ip" \
  --set controller.service.annotations."service\.beta\.kubernetes\.io/aws-load-balancer-scheme"="internet-facing"

# Checkpoint — wait for EXTERNAL-IP (NLB hostname)
kubectl get service -n ingress-basic -w
NLB_HOST=$(kubectl get service ingress-nginx-controller -n ingress-basic \
  -o jsonpath='{.status.loadBalancer.ingress[0].hostname}')
curl -I http://$NLB_HOST
# HTTP/1.1 404 Not Found  ← NGINX alive
```

### Phase 4: Vault

```bash
helm install vault hashicorp/vault \
  --namespace vault \
  --values vault/vault-values.yaml

# Wait for pods Running (they will be 0/1 until init)
kubectl get pods -n vault -w

# Initialise and unseal
kubectl exec -n vault vault-0 -- vault operator init \
  -key-shares=5 -key-threshold=3 -format=json > vault-init.json

# Run unseal commands for all 3 nodes (see section 10)
# ...

# Port-forward and configure
kubectl port-forward -n vault svc/vault 8200:8200 &
export VAULT_ADDR=http://127.0.0.1:8200
export VAULT_TOKEN=$(cat vault-init.json | jq -r '.root_token')

# Run all vault write commands from section 10
# (kubernetes auth, kv secrets, policies, roles, PKI)

# Checkpoint
vault status
# Initialized: true, Sealed: false

vault kv get secret/apps/app1
# confirms secrets exist
```

### Phase 5: cert-manager

```bash
helm install cert-manager jetstack/cert-manager \
  --namespace cert-manager \
  --version v1.14.0 \
  --set installCRDs=true

# Checkpoint
kubectl get pods -n cert-manager
# All 3 Running

# IRSA for DNS-01 (if using wildcard certs)
eksctl create iamserviceaccount \
  --cluster=$CLUSTER_NAME \
  --namespace=cert-manager \
  --name=cert-manager \
  --role-name=CertManagerRole \
  --attach-policy-arn=arn:aws:iam::${ACCOUNT_ID}:policy/CertManagerRoute53Policy \
  --approve \
  --override-existing-serviceaccounts \
  --region=$REGION

# Deploy ClusterIssuers
kubectl apply -f cert-manager/cluster-issuer-http01.yaml
kubectl apply -f cert-manager/vault-cluster-issuer.yaml

# Checkpoint
kubectl get clusterissuer
# letsencrypt-production   True
# vault-issuer             True
```

### Phase 6: ExternalDNS

```bash
eksctl create iamserviceaccount \
  --cluster=$CLUSTER_NAME \
  --namespace=external-dns \
  --name=external-dns \
  --role-name=ExternalDNSRole \
  --attach-policy-arn=arn:aws:iam::${ACCOUNT_ID}:policy/ExternalDNSPolicy \
  --approve \
  --region=$REGION

kubectl apply -f external-dns/

# Checkpoint
kubectl logs -n external-dns deploy/external-dns | head -20
# Should show "All records are already up to date"
```

### Phase 7: Applications

```bash
kubectl apply -f apps/serviceaccounts.yaml
kubectl apply -f apps/app1-with-vault.yaml
kubectl apply -f apps/app2.yaml

# Checkpoint — app1 pods should have 3 containers
kubectl get pods -n apps
kubectl exec -n apps deploy/app1-deployment -c app1 \
  -- cat /vault/secrets/config
# Shows injected secrets
```

### Phase 8: Ingress with TLS

```bash
kubectl apply -f ingress/tls-ingress.yaml

# Watch ExternalDNS create the Route 53 records
kubectl logs -n external-dns deploy/external-dns -f

# Watch certificate issuance
kubectl get certificate -n apps -w
# app1-tls-secret   True   ← issued

# Final test
curl -I https://app1.yourdomain.com
# HTTP/2 200
# server: nginx
```

### Phase 9: Network Policies

```bash
kubectl apply -f network-policies/

# Re-test after policies are applied
curl -I https://app1.yourdomain.com
# Still HTTP/2 200

kubectl exec -n apps deploy/app1-deployment -c app1 \
  -- cat /vault/secrets/config
# Still shows secrets
```

---

## 16. Troubleshooting Reference

### AWS Load Balancer Controller

```bash
# Check controller logs
kubectl logs -n kube-system deploy/aws-load-balancer-controller -f

# Service stuck at <pending>
kubectl describe service ingress-nginx-controller -n ingress-basic
# Look at Events for AWS errors

# Common error: subnets not tagged
# "Failed to build model due to no matching subnet found"
# Solution: tag subnets with kubernetes.io/role/elb=1

# Common error: IRSA not configured
# "AccessDenied: User: arn:aws:sts::...assumed-role/..."
# Solution: verify ServiceAccount annotation
kubectl describe sa aws-load-balancer-controller -n kube-system
# Should show: eks.amazonaws.com/role-arn annotation

# Verify IRSA is working
kubectl exec -n kube-system deploy/aws-load-balancer-controller \
  -- aws sts get-caller-identity
# Should show the IAM role ARN, not EC2 instance role
```

### NGINX Ingress Issues

```bash
# Check NGINX logs
kubectl logs -n ingress-basic deploy/ingress-nginx-controller -f

# Test routing internally (bypass NLB)
kubectl run curl-test \
  --image=curlimages/curl --rm -it --restart=Never \
  --namespace=apps -- \
  curl -H "Host: app1.yourdomain.com" \
  http://ingress-nginx-controller.ingress-basic.svc.cluster.local

# Dump generated NGINX config
kubectl exec -n ingress-basic deploy/ingress-nginx-controller \
  -- nginx -T 2>/dev/null | grep -A10 "app1.yourdomain.com"

# Ingress has no Address assigned
kubectl get ingress -n apps
# If ADDRESS is empty, NGINX didn't process the Ingress
# Check: correct ingressClassName?
kubectl get ingress -n apps tls-ingress -o jsonpath='{.spec.ingressClassName}'
```

### cert-manager Issues

```bash
# Certificate stuck at READY: False
kubectl describe certificate -n apps app1-tls-secret

# Check Order and Challenge
kubectl get order -n apps
kubectl describe order -n apps

kubectl get challenge -n apps
kubectl describe challenge -n apps
# Common EKS issue: "HTTP01 probe failed"
# Cause: NLB hostname not yet in DNS, or cert-manager temp pod not reachable

# Check if challenge URL is reachable
CHALLENGE_TOKEN=$(kubectl get challenge -n apps -o jsonpath='{.items[0].spec.token}')
curl http://app1.yourdomain.com/.well-known/acme-challenge/$CHALLENGE_TOKEN
# Should return the token, not 404 or connection refused

# cert-manager controller logs
kubectl logs -n cert-manager deploy/cert-manager -f | grep -iE "error|certificate|challenge"

# Force re-issue
kubectl delete certificaterequest -n apps --all
kubectl delete order -n apps --all
# cert-manager recreates automatically
```

### Vault Issues

```bash
# Vault sealed after pod restart (if not using KMS auto-unseal)
kubectl exec -n vault vault-0 -- vault status | grep Sealed
# If true, run unseal commands again

# Test Kubernetes auth from inside a pod
kubectl run vault-test \
  --image=hashicorp/vault \
  --serviceaccount=app1-sa \
  --namespace=apps \
  --rm -it --restart=Never -- \
  /bin/sh -c "
    VAULT_ADDR=http://vault.vault.svc.cluster.local:8200
    JWT=\$(cat /var/run/secrets/kubernetes.io/serviceaccount/token)
    vault write auth/kubernetes/login role=app1-role jwt=\$JWT
  "
# Should output a Vault token

# Vault agent init failed
kubectl logs -n apps -l app=app1 -c vault-agent-init
# Common error: "permission denied"
# Solution: verify policy and role bindings in Vault

# Check injector logs
kubectl logs -n vault deploy/vault-agent-injector -f

# Verify the webhook is registered
kubectl get mutatingwebhookconfigurations | grep vault
kubectl describe mutatingwebhookconfiguration vault-agent-injector-cfg
```

### ExternalDNS Issues

```bash
# Check if records were created
kubectl logs -n external-dns deploy/external-dns | grep -iE "error|update|create"

# Verify IRSA for ExternalDNS
kubectl exec -n external-dns deploy/external-dns \
  -- aws sts get-caller-identity
# Should show ExternalDNSRole

# Check Route 53 directly
aws route53 list-resource-record-sets \
  --hosted-zone-id $HOSTED_ZONE_ID \
  --query "ResourceRecordSets[?contains(Name, 'yourdomain')]"
```

---

## 17. EKS vs AKS — Key Differences Summary

Understanding these differences prevents misapplying patterns learned on one cloud to the other.

| Concern | AKS | EKS |
|---|---|---|
| **Load Balancer provisioning** | Cloud Controller Manager (built-in) | AWS Load Balancer Controller (separate install) |
| **Load Balancer type (default)** | Azure Standard Load Balancer (Layer 4) | Classic ELB (legacy) or NLB/ALB via AWS LBC |
| **Static IP** | Azure Public IP resource, attached to LB | Elastic IP (EIP) for NLB; ALB uses DNS |
| **EXTERNAL-IP format** | Real IP address (`52.154.x.x`) | DNS hostname (`xxxx.elb.region.amazonaws.com`) |
| **DNS records** | A records pointing to IP | CNAME or Route 53 Alias records pointing to hostname |
| **IAM / identity** | Managed Service Identity (MSI) | IRSA (IAM Roles for Service Accounts) |
| **TLS via cloud service** | Azure App Gateway (separate addon) | ACM certificates on ALB/NLB |
| **cert-manager DNS-01** | Azure DNS zone delegated access | Route 53 via IRSA |
| **ExternalDNS auth** | MSI or Workload Identity | IRSA |
| **Vault auth** | Kubernetes auth (SA JWT) | Kubernetes auth (SA JWT) — same |
| **Network policy CNI** | Azure CNI with Azure Network Policy | VPC CNI + Calico, or Cilium |
| **Node identity** | VM Managed Identity | EC2 Instance Profile + IRSA per-pod |
| **Persistent volumes** | Azure Disk / Azure File | EBS / EFS via CSI drivers |
| **Subnet tagging required** | No | Yes — `kubernetes.io/role/elb=1` |
| **Ingress class for native LB** | `azure/application-gateway` | `alb` (AWS LBC) |

---

## 18. Component Summary

| Component | Type | Namespace | Role |
|---|---|---|---|
| AWS NLB | AWS Resource | N/A | Layer 4 TCP forwarding from internet to EKS nodes |
| AWS LBC | Deployment | kube-system | Provisions NLB/ALB from K8s Service/Ingress resources |
| NGINX Ingress Controller | Deployment | ingress-basic | Layer 7 HTTP routing, TLS termination |
| NGINX Service | Service (LoadBalancer) | ingress-basic | Triggers NLB provisioning |
| App1 / App2 | Deployment | apps | Application workloads |
| App1/2 Service | Service (ClusterIP) | apps | Internal routing target for NGINX |
| Ingress resource | Ingress | apps | Host/path routing rules |
| cert-manager | Deployment | cert-manager | Certificate lifecycle automation |
| ClusterIssuer (Let's Encrypt) | ClusterIssuer | cluster | ACME HTTP-01 or DNS-01 (Route 53) cert provider |
| ClusterIssuer (Vault PKI) | ClusterIssuer | cluster | Internal CA cert provider |
| Certificate resource | Certificate | apps | Desired TLS cert spec |
| TLS Secret | Secret | apps | Stores cert + key; read by NGINX |
| HashiCorp Vault | StatefulSet | vault | Secret storage, PKI, auth broker |
| vault-agent-injector | Deployment | vault | Mutating webhook — injects sidecars into pods |
| vault-agent | Sidecar | apps | Fetches and refreshes secrets at pod runtime |
| ExternalDNS | Deployment | external-dns | Syncs Ingress hostnames to Route 53 records |
| Route 53 | AWS Resource | N/A | DNS — maps hostnames to NLB endpoints |
| ACM | AWS Resource | N/A | Managed TLS certificates for ALB/NLB |
| IRSA | AWS IAM | N/A | Grants per-pod AWS API permissions via SA annotation |
| NetworkPolicy | NetworkPolicy | various | Zero-trust pod-to-pod traffic control |

### Full Certificate Flow Summary

```
Let's Encrypt (HTTP-01) path:
  Ingress annotation
    → cert-manager creates Certificate resource
    → cert-manager runs ACME HTTP-01 challenge
    → Let's Encrypt validates via: Route 53 → NLB → NGINX → temp pod
    → Certificate issued
    → Stored in K8s Secret
    → NGINX reads Secret → serves TLS

Let's Encrypt (DNS-01, wildcard) path:
  Certificate resource
    → cert-manager uses Route 53 IRSA credentials
    → Creates TXT record in Route 53
    → Let's Encrypt validates DNS record
    → Certificate issued → K8s Secret → NGINX

ACM path (ALB/NLB termination):
  ALB/NLB annotation (certificate-arn)
    → ALB/NLB loads ACM cert directly from AWS
    → TLS terminates at LB level
    → Plain HTTP forwarded to pods
    → No K8s Secret involved

Vault PKI path:
  cert-manager ClusterIssuer (vault-issuer)
    → cert-manager authenticates to Vault via K8s auth
    → Vault PKI signs the CSR
    → Certificate issued → K8s Secret → NGINX

Vault Agent (runtime secrets) path:
  Pod annotation (vault.hashicorp.com/agent-inject)
    → vault-agent-injector webhook patches pod spec
    → vault-agent-init authenticates with SA JWT
    → Reads KV secrets from Vault
    → Renders template → /vault/secrets/<file>
    → App reads file → uses secrets at runtime
```
