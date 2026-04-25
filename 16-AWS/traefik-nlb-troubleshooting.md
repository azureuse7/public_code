# Traefik / NLB Gateway Timeout — Troubleshooting Guide

## End-to-End Traffic Flow & What's Going Wrong

### The Full Request Journey

```
User Browser
     │
     ▼
[Internet]
     │
     ▼
AWS Network Load Balancer (NLB)
  - Listens on ports 80/443
  - Has a Security Group allowing inbound 80/443  ✅
     │
     ▼
Traefik Pod (Ingress Controller)
  - Receives the request
  - Looks up routing rules (IngressRoute / Ingress objects)
  - Tries to forward to the target Service/Pod  ❌ FAILS HERE
     │
     ▼
Target Pod (e.g. your app on port 8080)
```



---

## Why This Happens — The Most Likely Causes

### 1. Network Policy is blocking Traefik → Pod traffic



---

### 2. Security Group on the Worker Nodes is blocking pod-to-pod traffic

On EKS, pods communicate via the node's Security Group. If the **node Security Group** doesn't allow traffic on the port your app pod listens on, Traefik's packets get dropped at the AWS network level.

**What to check:**
- Go to EC2 → Security Groups
- Find the Security Group attached to your worker nodes
- Check inbound rules — does it allow traffic from **other nodes in the same SG** on the app's port?

Typically you need a self-referencing rule:

```
Inbound: All traffic / Source = same Security Group ID
```

This allows node-to-node (and therefore pod-to-pod) communication.

---

### 3. Traefik can't resolve the Kubernetes Service DNS

Traefik forwards to a `Service` name like `my-app.default.svc.cluster.local`. If CoreDNS is broken or Traefik's egress to port 53 is blocked by a NetworkPolicy, it can't resolve the address and times out.

**What to check:**

```bash
# Exec into Traefik pod and test DNS
kubectl exec -it <traefik-pod> -n traefik -- sh
nslookup kubernetes.default.svc.cluster.local
nslookup <your-service>.<namespace>.svc.cluster.local
```

---

### 4. The target Service or endpoints are misconfigured

Even if routing is fine, if the Service has no ready endpoints (pods not matching the selector), Traefik gets a connection refused or timeout.

```bash
# Check endpoints — should show pod IPs, not be empty
kubectl get endpoints <service-name> -n <namespace>

# If empty, your Service selector doesn't match pod labels
kubectl describe service <service-name> -n <namespace>
kubectl get pods -n <namespace> --show-labels
```

---

### 5. NLB → Traefik: Node Security Group missing NodePort access

You said the NLB SG allows inbound 80/443, but on EKS with NLB the traffic flows:

```
NLB → Node IP (NodePort) → Traefik Pod
```

The **node's Security Group** must allow inbound on the **NodePort range** (30000–32767) or the specific NodePort Traefik uses, from the NLB's source IPs (or the NLB SG).

```bash
# Find what NodePort Traefik's service is using
kubectl get svc -n traefik
# Look for something like 80:31234/TCP — 31234 is the NodePort
```

Then verify that port 31234 is allowed inbound on the worker node Security Group.

---

## Diagnostic Checklist — In Order

| Step | Command | What you're confirming |
|------|---------|------------------------|
| 1 | `kubectl get endpoints -n <ns>` | App pods are registered |
| 2 | `kubectl get networkpolicy -A` | No default-deny blocking Traefik |
| 3 | Exec into Traefik pod, `curl <svc>.<ns>.svc.cluster.local:<port>` | Direct connectivity to app |
| 4 | Check node SG inbound rules | NodePort range open from NLB |
| 5 | `kubectl logs <traefik-pod> -n traefik` | Traefik error messages |
| 6 | `kubectl describe ingressroute` or `kubectl describe ingress` | Routing rules correct |

---

