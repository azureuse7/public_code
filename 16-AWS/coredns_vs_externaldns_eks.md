# CoreDNS vs External DNS in Amazon EKS — End-to-End Guide

---

## Overview

| | CoreDNS | External DNS |
|---|---|---|
| **Purpose** | Internal cluster DNS resolution | Sync Kubernetes resources to external DNS providers (e.g. Route 53) |
| **Scope** | Inside the cluster only | Outside the cluster (public/private DNS) |
| **Manages** | `cluster.local` DNS namespace | Real DNS zones (e.g. `myapp.example.com`) |
| **Deployed as** | Kubernetes Deployment (managed add-on) | Kubernetes Deployment (self-managed or add-on) |
| **Who calls it** | Every pod, every DNS lookup | Kubernetes controller watches Ingress/Service |

---

## Part 1 — CoreDNS

### What is it?

CoreDNS is the **in-cluster DNS server**. It is the authoritative resolver for the `cluster.local` domain and handles all DNS lookups that pods make inside the cluster.

It is a managed EKS add-on and is deployed automatically when you create an EKS cluster.

---

### What CoreDNS resolves

| DNS Name | Resolves To |
|---|---|
| `my-service` | Service in the same namespace |
| `my-service.my-namespace` | Service in another namespace |
| `my-service.my-namespace.svc.cluster.local` | Fully qualified service ClusterIP |
| `my-pod-ip.my-namespace.pod.cluster.local` | Individual pod IP |
| `google.com` | Forwarded upstream (to VPC DNS / Route 53 Resolver) |

---

### Architecture inside EKS

```
Pod
 │
 │  DNS query: "my-service.default.svc.cluster.local"
 ▼
/etc/resolv.conf  ──► nameserver 172.20.0.10   (CoreDNS ClusterIP)
                       search default.svc.cluster.local svc.cluster.local cluster.local
 │
 ▼
CoreDNS Deployment (2+ replicas in kube-system)
 │
 ├── cluster.local queries ──► answered from in-memory cache of kube-apiserver data
 │                              (Service/Endpoint records synced via watches)
 │
 └── external queries (e.g. google.com) ──► forwarded to 169.254.169.253
                                             (VPC DNS / Route 53 Resolver endpoint)
```

CoreDNS listens on the `kube-dns` Service, which always has the IP `172.20.0.10` (or `10.96.0.10` depending on CIDR).

---

### How pods find CoreDNS

When a pod starts, `kubelet` injects `/etc/resolv.conf` automatically:

```
nameserver 172.20.0.10
search default.svc.cluster.local svc.cluster.local cluster.local ec2.internal
options ndots:5
```

- `nameserver` → CoreDNS ClusterIP
- `search` → allows short names like `my-service` to resolve without FQDN
- `ndots:5` → if the name has fewer than 5 dots, search domains are tried first

---

### CoreDNS ConfigMap (Corefile)

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: coredns
  namespace: kube-system
data:
  Corefile: |
    .:53 {
        errors
        health {
            lameduck 5s
        }
        ready
        kubernetes cluster.local in-addr.arpa ip6.arpa {
            pods insecure
            fallthrough in-addr.arpa ip6.arpa
            ttl 30
        }
        prometheus :9153
        forward . /etc/resolv.conf       # forwards external queries to VPC DNS
        cache 30
        loop
        reload
        loadbalance
    }
```

Key plugins:

| Plugin | Purpose |
|---|---|
| `kubernetes` | Watches kube-apiserver for Services/Endpoints; answers `cluster.local` queries |
| `forward` | Forwards non-cluster queries upstream (VPC DNS) |
| `cache` | Caches responses to reduce upstream load |
| `health` | HTTP health endpoint on port 8080 |
| `ready` | Readiness probe endpoint on port 8181 |
| `prometheus` | Exposes metrics on port 9153 |

---

### CoreDNS in EKS — Managed Add-on

EKS manages CoreDNS as an add-on. You can view and update it:

```bash
# Check current version
aws eks describe-addon \
  --cluster-name my-cluster \
  --addon-name coredns

# List available versions
aws eks describe-addon-versions --addon-name coredns

# Update the add-on
aws eks update-addon \
  --cluster-name my-cluster \
  --addon-name coredns \
  --addon-version v1.11.1-eksbuild.4 \
  --resolve-conflicts OVERWRITE
