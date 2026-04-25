# Subnets in Kubernetes: EKS vs AKS

---

## Part 1: Subnets in Amazon EKS

### Overview

Amazon EKS (Elastic Kubernetes Service) runs inside an AWS **VPC (Virtual Private Cloud)**. Subnets in EKS determine where your control plane ENIs, worker nodes, pods, and load balancers are placed.

---

### Subnet Types in EKS

#### 1. Public Subnets
- Have a route to an **Internet Gateway (IGW)**
- Used for:
  - Public-facing **Load Balancers** (AWS ALB/NLB)
  - Bastion hosts / NAT Gateways
- Worker nodes placed here can have public IPs (not recommended for production)

#### 2. Private Subnets
- No direct route to the internet
- Outbound traffic goes through a **NAT Gateway** in a public subnet
- Used for:
  - **Worker nodes** (recommended)
  - **Pods** (with VPC CNI)
  - Internal Load Balancers

---

### EKS Subnet Requirements

#### Control Plane Subnets
EKS creates **Elastic Network Interfaces (ENIs)** in the subnets you specify during cluster creation. These ENIs allow the managed control plane to communicate with worker nodes.

- Minimum: **2 subnets** across **2 different Availability Zones**
- Recommended: use at least 2 AZs for high availability
- Subnets must have **at least 6 free IP addresses** (AWS recommends /28 or larger)

#### Worker Node Subnets
- Each node gets a primary IP from the subnet
- With **AWS VPC CNI**, each pod gets a **real VPC IP** from the node's subnet
- With **prefix delegation**, a /28 prefix is assigned per ENI, increasing pod density

#### Load Balancer Subnets
Subnet tags are required for the AWS Load Balancer Controller to auto-discover subnets:

| Tag | Value | Purpose |
|-----|-------|---------|
| `kubernetes.io/cluster/<cluster-name>` | `owned` or `shared` | Marks the subnet as usable by EKS |
| `kubernetes.io/role/elb` | `1` | Public subnet — for internet-facing LBs |
| `kubernetes.io/role/internal-elb` | `1` | Private subnet — for internal LBs |

---

### EKS Networking Architecture

```
VPC (e.g. 10.0.0.0/16)
├── AZ-1a
│   ├── Public Subnet  10.0.1.0/24   ← NAT GW, Public ALB
│   └── Private Subnet 10.0.2.0/24   ← Worker Nodes, Pods
├── AZ-1b
│   ├── Public Subnet  10.0.3.0/24   ← NAT GW, Public ALB
│   └── Private Subnet 10.0.4.0/24   ← Worker Nodes, Pods
└── AZ-1c
    ├── Public Subnet  10.0.5.0/24
    └── Private Subnet 10.0.6.0/24
```

---

### CNI and IP Address Management

#### AWS VPC CNI (default)
- Each pod gets a **secondary IP** directly from the VPC subnet
- Enables pod-to-pod communication without NAT
- IP consumption is high — plan subnet sizes carefully

**IP Planning Example:**
- Node instance type: `m5.large` → supports 3 ENIs × 10 IPs = **30 IPs per node**
- For 10 nodes: ~300 IPs needed from the private subnet

#### Custom CNI (e.g. Calico, Cilium)
- Pods get IPs from an **overlay network** (not VPC IPs)
- Less VPC IP consumption
- Requires disabling AWS VPC CNI or using it in "chained" mode

---

### Common EKS Subnet Mistakes

| Mistake | Impact |
|---------|--------|
| Too-small subnets | Nodes/pods fail to get IPs, scheduling fails |
| Missing subnet tags | Load Balancer Controller cannot find subnets |
| Single AZ | No high availability, AZ outage = cluster down |
| Worker nodes in public subnet | Security risk — nodes exposed to internet |
| Not enough IPs for control plane ENIs | Cluster creation or node join fails |

---

### EKS Subnet Best Practices

