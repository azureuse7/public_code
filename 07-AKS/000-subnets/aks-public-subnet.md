# Public Subnets in AKS — Do They Exist?

---

## Short Answer

**Azure does not have a concept of "public subnet" vs "private subnet".**

Unlike AWS, Azure subnets do **not** have route tables with an Internet Gateway toggle.
In Azure, **all subnets within a VNet can route to the internet by default** — the control is done differently.

---

## How Azure Controls Internet Access (Instead of Subnet Type)

AWS uses subnet type (public/private) as the primary control.
Azure uses a layered model:

| Control Layer | Azure Equivalent | Controls |
|---------------|-----------------|----------|
| Subnet "public/private" | **Does not exist** | — |
| Internet routing | **Default system routes** (always present) | Outbound internet access |
| Inbound internet access | **Public IP on the resource** | Whether a resource is reachable |
| Traffic filtering | **NSG (Network Security Group)** | Allow/deny inbound and outbound |
| Forced routing | **UDR (User Defined Route)** | Override default routes, force traffic to firewall |
| Outbound control | **NAT Gateway or Azure Firewall** | Centralized outbound internet |

---

## Default Behavior of an Azure Subnet

When you create a subnet in Azure VNet, by default:

```
Azure Subnet (no extra config)
├── Outbound to internet:  ALLOWED  (via default system route)
├── Inbound from internet: BLOCKED  (no public IP assigned to resource)
├── VNet-internal traffic: ALLOWED
└── Azure services traffic: ALLOWED
```

Every Azure subnet has these **default system routes** automatically:

| Address Prefix | Next Hop |
|----------------|----------|
| VNet address space | Virtual network (local) |
| `0.0.0.0/0` | Internet |
| Azure service ranges | Internet |

So technically, **every Azure subnet has a route to the internet** — similar to what AWS calls a "public subnet" — but inbound access is still blocked unless a public IP is assigned.

---

## How AKS Nodes Get Internet Access

### Outbound (Egress) — Three Options

#### Option 1: Load Balancer (Default)
AKS creates a **public Standard Load Balancer** with a public IP.
All outbound traffic from nodes uses this LB's public IP via SNAT.

```
AKS Node (private IP only)
  └── Outbound traffic → Azure Load Balancer (public IP) → Internet
```

#### Option 2: NAT Gateway
A **NAT Gateway** is attached to the node subnet.
More scalable than LB for outbound — no SNAT port exhaustion.

```
AKS Node
  └── Outbound traffic → NAT Gateway (public IP) → Internet
```

#### Option 3: User Defined Route (UDR) — Bring Your Own
All outbound traffic is forced through **Azure Firewall** or a third-party NVA.

```
AKS Node
  └── Outbound traffic → UDR → Azure Firewall → Internet
```

This is the **most secure** option — used in enterprise/private clusters.

---

## Inbound Traffic to AKS — How It Works

Since there are no "public subnets" in Azure, inbound internet access depends on **public IPs assigned to specific resources**.

### Internet-Facing Load Balancer (Ingress)
```yaml
apiVersion: v1
kind: Service
metadata:
  name: my-app
spec:
  type: LoadBalancer   # Azure creates a public IP for this LB
  ports:
    - port: 80
```
Azure provisions a **public Standard Load Balancer** with a public IP in the same resource group as the AKS nodes.
The node subnet does not need to be "public" — the LB sits outside the subnet.

### Internal Load Balancer (No Internet Exposure)
```yaml
apiVersion: v1
kind: Service
metadata:
  name: my-internal-app
  annotations:
    service.beta.kubernetes.io/azure-load-balancer-internal: "true"
spec:
  type: LoadBalancer
```
Azure provisions an **internal Load Balancer** with a private IP from the node subnet (or a specified subnet).
No internet access at all.

### Application Gateway Ingress Controller (AGIC)
- An **Azure Application Gateway** (Layer 7 LB) is placed in a **dedicated subnet**
- The App Gateway has a public IP
- It forwards traffic to AKS pods via private IPs

```
Internet → App Gateway (public IP, dedicated subnet) → AKS Pods (private IPs)
```