```

> **Warning:** If you customise the CoreDNS ConfigMap, use `PRESERVE` for `--resolve-conflicts` to avoid Anthropic overwriting your changes on updates.

---

### CoreDNS scaling on EKS

By default EKS deploys 2 replicas. For large clusters, use `cluster-proportional-autoscaler`:

```yaml
# Scales CoreDNS based on node count
--target=Deployment/coredns
--namespace=kube-system
--default-params={"linear":{"coresPerReplica":256,"nodesPerReplica":16,"min":2}}
```

Or use the `NodeLocal DNSCache` DaemonSet to cache DNS at the node level and reduce load on CoreDNS pods.

---

### Common CoreDNS issues on EKS

| Symptom | Likely Cause | Fix |
|---|---|---|
| Pods can't resolve services | CoreDNS pods not running | `kubectl get pods -n kube-system -l k8s-app=kube-dns` |
| Slow DNS | `ndots:5` causing many search-domain attempts | Use FQDNs or reduce `ndots` |
| CoreDNS OOMKilled | High cluster traffic, not enough memory | Increase resource limits, add replicas |
| External DNS failing | VPC DNS unreachable or custom forward target wrong | Check `forward` plugin config and security groups |
| Network policy blocking CoreDNS | Egress rules deny port 53 | Allow egress to `172.20.0.10/32` port `53` (UDP+TCP) |

---

---

## Part 2 — External DNS

### What is it?

External DNS is a **Kubernetes controller** that watches Kubernetes resources (Ingress, Service of type LoadBalancer) and **automatically creates/updates DNS records in an external DNS provider** — most commonly AWS Route 53.

It bridges the gap between Kubernetes and real-world DNS.

---

### What External DNS manages

| Kubernetes Resource | DNS Record Created |
|---|---|
| `Service` (type: LoadBalancer) | A record or CNAME → NLB/ELB hostname |
| `Ingress` | A record or CNAME → ALB/NLB hostname |
| `HTTPRoute` (Gateway API) | A record → Gateway endpoint |

---

### Architecture in EKS

```
Developer applies Ingress/Service
          │
          ▼
   Kubernetes API Server
          │
          │  External DNS controller watches for:
          │  - Ingress with hostname annotations
          │  - Services with external-dns annotations
          ▼
  External DNS Pod (kube-system)
          │
          │  Calls Route 53 API (via IRSA / IAM role)
          ▼
    AWS Route 53
          │
          ├── Creates A record:   myapp.example.com → 1.2.3.4 (ALB IP or CNAME)
          └── Creates TXT record: "heritage=external-dns,owner=my-cluster"
                                  (ownership marker to avoid conflicts)
          │
          ▼
    End User Browser
    DNS query: myapp.example.com ──► Route 53 ──► ALB/NLB IP
```

---

### How External DNS identifies what to manage

External DNS uses **annotations** on your resources:

```yaml
# On an Ingress
metadata:
  annotations:
    external-dns.alpha.kubernetes.io/hostname: myapp.example.com
    external-dns.alpha.kubernetes.io/ttl: "60"

# On a LoadBalancer Service
metadata:
  annotations:
    external-dns.alpha.kubernetes.io/hostname: api.example.com
```

Or it can auto-detect hostnames from the `spec.rules[].host` field in an Ingress.

---

### IRSA — IAM permissions for External DNS

External DNS needs Route 53 permissions. On EKS, use **IRSA (IAM Roles for Service Accounts)**:

#### Step 1 — IAM Policy

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "route53:ChangeResourceRecordSets"
      ],
      "Resource": "arn:aws:route53:::hostedzone/*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "route53:ListHostedZones",
        "route53:ListResourceRecordSets",
        "route53:ListTagsForResource"
      ],
      "Resource": "*"
    }
  ]
}
```

#### Step 2 — IAM Role with trust policy

```json
{
  "Effect": "Allow",
  "Principal": {
    "Federated": "arn:aws:iam::123456789012:oidc-provider/oidc.eks.eu-west-2.amazonaws.com/id/EXAMPLED539D4633E53DE1B71EXAMPLE"
  },
  "Action": "sts:AssumeRoleWithWebIdentity",
  "Condition": {
    "StringEquals": {
      "oidc.eks.eu-west-2.amazonaws.com/id/EXAMPLED539D4633E53DE1B71EXAMPLE:sub": "system:serviceaccount:kube-system:external-dns"
    }
  }
}
```

#### Step 3 — Annotate the ServiceAccount

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: external-dns
  namespace: kube-system
  annotations:
    eks.amazonaws.com/role-arn: arn:aws:iam::123456789012:role/external-dns-role
```

---

### Deploying External DNS with Helm

```bash
helm repo add external-dns https://kubernetes-sigs.github.io/external-dns/
helm repo update

helm install external-dns external-dns/external-dns \
  --namespace kube-system \
  --set provider=aws \
  --set aws.region=eu-west-2 \
  --set serviceAccount.create=false \
  --set serviceAccount.name=external-dns \
  --set policy=sync \
  --set domainFilters[0]=example.com \
  --set txtOwnerId=my-eks-cluster