1. Use **private subnets for worker nodes** — never expose nodes directly to the internet
2. Size private subnets generously — `/19` or `/18` for large clusters (8192+ IPs)
3. Use at least **3 AZs** for production
4. Tag subnets correctly for the AWS Load Balancer Controller
5. Use a **separate VPC** per environment (dev/staging/prod)
6. Enable **VPC Flow Logs** for network visibility

---

---

## Part 2: Subnets in Azure AKS

### Overview

Azure AKS (Azure Kubernetes Service) runs inside an Azure **Virtual Network (VNet)**. You can deploy AKS into an existing VNet/subnet or let Azure create one automatically. The networking model (CNI plugin) significantly impacts how subnets are used.

---

### Subnet Types in AKS

#### 1. Node Subnet
- Where **AKS worker nodes (VMs)** are placed
- Every node gets a private IP from this subnet
- Required for all AKS network models

#### 2. Pod Subnet (Azure CNI Overlay / CNI with pod subnet)
- Separate subnet exclusively for **pod IPs**
- Used with **Azure CNI** (non-overlay) when pod subnet is specified
- Allows large pod IP space without consuming node subnet IPs

#### 3. API Server Subnet (VNet Integration)
- Used when **API Server VNet Integration** is enabled
- The AKS control plane (API server) gets IPs from this subnet
- Enables private, low-latency communication between nodes and control plane

#### 4. Internal Load Balancer Subnet
- The subnet where internal Azure Load Balancers are provisioned
- Specified via annotation: `service.beta.kubernetes.io/azure-load-balancer-internal-subnet`

---

### AKS Network Models

#### Kubenet (Basic)
- Nodes get IPs from the VNet subnet
- Pods get IPs from a **private overlay network** (not VNet IPs)
- A **UDR (User Defined Route)** is added for pod routing between nodes
- Low VNet IP consumption
- Limitations: no direct pod-to-pod VNet routing, max 400 nodes

```
VNet 10.0.0.0/8
└── Node Subnet 10.240.0.0/16  ← Nodes get IPs here
    Pod CIDR: 10.244.0.0/16    ← Pods (not in VNet, overlay)
```

#### Azure CNI (Advanced)
- Both **nodes and pods** get real VNet IPs
- Every pod is directly addressable within the VNet
- High IP consumption — plan carefully

```
VNet 10.0.0.0/8
└── Subnet 10.240.0.0/16
    Node IP:  10.240.0.4   (1 IP per node)
    Pod IPs:  10.240.0.5 – 10.240.0.34  (30 IPs per node by default)
```

**IP Planning for Azure CNI:**
- Default: each node reserves **30 pod IPs** from the subnet
- Formula: `required IPs = (max nodes × (max pods per node + 1)) + 1`
- Example: 50 nodes × 31 = 1,550 IPs → use at least a `/21` (2046 IPs)

#### Azure CNI Overlay (Recommended for large clusters)
- Nodes get VNet IPs, pods get IPs from a **private overlay CIDR** (not VNet)
- Best of both worlds: direct node connectivity + pod IP scalability
- Supports up to **250 pods per node**
- No UDR needed (unlike Kubenet)

```
VNet 10.0.0.0/8
└── Node Subnet 10.240.0.0/16  ← Nodes only
Pod Overlay CIDR: 192.168.0.0/16  ← Pods (virtual, not in VNet)
```

#### Azure CNI Powered by Cilium
- Uses **Cilium** as the CNI and network policy engine
- Supports eBPF-based networking — high performance
- Works with both overlay and non-overlay modes
- Required for **Azure Network Policy** with Cilium

---

### AKS Subnet Requirements

| Component | Requirement |
|-----------|-------------|
| Node subnet | Must be delegated to `Microsoft.ContainerService/managedClusters` (for BYO subnet) |
| Minimum node subnet size | `/29` (6 usable IPs) — but `/24` or larger recommended |
| Pod subnet (Azure CNI) | Separate subnet, not shared with other resources |
| API server subnet | `/28` minimum, dedicated, delegated to AKS |
| No subnet overlap | Node, pod, service CIDRs must not overlap |