---

## AKS Networking Architecture (No Public/Private Subnet Split)

```
Azure VNet  10.0.0.0/8
│
├── Node Subnet         10.240.0.0/16
│   ├── AKS Node 1  (private IP only, e.g. 10.240.0.4)
│   ├── AKS Node 2  (private IP only, e.g. 10.240.0.5)
│   ├── NAT Gateway or LB for outbound  ──────────────→ Internet
│   └── Internal Load Balancer (if internal service)
│
├── App Gateway Subnet  10.241.0.0/24
│   └── Application Gateway (public IP) ←────────────── Internet
│
└── API Server Subnet   10.242.0.0/28   (private cluster only)
    └── AKS Control Plane ENI
```

Note: there is no "public subnet" with an Internet Gateway like AWS.
Instead, **individual resources** (LB, App Gateway, NAT GW) hold public IPs.

---

## Controlling "Public" vs "Private" in AKS — The Real Controls

### NSG (Network Security Group)
Attached to a subnet or NIC. Acts as a firewall.

```
NSG on Node Subnet — example rules
┌────────────────┬──────────┬────────┬────────┐
│ Rule           │ Source   │ Port   │ Action │
├────────────────┼──────────┼────────┼────────┤
│ Allow LB probe │ AzureLB  │ any    │ Allow  │
│ Allow VNet     │ VirtualN │ any    │ Allow  │
│ Deny internet  │ Internet │ any    │ Deny   │  ← blocks inbound internet
└────────────────┴──────────┴────────┴────────┘
```

### UDR (User Defined Route) — Force Tunnel
Override the default `0.0.0.0/0 → Internet` route to send traffic to a firewall instead:

```
Custom Route Table on Node Subnet
┌─────────────────┬──────────────────────────┐
│ Destination     │ Next Hop                 │
├─────────────────┼──────────────────────────┤
│ 10.0.0.0/8      │ Virtual network (local)  │
│ 0.0.0.0/0       │ 10.0.100.4 (Firewall IP) │  ← all internet via firewall
└─────────────────┴──────────────────────────┘
```

This turns the subnet "private" in the AWS sense — no direct internet access.

### Private Cluster
When AKS is deployed as a **private cluster**:
- The API server has **no public endpoint**
- Access is only via private IP within the VNet or peered VNets

```
Public Cluster:   kubectl → public API endpoint (internet-accessible)
Private Cluster:  kubectl → private endpoint (VNet/VPN/ExpressRoute only)
```

---

## AKS vs EKS — Public Subnet Comparison

| Concept | AWS EKS | Azure AKS |
|---------|---------|-----------|
| Public subnet definition | Subnet with `0.0.0.0/0 → IGW` route | Does not exist as a concept |
| Private subnet definition | Subnet without IGW route | Subnet with NSG deny + UDR to firewall |
| Default internet access | Only public subnets | All subnets (via default system routes) |
| Internet-facing LB placement | Must be in a tagged public subnet | LB is not inside a subnet (resource-level public IP) |
| Worker node internet (outbound) | Via NAT GW in public subnet | Via LB, NAT GW, or Azure Firewall |
| Inbound internet to nodes | Possible if public IP + SG allows | Blocked by default (no public IP on nodes) |
| Isolating nodes from internet | Put in private subnet | Use NSG deny rules + UDR |
| Required subnet tags for LB | Yes (`kubernetes.io/role/elb = 1`) | No tags — uses annotations on the Service |

---

## Summary

| Question | Answer |
|----------|--------|
| Does AKS have public subnets? | No — Azure has no public/private subnet distinction |
| Can AKS nodes reach the internet? | Yes — via default routes (LB, NAT GW, or Firewall) |
| Can AKS nodes receive internet traffic? | Only if a public IP resource (LB, App GW) routes to them |
| How do you make AKS "private"? | NSG deny rules + UDR to force traffic through Azure Firewall |
| What is the closest AWS "public subnet" equivalent in AKS? | A subnet with a NAT Gateway or public LB for outbound, and an App Gateway for inbound |
