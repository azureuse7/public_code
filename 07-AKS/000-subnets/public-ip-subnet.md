# Public IP Subnets in AWS / EKS

---

## What Is a Public Subnet?

A **public subnet** is a subnet whose route table contains a route that sends internet-bound traffic (`0.0.0.0/0`) to an **Internet Gateway (IGW)**.

```
Route Table (Public Subnet)
┌─────────────────┬────────────────────┐
│ Destination     │ Target             │
├─────────────────┼────────────────────┤
│ 10.0.0.0/16     │ local              │  ← VPC-internal traffic
│ 0.0.0.0/0       │ igw-xxxxxxxxx      │  ← Internet traffic → IGW
└─────────────────┴────────────────────┘
```

A subnet is **private** if that `0.0.0.0/0 → igw` route does not exist.

---

## What Does a Public Subnet Do?

### 1. Enables Direct Inbound Internet Access
Resources in a public subnet with a **public IP or Elastic IP** can receive traffic directly from the internet.

- A web server in a public subnet on port 443 → reachable from the world
- An EC2 instance with a public IP → SSH-able from your laptop

### 2. Enables Direct Outbound Internet Access
Resources in a public subnet can initiate connections to the internet **without a NAT Gateway**.

- Pull Docker images from DockerHub
- Call external APIs
- Download OS updates

### 3. Hosts Resources That Must Be Reachable from the Internet
- **Internet-facing Load Balancers** (ALB / NLB)
- **NAT Gateways** (so private subnets can reach the internet)
- **Bastion hosts** (jump servers)
- **VPN endpoints**

---

## Public Subnet vs Private Subnet

| Feature | Public Subnet | Private Subnet |
|---------|---------------|----------------|
| Route to Internet Gateway | Yes (`0.0.0.0/0 → igw`) | No |
| Resources get public IPs | Optional (if subnet setting enabled) | No |
| Inbound internet traffic | Possible (with public IP + SG rules) | Not possible directly |
| Outbound internet traffic | Direct via IGW | Via NAT Gateway (in public subnet) |
| Typical resources | LB, NAT GW, Bastion | Worker nodes, databases, pods |
| Security exposure | Higher | Lower |

---

## How Public IP Assignment Works in a Subnet

Every subnet has a setting:
> **"Auto-assign public IPv4 address"** → enabled or disabled

| Setting | Effect |
|---------|--------|
| Enabled | Every EC2/EKS node launched in this subnet gets a **public IP automatically** |
| Disabled | No public IP unless you explicitly assign an Elastic IP |

In AWS Console: VPC → Subnets → Select subnet → Actions → **Edit subnet settings**

---

## Public Subnets in EKS — What They Do

In an EKS cluster, public subnets serve specific, limited roles.

### Role 1: Internet-Facing Load Balancers
When a Kubernetes `Service` of type `LoadBalancer` is created with no internal annotation, AWS provisions an **ALB or NLB in the public subnet**.

```yaml
apiVersion: v1
kind: Service
metadata:
  name: my-app
  # No internal annotation → goes to public subnet
spec:
  type: LoadBalancer
  ports:
    - port: 80
```

The AWS Load Balancer Controller picks the public subnet based on this tag:
```
kubernetes.io/role/elb = 1
```

### Role 2: NAT Gateway Placement
Private worker nodes need outbound internet access to:
- Pull container images from ECR / DockerHub
- Call AWS APIs (EC2, S3, etc.)
- Download Helm charts

A **NAT Gateway is placed in the public subnet**. Private subnet route tables point `0.0.0.0/0` to this NAT GW.

```
Private Subnet Route Table
┌─────────────────┬────────────────────┐
│ Destination     │ Target             │
├─────────────────┼────────────────────┤
│ 10.0.0.0/16     │ local              │
│ 0.0.0.0/0       │ nat-xxxxxxxxx      │  ← NAT GW (sits in public subnet)
└─────────────────┴────────────────────┘
```

### Role 3: Bastion Hosts (Optional)
A bastion host in the public subnet lets you SSH into private worker nodes for debugging.

```
Internet → Bastion (public subnet, port 22) → Worker Node (private subnet, port 22)
```

### Role 4: Worker Nodes (Not Recommended)
Worker nodes *can* be placed in public subnets, but this is **not recommended** because:
- Node ports become internet-accessible
- Increases attack surface
- If `Auto-assign public IP` is on, every node gets a public IP