---

### AKS Private Cluster and Subnet

When AKS is deployed as a **private cluster**:
- The API server endpoint is **not public** — only accessible within the VNet or peered VNets
- A **Private Endpoint** is created in the node subnet (or a dedicated subnet)
- DNS resolution is handled by **Azure Private DNS Zone**

```
Your VNet
└── Node Subnet
    ├── Worker Nodes
    └── Private Endpoint → AKS API Server (private IP)

Azure Private DNS Zone: privatelink.<region>.azmk8s.io
```

---

### AKS Networking Architecture

```
Azure VNet (e.g. 10.0.0.0/8)
├── Node Subnet      10.240.0.0/16   ← Worker VMs
├── Pod Subnet       10.241.0.0/16   ← Pods (Azure CNI with pod subnet)
├── API Server Subnet 10.242.0.0/28  ← Control plane VNet integration
└── (optional) Ingress Subnet        ← Application Gateway / Internal LB
```

---

### Service CIDR and DNS in AKS

These are virtual CIDRs (not tied to any subnet):

| Parameter | Default | Description |
|-----------|---------|-------------|
| `--service-cidr` | `10.0.0.0/16` | IP range for Kubernetes Services (ClusterIP) |
| `--dns-service-ip` | `10.0.0.10` | IP for CoreDNS — must be within service CIDR |
| `--pod-cidr` | `10.244.0.0/16` | Pod overlay CIDR (Kubenet / CNI Overlay) |

**Rules:**
- Service CIDR must not overlap with VNet address space
- DNS service IP must be within service CIDR (not the first IP)

---

### AKS Node Pool Subnets

Each **node pool** can be placed in a **different subnet**:
- System node pool → `10.240.0.0/24`
- GPU node pool → `10.240.1.0/24`
- Spot node pool → `10.240.2.0/24`

This allows network segmentation, different NSG rules per pool, and cost management.

---

### Common AKS Subnet Mistakes

| Mistake | Impact |
|---------|--------|
| Subnet too small (Azure CNI) | Node scale-out fails — no IPs available |
| Overlapping CIDRs | Routing failures, cluster creation blocked |
| Missing subnet delegation | BYO subnet rejected during cluster creation |
| Sharing subnet with other Azure resources | IP exhaustion, security boundary issues |
| Wrong DNS IP (not in service CIDR) | CoreDNS fails, all DNS in cluster breaks |

---

### AKS Subnet Best Practices

1. Use **Azure CNI Overlay** for large clusters to avoid IP exhaustion
2. Dedicate a subnet **per node pool** for isolation and NSG control
3. Use a `/24` or larger for node subnets — never `/29` in production
4. For private clusters, use a dedicated `/28` subnet for API server VNet integration
5. Plan service CIDR, pod CIDR, and VNet ranges **before deployment** — cannot change post-creation
6. Use **NSGs** on node subnets to restrict inbound/outbound traffic
7. Enable **Azure Network Policy** or **Calico** for pod-level network policies

---

## EKS vs AKS Subnet Comparison

| Feature | EKS | AKS |
|---------|-----|-----|
| Default CNI | AWS VPC CNI (pods get VPC IPs) | Kubenet or Azure CNI |
| Pod IP source | VPC subnet (real IPs) | Overlay or VNet subnet |
| Control plane subnet | EKS creates ENIs in your subnets | Optional API server VNet integration |
| Subnet tags required | Yes (for LB auto-discovery) | No (uses annotations) |
| IP consumption (default) | High — every pod uses a VPC IP | Low (Kubenet) or High (Azure CNI) |
| Multi-AZ requirement | 2+ AZs required | Availability Zones optional |
| Private cluster | Private endpoint + Route53 PHZ | Private endpoint + Azure Private DNS |
| Node pool per subnet | Yes (managed node groups) | Yes (per node pool) |
| Max pods per node (default) | Based on ENI limits per instance | 30 (Azure CNI), 110 (Kubenet/Overlay) |
