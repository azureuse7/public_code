# EKS Networking Deep Dive: CNI, AWS VPC CNI, Calico & Cilium

---

## Table of Contents

1. [The Problem CNI Solves](#1-the-problem-cni-solves)
2. [What is the Container Network Interface (CNI)?](#2-what-is-the-container-network-interface-cni)
3. [AWS VPC CNI — The EKS Default](#3-aws-vpc-cni--the-eks-default)
4. [How Other CNIs Fit In: Calico & Cilium](#4-how-other-cnis-fit-in-calico--cilium)
5. [End-to-End Traffic Walkthrough](#5-end-to-end-traffic-walkthrough)
6. [Network Policy Comparison](#6-network-policy-comparison)
7. [Choosing the Right CNI for EKS](#7-choosing-the-right-cni-for-eks)
8. [Quick Reference Cheat Sheet](#8-quick-reference-cheat-sheet)

---

## 1. The Problem CNI Solves

By default, Linux network namespaces are completely isolated. When a container runtime (like `containerd`) creates a container, it gets its own private network namespace — it cannot talk to any other container or the outside world.

Kubernetes adds an extra requirement on top of that: **every Pod must be reachable from every other Pod without NAT**, regardless of which Node they live on. This is called the **Kubernetes Networking Model**.

```
Kubernetes Networking Rules:
  ✅ Pod-to-Pod on the same Node  — no NAT
  ✅ Pod-to-Pod across Nodes      — no NAT
  ✅ Node-to-Pod                  — no NAT
  ✅ Pod sees its own IP externally (no masquerade for inbound)
```

Implementing this across potentially hundreds of Nodes in AWS is non-trivial. That's exactly the gap CNI fills.

---

## 2. What is the Container Network Interface (CNI)?

### 2.1 Definition

CNI is a **specification + library** that defines how container runtimes should configure networking for containers. It's a contract between:

- The **container runtime** (e.g., `containerd`, `cri-o`) — which calls CNI
- The **CNI plugin** (e.g., AWS VPC CNI, Calico, Cilium) — which does the work

The spec lives at: https://github.com/containernetworking/cni

### 2.2 How CNI Works — Step by Step

When Kubernetes schedules a new Pod, this sequence happens:

```
1. kubelet receives a Pod spec from the API server
2. kubelet tells the container runtime (containerd) to start the Pod
3. containerd creates a network namespace: /var/run/netns/abc123
4. containerd calls the CNI plugin via a JSON config in /etc/cni/net.d/
5. CNI plugin runs its ADD command:
      - Creates a veth pair
      - Assigns an IP address to the Pod
      - Sets up routes so traffic can flow
6. Pod is now reachable on its assigned IP
```

When a Pod is deleted:

```
1. containerd calls the CNI plugin's DEL command
2. CNI plugin cleans up:
      - Removes veth pair
      - Releases the IP back to the pool
      - Removes routes
3. Network namespace is destroyed
```

### 2.3 CNI Plugin Interface

The plugin is just a binary that accepts JSON on stdin and writes JSON to stdout:

```json
// Input: what containerd sends to the CNI plugin
{
  "cniVersion": "0.4.0",
  "name": "my-net",
  "type": "aws-cni",        // Which plugin binary to call
  "kubernetes": {
    "k8s_api_root": "https://10.0.0.1",
    "podName": "my-app-7d4f9",
    "podNamespace": "default",
    "podUID": "abc-123"
  }
}

// Output: what the plugin returns
{
  "cniVersion": "0.4.0",
  "ips": [
    {
      "version": "4",
      "address": "192.168.1.45/32",
      "gateway": "192.168.1.1"
    }
  ],
  "routes": [
    { "dst": "0.0.0.0/0" }
  ]
}
```

### 2.4 Key CNI Concepts

| Concept | Description |
|---|---|
| **veth pair** | A virtual Ethernet cable — one end in the Pod namespace, one end on the host |
| **bridge** | A virtual switch on the host — many veth ends connect to it |
| **IPAM** | IP Address Management — how IPs are assigned to Pods |
| **overlay** | Encapsulates Pod traffic in another protocol (VXLAN/GENEVE) to cross Node boundaries |
| **underlay** | Uses native routing (no encapsulation) — requires the network to know Pod CIDRs |

---

## 3. AWS VPC CNI — The EKS Default

### 3.1 What Makes It Special

Most CNIs assign Pods IPs from a **separate overlay network** (e.g., `10.244.0.0/16`) that is distinct from the VPC network. Traffic between Pods on different Nodes gets **encapsulated** (tunnelled) before being sent.

AWS VPC CNI takes a completely different approach: **Pods get real VPC IP addresses**. There is no overlay — Pod IPs are native to the VPC.

```
Traditional overlay CNI:
  Pod A (10.244.1.5) → encapsulate in VXLAN → Node IP (172.16.0.10) → Node IP (172.16.0.20) → decapsulate → Pod B (10.244.2.8)

AWS VPC CNI:
  Pod A (10.0.1.45) ─────────────────────────────────────────────────→ Pod B (10.0.2.12)
  (Pod IPs ARE VPC IPs — routed natively by VPC)
```

### 3.2 How It Works: Elastic Network Interfaces (ENIs)

Each EC2 instance supports multiple **Elastic Network Interfaces (ENIs)**, and each ENI can have multiple **secondary private IPv4 addresses**.

AWS VPC CNI exploits this:

```
EC2 Node (e.g., m5.xlarge):
  ┌──────────────────────────────────────────────────────────────────┐
  │ Primary ENI (eth0)                                                │
  │   Primary IP: 10.0.1.10  ← Node IP                               │
  │   Secondary IPs: 10.0.1.45, 10.0.1.46, 10.0.1.47  ← Pod IPs    │
  │                                                                   │
  │ Secondary ENI (eth1)                                              │
  │   Primary IP: 10.0.1.20                                          │
  │   Secondary IPs: 10.0.1.50, 10.0.1.51, 10.0.1.52  ← Pod IPs    │
  └──────────────────────────────────────────────────────────────────┘
```

The `aws-node` DaemonSet (the VPC CNI agent) runs on every Node and:

1. Attaches additional ENIs to the Node as Pod density grows
2. Pre-warms a pool of secondary IPs so Pod startup is fast
3. Associates each secondary IP to a Pod when it is scheduled

### 3.3 The IPAMD (IP Address Management Daemon)

`ipamd` is the core daemon in `aws-node`. It:

- Monitors the Node's ENIs via EC2 API
- Maintains a warm pool of available secondary IPs (controlled by `WARM_IP_TARGET`, `MINIMUM_IP_TARGET`)
- Assigns IPs to Pods on request from the CNI plugin binary

```
Pod scheduled on Node
        │
        ▼
containerd calls /opt/cni/bin/aws-cni
        │
        ▼
aws-cni binary contacts ipamd via gRPC (unix socket)
        │
        ▼
ipamd picks an IP from the warm pool: 10.0.1.47
        │
        ▼
aws-cni creates veth pair:
  - eth0 inside Pod namespace → IP 10.0.1.47/32
  - eniY inside host namespace → connected to the ENI
        │
        ▼
aws-cni adds host routes:
  ip route add 10.0.1.47 dev eniY   (route to this Pod)
        │
        ▼
Pod is running with IP 10.0.1.47 — a real VPC IP
```

### 3.4 Pod Density Limits

Because Pod IPs come from ENI secondary IPs, you're constrained by EC2 instance limits:

```
Max Pods = (Number of ENIs) × (IPs per ENI - 1) + 2

Example: m5.xlarge
  ENIs:       4
  IPs/ENI:    15
  Max Pods:   (4 × (15-1)) + 2 = 58
```

You can check limits: https://github.com/awslabs/amazon-eks-ami/blob/main/nodeadm/internal/kubelet/eni-max-pods.txt

To exceed these limits, you can enable **prefix delegation** (assigns /28 prefixes to ENIs instead of individual IPs).

### 3.5 Security Groups for Pods

Because Pods have VPC IPs, you can apply **AWS Security Groups directly to Pods** — not just Nodes. This is done via the `SecurityGroupPolicy` CRD:

```yaml
apiVersion: vpcresources.k8s.aws/v1beta1
kind: SecurityGroupPolicy
metadata:
  name: allow-rds-access
  namespace: production
spec:
  podSelector:
    matchLabels:
      app: backend-api
  securityGroups:
    groupIds:
      - sg-0abc123def456789a   # SG that allows port 5432 to RDS
```

This is a significant advantage over other CNIs where you'd have to open the SG at the Node level.

### 3.6 VPC CNI Configuration (Key Environment Variables)

```yaml
# aws-node DaemonSet env vars

WARM_IP_TARGET: "2"          # Always keep 2 spare IPs ready per Node
MINIMUM_IP_TARGET: "10"      # Minimum IPs to pre-allocate
WARM_ENI_TARGET: "1"         # Keep 1 spare ENI attached
ENABLE_PREFIX_DELEGATION: "true"   # Assign /28 blocks for higher Pod density
AWS_VPC_K8S_CNI_EXTERNALSNAT: "false"  # Use VPC NAT gateway (not Node SNAT) for egress
ENABLE_POD_ENI: "true"       # Enable Security Groups for Pods
```

---

## 4. How Other CNIs Fit In: Calico & Cilium

### 4.1 Why Use a Different CNI at All?

AWS VPC CNI is excellent for basic connectivity and AWS-native integration, but it has gaps:

| Feature | AWS VPC CNI | Calico | Cilium |
|---|---|---|---|
| Basic Pod networking | ✅ | ✅ | ✅ |
| Kubernetes NetworkPolicy | ❌ (needs add-on) | ✅ | ✅ |
| Egress gateway | ❌ | ✅ (Enterprise) | ✅ |
| L7 policies (HTTP, gRPC) | ❌ | ❌ (Enterprise) | ✅ |
| WireGuard encryption | ❌ | ✅ | ✅ |
| eBPF dataplane | ❌ | ✅ (v3.13+) | ✅ (native) |
| Built-in observability | ❌ | Limited | ✅ (Hubble) |
| FQDN-based policies | ❌ | ✅ | ✅ |

### 4.2 Calico on EKS

#### 4.2.1 Two Deployment Modes

**Mode 1: Calico for NetworkPolicy only (most common on EKS)**

AWS VPC CNI handles IP assignment; Calico only enforces NetworkPolicy. This is the simplest approach.

```
┌─────────────────────────────────────────────────────┐
│ Data plane                                           │
│   AWS VPC CNI  ─── assigns Pod IPs (VPC native)     │
│   Calico Felix ─── programs iptables/eBPF rules      │
│                    for NetworkPolicy enforcement     │
└─────────────────────────────────────────────────────┘
```

Installation:
```bash
kubectl apply -f https://raw.githubusercontent.com/aws/amazon-vpc-cni-k8s/master/config/master/calico-operator.yaml
```

**Mode 2: Calico as full CNI replacement**

Calico replaces VPC CNI entirely and manages its own IP space. Pods get Calico-managed IPs (not VPC IPs). Traffic crosses Nodes via BGP routing or VXLAN encapsulation.

```
Node A (10.0.1.10)          Node B (10.0.2.10)
  Pod: 192.168.1.5             Pod: 192.168.2.8
       │                             │
       └──── VXLAN tunnel ───────────┘
             (or BGP route)
```

When using this mode on EKS, you lose Security Groups for Pods since Pod IPs aren't VPC IPs.

#### 4.2.2 Calico NetworkPolicy Example

Calico supports both Kubernetes `NetworkPolicy` and its own richer `GlobalNetworkPolicy` CRD:

```yaml
# Standard Kubernetes NetworkPolicy (Calico enforces these)
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-frontend-to-backend
  namespace: production
spec:
  podSelector:
    matchLabels:
      app: backend
  policyTypes:
    - Ingress
  ingress:
    - from:
        - podSelector:
            matchLabels:
              app: frontend
      ports:
        - protocol: TCP
          port: 8080
```

```yaml
# Calico GlobalNetworkPolicy — cluster-wide, more powerful
apiVersion: projectcalico.org/v3
kind: GlobalNetworkPolicy
metadata:
  name: deny-all-egress-except-dns
spec:
  selector: all()          # Applies to all endpoints
  types:
    - Egress
  egress:
    - action: Allow
      protocol: UDP
      destination:
        ports: [53]        # Allow DNS
    - action: Allow
      protocol: TCP
      destination:
        ports: [53]
    - action: Deny          # Block everything else egress
```

```yaml
# FQDN-based policy (Calico Enterprise / open-source via DNS policy)
apiVersion: projectcalico.org/v3
kind: GlobalNetworkPolicy
metadata:
  name: allow-s3-access
spec:
  selector: app == "data-processor"
  egress:
    - action: Allow
      destination:
        domains:
          - "*.s3.amazonaws.com"
          - "*.s3.us-east-1.amazonaws.com"
```

#### 4.2.3 How Calico Enforces Policy — Felix

Calico's agent is **Felix**, running as a DaemonSet. Felix:

1. Watches Kubernetes NetworkPolicy objects via the API server
2. Computes the required iptables or eBPF rules
3. Programs them into the kernel on the Node

```
NetworkPolicy object
      │
      ▼ (watch)
 Calico Felix
      │
      ▼ (programs)
 iptables / eBPF rules on Node
      │
      ▼ (enforced on)
 veth interfaces of Pods
```

With eBPF mode (`FELIX_BPFENABLED=true`), Felix bypasses iptables entirely, compiling policy directly into BPF programs attached to network interfaces — significantly faster at scale.

### 4.3 Cilium on EKS

#### 4.3.1 Architecture

Cilium is built from the ground up on **eBPF** (extended Berkeley Packet Filter). Instead of iptables rules, Cilium compiles networking and security logic into BPF programs that run inside the Linux kernel.

```
Traditional CNI (iptables):
  Packet → iptables (100s of rules) → routing decision → destination

Cilium (eBPF):
  Packet → BPF program (JIT compiled, kernel-native) → destination
           (runs in kernel, no context switch to userspace)
```

#### 4.3.2 Cilium on EKS: Two Modes

**Mode 1: Cilium with AWS VPC CNI (chaining mode)**

Like Calico's policy-only mode, Cilium can chain on top of VPC CNI — taking over NetworkPolicy enforcement while VPC CNI handles IP assignment.

```bash
# Helm install in chaining mode
helm install cilium cilium/cilium \
  --namespace kube-system \
  --set cni.chainingMode=aws-cni \
  --set enableIPv4Masquerade=false \
  --set tunnel=disabled
```

**Mode 2: Cilium as replacement CNI (EKS Auto Mode / ACNS)**

AWS's **Advanced Container Networking Services (ACNS)** is powered by Cilium. In this mode, Cilium manages the full dataplane — including Pod IPs using prefix delegation.

EKS Auto Mode uses `networking.k8s.aws/v1alpha1` `ClusterNetworkPolicy` (a superset of Kubernetes NetworkPolicy):

```yaml
apiVersion: networking.k8s.aws/v1alpha1
kind: ClusterNetworkPolicy
metadata:
  name: default-deny-all
spec:
  policyType: Ingress
  podSelector: {}       # All pods
  ingress: []           # No ingress allowed by default
```

#### 4.3.3 Cilium NetworkPolicy Examples

**L3/L4 policy (like standard NetworkPolicy):**
```yaml
apiVersion: cilium.io/v2
kind: CiliumNetworkPolicy
metadata:
  name: allow-payments-api
  namespace: production
spec:
  endpointSelector:
    matchLabels:
      app: payments-api
  ingress:
    - fromEndpoints:
        - matchLabels:
            app: checkout-service
      toPorts:
        - ports:
            - port: "8443"
              protocol: TCP
```

**L7 policy — HTTP method + path (unique to Cilium):**
```yaml
apiVersion: cilium.io/v2
kind: CiliumNetworkPolicy
metadata:
  name: allow-get-only
  namespace: production
spec:
  endpointSelector:
    matchLabels:
      app: product-catalog
  ingress:
    - fromEndpoints:
        - matchLabels:
            app: frontend
      toPorts:
        - ports:
            - port: "8080"
              protocol: TCP
          rules:
            http:
              - method: "GET"           # Only GET allowed
                path: "/api/v1/products.*"
              # POST /api/v1/products → DENIED
              # GET  /api/v1/products  → ALLOWED
```

**DNS-based egress policy:**
```yaml
apiVersion: cilium.io/v2
kind: CiliumNetworkPolicy
metadata:
  name: allow-external-api
spec:
  endpointSelector:
    matchLabels:
      app: data-fetcher
  egress:
    - toFQDNs:
        - matchPattern: "api.stripe.com"
        - matchPattern: "*.amazonaws.com"
    - toEndpoints:
        - matchLabels:
            k8s:io.kubernetes.pod.namespace: kube-system
            k8s:k8s-app: kube-dns
      toPorts:
        - ports:
            - port: "53"
              protocol: UDP
```

#### 4.3.4 Hubble — Cilium's Observability Layer

Hubble is built into Cilium and provides deep network visibility:

```bash
# Install Hubble UI
helm upgrade cilium cilium/cilium \
  --set hubble.enabled=true \
  --set hubble.relay.enabled=true \
  --set hubble.ui.enabled=true

# CLI: observe live traffic
hubble observe --namespace production

# Example output:
# TIMESTAMP             SOURCE                      DESTINATION                VERDICT
# 2024-01-15 10:23:01   production/frontend-7d9f    production/backend-4k2p    FORWARDED
# 2024-01-15 10:23:01   production/frontend-7d9f    production/db-6m8r         DROPPED    (policy denied)
# 2024-01-15 10:23:02   production/backend-4k2p     kube-system/kube-dns-xyz   FORWARDED
```

Hubble gives you: flow logs, service dependency maps, policy verdict visibility, HTTP metrics (status codes, latency) — without any application changes.

---

## 5. End-to-End Traffic Walkthrough

Let's trace a complete request from a frontend Pod to a backend Pod across two different Nodes on EKS.

### Setup

```
VPC CIDR:           10.0.0.0/16
Node A:             10.0.1.10  (runs frontend Pod)
Node B:             10.0.2.10  (runs backend Pod)
Frontend Pod IP:    10.0.1.45  (assigned via VPC CNI)
Backend Pod IP:     10.0.2.18  (assigned via VPC CNI)
```

### 5.1 Pod-to-Pod: Same Node (AWS VPC CNI)

```
Frontend Pod (10.0.1.45)
        │ eth0 (inside Pod network namespace)
        │
    veth pair
        │
        │ veth_frontend (on host network namespace)
        │
   [host routing table]
   ip route: 10.0.1.47 dev veth_backend  ← direct veth route
        │
        │ veth_backend (on host network namespace)
        │
    veth pair
        │
        │ eth0 (inside Pod network namespace)
        ▼
Backend Pod (10.0.1.47)
```

No encapsulation, no bridge, just direct veth-to-veth routing via the host routing table.

### 5.2 Pod-to-Pod: Cross Node (AWS VPC CNI)

```
NODE A (10.0.1.10)
┌──────────────────────────────────────────────────────┐
│  Frontend Pod (10.0.1.45)                             │
│     │ eth0                                            │
│  veth pair                                           │
│     │ veth_front (host ns)                           │
│                                                      │
│  Host routing table:                                 │
│    10.0.1.45 dev veth_front    (local pod)           │
│    10.0.2.0/24 → ENI → VPC    (remote subnet)       │
│     │                                                │
│  eth0 / eth1 (ENI)                                   │
└──────────────────────────────────────────────────────┘
          │
          │  AWS VPC routing (native, no encapsulation)
          │  Packet: src=10.0.1.45, dst=10.0.2.18
          │  VPC route table: 10.0.2.0/24 → local
          ▼
NODE B (10.0.2.10)
┌──────────────────────────────────────────────────────┐
│  eth0 / eth1 (ENI) receives packet                   │
│     │                                                │
│  Host routing table:                                 │
│    10.0.2.18 dev veth_back     (local pod route)     │
│     │                                                │
│  veth pair                                           │
│     │ veth_back (host ns)                            │
│     │ eth0 (Pod ns)                                  │
│     ▼                                                │
│  Backend Pod (10.0.2.18)                             │
└──────────────────────────────────────────────────────┘
```

Because Pods have real VPC IPs, the VPC routing table handles cross-Node routing transparently — just like routing between two EC2 instances.

### 5.3 Same Scenario with Calico Overlay (for comparison)

If Calico were the sole CNI with VXLAN mode:

```
Frontend Pod (192.168.1.5) — Calico IP, NOT a VPC IP
        │
        │ eth0 (Pod ns) → cali_front veth (host ns)
        │
   Calico Felix routing:
        │
        ▼
   VXLAN encapsulation:
   Inner: src=192.168.1.5, dst=192.168.2.8
   Outer: src=10.0.1.10 (Node A VPC IP), dst=10.0.2.10 (Node B VPC IP)
        │
        │  AWS VPC routes Node A → Node B (via VPC IP)
        ▼
   Node B decapsulates:
   Inner packet: dst=192.168.2.8
        │
        │ Routes to veth for backend Pod
        ▼
   Backend Pod (192.168.2.8)
```

The overhead of encapsulation/decapsulation adds latency (~5–15%) and reduces MTU (overhead from VXLAN header).

### 5.4 Pod-to-Service Traffic

Services use `kube-proxy` (iptables/IPVS) or Cilium's eBPF kube-proxy replacement for DNAT:

```
Frontend Pod → ClusterIP Service (10.100.50.30:80)
       │
       │ Packet: src=10.0.1.45, dst=10.100.50.30:80
       │
  iptables PREROUTING (kube-proxy rules)
  OR Cilium BPF (if kube-proxy replacement enabled)
       │
       │ DNAT: dst=10.100.50.30:80 → dst=10.0.2.18:8080 (selected endpoint)
       │ Conntrack entry created
       ▼
  Routed to Backend Pod (10.0.2.18:8080)

Reply:
  Backend Pod → src=10.0.2.18:8080, dst=10.0.1.45
       │
  iptables/BPF conntrack: reverse SNAT
       │ src=10.100.50.30:80 restored
       ▼
  Frontend Pod sees reply from ClusterIP (10.100.50.30)
```

With **Cilium kube-proxy replacement**, the BPF program intercepts at the socket layer — the DNAT happens before the packet even reaches the network stack, eliminating the cost of iptables rules entirely.

### 5.5 Egress: Pod to the Internet / AWS Services

```
Backend Pod (10.0.2.18) → api.stripe.com

With default VPC CNI (SNAT at Node):
  Pod IP 10.0.2.18 → SNATed to Node IP 10.0.2.10 → NAT Gateway → Internet

With AWS_VPC_K8S_CNI_EXTERNALSNAT=true (VPC NAT):
  Pod IP 10.0.2.18 → VPC NAT Gateway (not SNATed at Node) → Internet
  (Pod IP visible in flow logs — better for security auditing)

With Cilium Egress Gateway:
  Pod IP 10.0.2.18 → dedicated egress Node (10.0.3.50) → fixed Elastic IP
  (specific Pods always egress from a fixed, predictable IP — useful for IP allowlisting)
```

---

## 6. Network Policy Comparison

### 6.1 Default Behaviour Without Policy

Without any NetworkPolicy, all Pod-to-Pod traffic is **allowed** in Kubernetes. Always start with a default-deny:

```yaml
# Default deny all ingress and egress for a namespace
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-all
  namespace: production
spec:
  podSelector: {}      # Selects all Pods in namespace
  policyTypes:
    - Ingress
    - Egress
```

### 6.2 Allowing DNS (Critical — Never Forget)

After default-deny, Pods cannot resolve DNS. Always add:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-dns-egress
  namespace: production
spec:
  podSelector: {}
  policyTypes:
    - Egress
  egress:
    - to:
        - namespaceSelector:
            matchLabels:
              kubernetes.io/metadata.name: kube-system
      ports:
        - protocol: UDP
          port: 53
        - protocol: TCP
          port: 53
```

### 6.3 Feature Comparison Table

| Capability | k8s NetworkPolicy | Calico (OSS) | Cilium |
|---|---|---|---|
| L3 IP block rules | ✅ | ✅ | ✅ |
| L4 port/protocol | ✅ | ✅ | ✅ |
| L7 HTTP/gRPC rules | ❌ | ❌ | ✅ |
| FQDN / DNS policies | ❌ | ✅ | ✅ |
| Global policies (cluster-wide) | ❌ | ✅ | ✅ |
| Egress gateway with fixed IP | ❌ | ✅ (Enterprise) | ✅ |
| Policy audit/logging | ❌ | ✅ | ✅ (Hubble) |
| WireGuard encryption | ❌ | ✅ | ✅ |
| eBPF dataplane | ❌ | ✅ (opt-in) | ✅ (native) |
| kube-proxy replacement | ❌ | ❌ | ✅ |

---

## 7. Choosing the Right CNI for EKS

### Decision Tree

```
Start here
    │
    ├── Do you need Security Groups per Pod?
    │       YES → Use AWS VPC CNI (+ Calico/Cilium for policy)
    │
    ├── Do you need L7 policies (HTTP path, method, gRPC)?
    │       YES → Use Cilium (chaining or replacement mode)
    │
    ├── Do you need FQDN-based egress policies?
    │       YES → Calico or Cilium
    │
    ├── Do you need Pod-level encryption (WireGuard)?
    │       YES → Calico or Cilium
    │
    ├── Do you want maximum AWS-native simplicity?
    │       YES → AWS VPC CNI only (add Calico for policy enforcement)
    │
    └── EKS Auto Mode?
            YES → ACNS (Cilium under the hood) — managed by AWS
```

### Common Patterns at gagan/Enterprise Scale

| Pattern | Components | Use Case |
|---|---|---|
| **AWS Native** | VPC CNI + Calico (policy only) | Most common; AWS SG per Pod; standard K8s NetworkPolicy |
| **Observability-first** | VPC CNI + Cilium (chaining) | Need Hubble visibility + L7 policy; keep VPC IPs |
| **Full Cilium** | Cilium replaces VPC CNI | eBPF performance; L7 policies; kube-proxy replacement |
| **EKS Auto Mode** | AWS-managed ACNS (Cilium) | Managed nodes; ClusterNetworkPolicy CRD |

---

## 8. Quick Reference Cheat Sheet

### AWS VPC CNI

```bash
# Check ipamd status
kubectl logs -n kube-system -l k8s-app=aws-node -c aws-node | grep -i "ip address"

# See IP assignments per Node
kubectl get eniconfig
kubectl describe node <node> | grep -A 20 "Allocatable"

# Check warm pool
kubectl exec -n kube-system $(kubectl get pod -n kube-system -l k8s-app=aws-node -o name | head -1) \
  -- /app/grpc-health-probe -addr=:50051

# Enable prefix delegation
kubectl set env daemonset aws-node -n kube-system ENABLE_PREFIX_DELEGATION=true
kubectl set env daemonset aws-node -n kube-system WARM_PREFIX_TARGET=1
```

### Calico

```bash
# Install calicoctl
curl -L https://github.com/projectcalico/calico/releases/latest/download/calicoctl-linux-amd64 -o calicoctl
chmod +x calicoctl

# Check Felix status on a Node
kubectl exec -n calico-system $(kubectl get pod -n calico-system -l app=calico-node -o name | head -1) \
  -- calico-node -felix-live

# List all NetworkPolicies
calicoctl get networkpolicy --all-namespaces

# Verify policy is being enforced
calicoctl get globalnetworkpolicy

# View iptables rules set by Calico
iptables -L cali-FORWARD --line-numbers | head -30
```

### Cilium

```bash
# Check Cilium status
cilium status

# Live traffic observation (requires Hubble)
hubble observe --namespace production --last 100
hubble observe --verdict DROPPED

# Test connectivity
cilium connectivity test

# View BPF maps
cilium bpf policy get
cilium bpf lb list       # Load balancer entries (kube-proxy replacement)

# Check endpoint policy
cilium endpoint list
cilium endpoint get <id>
```

### NetworkPolicy Debugging

```bash
# Test Pod-to-Pod connectivity
kubectl exec -it frontend-pod -- curl -v http://backend-svc:8080/health

# Check if NetworkPolicy exists
kubectl get networkpolicy -n production

# Describe what a policy selects
kubectl describe networkpolicy allow-frontend -n production

# Temporarily bypass for debugging (label trick)
kubectl label pod backend-pod debug=true   # If policy excludes debug=true pods
```

---

## Summary

```
CNI Spec
  └── defines the interface between container runtime and network plugin

AWS VPC CNI
  └── assigns real VPC IPs to Pods via ENI secondary IPs
  └── no overlay, native VPC routing
  └── enables Security Groups per Pod
  └── constrained by EC2 ENI/IP limits

Calico (on EKS)
  └── typically used in policy-only mode (on top of VPC CNI)
  └── enforces NetworkPolicy via Felix (iptables or eBPF)
  └── richer policy model: GlobalNetworkPolicy, FQDN, ordering

Cilium (on EKS)
  └── eBPF-native — fast, programmable, kernel-level
  └── L7 policies (HTTP, gRPC, Kafka)
  └── kube-proxy replacement
  └── Hubble observability
  └── EKS Auto Mode / ACNS is Cilium under the hood
```

---

*Document generated: April 2026*
*Covers: EKS with AWS VPC CNI, Calico OSS, Cilium OSS, EKS Auto Mode / ACNS*