---

## EKS Public Subnet Architecture

```
VPC 10.0.0.0/16
│
├── us-east-1a
│   ├── Public Subnet  10.0.1.0/24
│   │   ├── NAT Gateway  ───────────────────────┐
│   │   ├── Internet-facing ALB                 │
│   │   └── (optional) Bastion Host             │
│   │                                           │
│   └── Private Subnet 10.0.2.0/24             │
│       ├── EKS Worker Node 1                  │
│       ├── EKS Worker Node 2                  │ (outbound via NAT)
│       └── Pods (VPC CNI IPs)  ───────────────┘
│
├── us-east-1b
│   ├── Public Subnet  10.0.3.0/24
│   │   └── NAT Gateway
│   └── Private Subnet 10.0.4.0/24
│       └── EKS Worker Nodes
│
└── Internet Gateway  ← attached to VPC, used by all public subnets
```

---

## Subnet Tags Required by EKS

EKS and the AWS Load Balancer Controller use tags to discover which subnets to use.

### Public Subnet Tags

| Tag Key | Value | Purpose |
|---------|-------|---------|
| `kubernetes.io/cluster/<cluster-name>` | `owned` or `shared` | Tells EKS this subnet belongs to the cluster |
| `kubernetes.io/role/elb` | `1` | Marks subnet for **internet-facing** Load Balancers |

### Private Subnet Tags

| Tag Key | Value | Purpose |
|---------|-------|---------|
| `kubernetes.io/cluster/<cluster-name>` | `owned` or `shared` | Cluster association |
| `kubernetes.io/role/internal-elb` | `1` | Marks subnet for **internal** Load Balancers |

Without these tags, the AWS Load Balancer Controller cannot find the right subnet and `LoadBalancer` services will stay in `Pending` state indefinitely.

---

## Public IP on EKS Nodes — What Happens

### With Public IP Enabled on Worker Nodes
```
Worker Node
├── Private IP: 10.0.2.15   (VPC-internal)
├── Public IP:  54.x.x.x    (internet-reachable)
└── All NodePort services reachable from internet (if SG allows)
```

### With Public IP Disabled (Recommended)
```
Worker Node
├── Private IP: 10.0.2.15   (VPC-internal only)
└── Outbound internet: via NAT Gateway
```

Disabling public IPs on nodes means:
- No direct inbound internet access to nodes
- Outbound traffic still works via NAT Gateway
- Security groups are your only protection if public IPs are enabled

---

## Security Groups and Public Subnets

Being in a public subnet does **not** automatically open traffic. **Security Groups** are the firewall layer.

```
Public Subnet + Security Group = what actually controls traffic

Example: ALB Security Group
┌─────────────────────────────────────────────┐
│ Inbound:  0.0.0.0/0  → port 443  (HTTPS)   │
│ Inbound:  0.0.0.0/0  → port 80   (HTTP)    │
│ Outbound: 10.0.0.0/16 → port 8080 (to pods)│
└─────────────────────────────────────────────┘
```

A resource in a public subnet with **no inbound SG rules** is still not reachable from the internet.

---

## Common Mistakes with Public Subnets in EKS

| Mistake | Consequence |
|---------|-------------|
| Placing worker nodes in public subnet with auto-assign public IP | Every node exposed to internet |
| Missing `kubernetes.io/role/elb = 1` tag | ALB/NLB creation fails — Service stuck in Pending |
| Only 1 public subnet (single AZ) | ALB requires 2+ AZs — creation fails |
| No NAT Gateway in public subnet | Private nodes cannot pull images or call AWS APIs |
| Overly permissive Security Group on public resources | Security risk — internet can reach internal services |

---

## Quick Reference: What Goes Where

| Resource | Subnet Type | Why |
|----------|-------------|-----|
| EKS Worker Nodes | **Private** | Not directly internet-accessible |
| Pods (VPC CNI) | **Private** | Same subnet as nodes |
| Internet-facing ALB / NLB | **Public** | Needs direct internet access |
| Internal ALB / NLB | **Private** | Only accessible within VPC |
| NAT Gateway | **Public** | Needs IGW to forward outbound traffic |
| Bastion Host | **Public** | Must be SSH-able from internet |
| RDS / ElastiCache | **Private** | Never expose databases publicly |
| ECR VPC Endpoints | **Private** | Keep image pulls internal |