```

Key Helm values:

| Value | Description |
|---|---|
| `provider` | DNS provider (`aws`, `azure`, `google`, etc.) |
| `policy` | `sync` (create+delete) or `upsert-only` (never delete) |
| `domainFilters` | Restrict which zones External DNS manages |
| `txtOwnerId` | Unique cluster identifier written into TXT ownership records |
| `aws.zoneType` | `public`, `private`, or empty (both) |

---

### DNS record lifecycle

```
1. You create:  kubectl apply -f ingress.yaml
                (with hostname: myapp.example.com)

2. External DNS detects the Ingress via watch

3. External DNS queries: what is the current LB address?
   → ALB hostname: abc123.eu-west-2.elb.amazonaws.com

4. External DNS calls Route 53 API:
   → Upserts CNAME: myapp.example.com → abc123.eu-west-2.elb.amazonaws.com
   → Upserts TXT:   "heritage=external-dns,owner=my-eks-cluster,resource=ingress/default/myapp"

5. You delete: kubectl delete -f ingress.yaml

6. External DNS detects deletion
   → Deletes CNAME record (if policy=sync)
   → Deletes TXT ownership record
```

---

### Common External DNS issues on EKS

| Symptom | Likely Cause | Fix |
|---|---|---|
| Records not created | IRSA not configured correctly | Check pod logs: `kubectl logs -n kube-system -l app=external-dns` |
| Records not deleted | `policy=upsert-only` set | Change to `policy=sync` if deletion is intended |
| Wrong hosted zone updated | Missing `domainFilters` | Set `--domain-filter=example.com` |
| Conflict between clusters | Same `txtOwnerId` on multiple clusters | Use unique `txtOwnerId` per cluster |
| Records created but not resolving | Route 53 propagation delay | Wait 30–60s; check with `dig myapp.example.com` |
| Private zone not updated | `aws.zoneType` not set to `private` | Set `--aws-zone-type=private` |

---

---

## Part 3 — Side-by-Side Comparison

| Dimension | CoreDNS | External DNS |
|---|---|---|
| **DNS scope** | Internal (`cluster.local`) | External (your real domain) |
| **Records managed** | Service A/SRV records in memory | Route 53 (or other) A/CNAME/TXT records |
| **Who queries it** | Pods inside the cluster | Internet users / VPN users |
| **TTL typical** | 30s (in-memory, near-instant) | 60–300s (Route 53 propagation) |
| **Triggered by** | Every pod DNS call | Ingress/Service create/update/delete |
| **Authentication** | None (in-cluster) | IRSA / IAM role |
| **EKS managed add-on** | Yes | No (self-managed via Helm) |
| **Failure impact** | All pod-to-pod comms break | New services not reachable externally |
| **Customisation** | Corefile ConfigMap | Helm values / CLI flags |

---

## Part 4 — How They Work Together (End-to-End Flow)

Here is the complete flow from a developer deploying an app to an end user hitting it:

```
Developer
  │
  │  kubectl apply -f deployment.yaml
  │  kubectl apply -f service.yaml (type: LoadBalancer)
  │  kubectl apply -f ingress.yaml (host: myapp.example.com)
  │
  ▼
Kubernetes API Server
  │
  ├──► AWS Load Balancer Controller
  │      └── Creates ALB: abc123.eu-west-2.elb.amazonaws.com
  │
  ├──► External DNS Controller
  │      └── Sees Ingress host: myapp.example.com
  │      └── Calls Route 53: CNAME myapp.example.com → abc123...elb.amazonaws.com
  │
  └──► CoreDNS (watches Services)
         └── Stores in memory: my-service.default.svc.cluster.local → 10.100.x.x (ClusterIP)

─────────────────────────────────────────────────────────────────────

Inside the cluster (pod-to-pod):

  frontend-pod
    │
    │  curl http://backend-service/api
    │  (DNS: backend-service.default.svc.cluster.local)
    ▼
  CoreDNS  ──► returns ClusterIP 10.100.42.10
    │
  kube-proxy ──► routes to one of the backend pod IPs

─────────────────────────────────────────────────────────────────────

Outside the cluster (end user):

  User browser
    │
    │  https://myapp.example.com
    ▼
  Route 53 (managed by External DNS)
    │  resolves: myapp.example.com → abc123.elb.amazonaws.com → ALB IP
    ▼
  AWS ALB
    │  routes to the correct Service/pod via NodePort/TargetGroup
    ▼
  Your Pod
```

---

## Part 5 — Key Takeaways

1. **CoreDNS** is the cluster's internal phone book. Without it, no pod can find any other pod by name.

2. **External DNS** is the bridge between your cluster and the real world. Without it, you'd have to manually update Route 53 every time you deploy or scale a service.

3. They are **complementary, not competing** — both run simultaneously and solve completely different problems.

4. In EKS, CoreDNS is AWS-managed; External DNS is your responsibility to deploy and configure with correct IRSA permissions.

5. Always set a **unique `txtOwnerId`** per cluster in External DNS to prevent multi-cluster conflicts over the same Route 53 records.

---


