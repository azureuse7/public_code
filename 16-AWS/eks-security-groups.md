# Security Groups in Amazon EKS — End-to-End Guide

---

## 1. What Are Security Groups?

Security Groups (SGs) are **virtual firewalls** in AWS that control inbound and outbound traffic at the network interface (ENI) level. They are **stateful** — if you allow inbound traffic on a port, the response traffic is automatically allowed outbound.

In the context of EKS, security groups govern traffic between:

- The **EKS control plane** (managed by AWS) and your worker nodes
- **Worker nodes** communicating with each other (pod-to-pod, node-to-node)
- **Pods** and external AWS services (RDS, ElastiCache, etc.)
- **Load balancers** and the pods behind them

---

## 2. Types of Security Groups in EKS

### 2.1 Cluster Security Group (Auto-created)

When you create an EKS cluster, AWS automatically creates a **Cluster Security Group**. Its ID is visible in the EKS console under **Networking**.

- Attached to **both the control plane ENIs and all managed node groups** by default
- Allows unrestricted communication between the control plane and nodes
- Tagged: `kubernetes.io/cluster/<cluster-name>: owned`

### 2.2 Node Group Security Group

Each managed node group can have **additional security groups** attached alongside the cluster SG. These let you:

- Restrict traffic to specific node groups
- Allow nodes to reach specific databases or internal services

### 2.3 Security Groups for Pods (SGP)

Introduced in EKS via the **VPC CNI plugin**, this feature allows you to assign an AWS Security Group **directly to a Kubernetes pod**, not just to the node. This is the most granular option.

---

## 3. Default Traffic Rules (Cluster Security Group)

| Direction | Protocol | Port Range | Source/Destination | Purpose |
|-----------|----------|------------|-------------------|---------|
| Inbound   | TCP      | 443        | Control plane SG  | API server → kubelet |
| Inbound   | TCP      | 10250      | Control plane SG  | API server → kubelet metrics |
| Inbound   | All      | All        | Same SG (self)    | Node-to-node communication |
| Outbound  | All      | All        | 0.0.0.0/0         | All outbound traffic |

> ⚠️ **Note:** The self-referencing inbound rule is what enables pod-to-pod communication across nodes.

---

## 4. Security Groups for Pods (SGP) — Deep Dive

### 4.1 How It Works

Normally, pods inherit the security group of the node they run on. With SGP:

1. The VPC CNI plugin creates a **branch ENI** for the pod
2. The specified security group is attached to that branch ENI
3. AWS Security Group rules apply **at the pod level**, not the node level

This enables fine-grained network policies enforced by AWS — useful when Kubernetes NetworkPolicies aren't sufficient (e.g., for cross-VPC or RDS access).

### 4.2 Prerequisites

- EKS cluster on Kubernetes **1.17+**
- VPC CNI plugin version **1.7.7+**
- Node instances must be **Nitro-based** (e.g., m5, c5, r5, t3 — NOT t2)
- The `ENABLE_POD_ENI` flag must be set to `true` on the VPC CNI DaemonSet

### 4.3 Supported Instance Types

Only **AWS Nitro-based instances** support branch ENIs for SGP:

```
m5, m5a, m5d, m5n, m5zn
c5, c5a, c5d, c5n
r5, r5a, r5d, r5n
t3, t3a
p3, p3dn, g4dn
and others — check: https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/instance-types.html
```

---

## 5. Installation & Configuration

### Step 1: Enable Pod ENI on the VPC CNI DaemonSet

```bash
kubectl set env daemonset aws-node \
  -n kube-system \
  ENABLE_POD_ENI=true
```

Verify it's applied:

```bash
kubectl get daemonset aws-node -n kube-system \
  -o jsonpath='{.spec.template.spec.containers[0].env}' | jq .
```

### Step 2: Create the Security Group in AWS

Using the AWS CLI:

```bash
# Create the security group
aws ec2 create-security-group \
  --group-name my-pod-sg \
  --description "Security group for my-app pods" \
  --vpc-id vpc-0123456789abcdef0

# Note the GroupId returned, e.g.: sg-0abc123def456789
```

Add rules as needed, e.g., allow inbound PostgreSQL from within the VPC:

```bash
aws ec2 authorize-security-group-ingress \
  --group-id sg-0abc123def456789 \
  --protocol tcp \
  --port 5432 \
  --cidr 10.0.0.0/16
```

### Step 3: Create a `SecurityGroupPolicy` CRD

EKS introduces a custom resource `SecurityGroupPolicy` to associate pods with security groups:

```yaml
apiVersion: vpcresources.k8s.aws/v1beta1
kind: SecurityGroupPolicy
metadata:
  name: my-app-sgp
  namespace: default
spec:
  podSelector:
    matchLabels:
      app: my-app        # matches pods with this label
  securityGroups:
    groupIds:
      - sg-0abc123def456789   # your security group ID
```

Apply it:

```bash
kubectl apply -f my-app-sgp.yaml
```

### Step 4: Deploy Your Pod with the Matching Label

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
        app: my-app     # must match podSelector in SecurityGroupPolicy
    spec:
      containers:
        - name: my-app
          image: nginx:latest
          ports:
            - containerPort: 80
```

Apply:

```bash
kubectl apply -f my-app-deployment.yaml
```

### Step 5: Verify the Branch ENI is Attached

```bash
# Check the pod annotation — VPC CNI adds ENI info here
kubectl describe pod <pod-name> -n default | grep -A5 Annotations

# Look for:
# vpc.amazonaws.com/pod-eni: [{"eniId":"eni-xxx","ifAddress":"xx:xx:xx:xx:xx:xx","privateIp":"10.x.x.x","vlanId":1,"subnetCidr":"10.x.x.x/24"}]
```

---

## 6. Terraform Example

If you manage EKS with Terraform, here's how to wire it all up:

```hcl
# Security group for pods
resource "aws_security_group" "pod_sg" {
  name        = "my-app-pod-sg"
  description = "SG for my-app pods"
  vpc_id      = var.vpc_id

  ingress {
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = [var.vpc_cidr]
    description = "Allow PostgreSQL from within VPC"
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "my-app-pod-sg"
  }
}

# Enable Pod ENI on VPC CNI
resource "null_resource" "enable_pod_eni" {
  provisioner "local-exec" {
    command = <<EOT
      kubectl set env daemonset aws-node \
        -n kube-system \
        ENABLE_POD_ENI=true \
        --kubeconfig=${var.kubeconfig_path}
    EOT
  }

  depends_on = [module.eks]
}
```

---

## 7. Node Group Security Groups via Terraform (eksctl / managed node group)

```hcl
resource "aws_eks_node_group" "workers" {
  cluster_name    = aws_eks_cluster.main.name
  node_group_name = "workers"
  node_role_arn   = aws_iam_role.node.arn
  subnet_ids      = var.private_subnet_ids

  scaling_config {
    desired_size = 3
    max_size     = 5
    min_size     = 1
  }

  # Attach additional SGs to nodes in this group
  # (cluster SG is always attached automatically)
  remote_access {
    ec2_ssh_key               = var.ssh_key_name
    source_security_group_ids = [aws_security_group.bastion_sg.id]
  }
}
```

---

## 8. Common Use Cases

| Use Case | Approach |
|----------|----------|
| Allow pods to connect to RDS | Create SG allowing port 5432, attach via `SecurityGroupPolicy` |
| Restrict which pods reach ElastiCache | Use SGP with specific `podSelector` labels |
| Isolate node groups from each other | Use separate SGs per node group, remove self-referencing rules |
| Allow bastion SSH to nodes | Add bastion SG as source on port 22 inbound to node SG |
| Control plane to kubelet | Ensure port 10250 is open from the cluster SG |

---

## 9. Troubleshooting

### Pod stuck in `Pending` with SGP

```bash
# Check VPC CNI logs
kubectl logs -n kube-system -l k8s-app=aws-node --tail=50

# Common causes:
# - Instance type doesn't support branch ENIs (not Nitro)
# - ENABLE_POD_ENI not set
# - Insufficient ENI capacity on the node
```

### Check ENI limits per instance type

```bash
aws ec2 describe-instance-types \
  --instance-types m5.large \
  --query 'InstanceTypes[*].NetworkInfo.{MaxENIs:MaximumNetworkInterfaces,MaxIPs:Ipv4AddressesPerInterface}'
```

### Connectivity issues between pods

```bash
# Confirm SecurityGroupPolicy is matching correctly
kubectl get securitygrouppolicy -n default -o yaml

# Confirm the pod has the right labels
kubectl get pod <pod-name> --show-labels
```

---

## 10. Key Gotchas

1. **Branch ENI limits** — each Nitro instance has a maximum number of branch ENIs. Check [AWS docs](https://docs.aws.amazon.com/eks/latest/userguide/security-groups-for-pods.html) for limits per instance type.
2. **Windows nodes** — SGP is not supported on Windows worker nodes.
3. **Fargate** — Fargate pods get their own ENI automatically; SGP works differently there.
4. **Policy conflicts** — if you also use Kubernetes `NetworkPolicy`, both layers apply. Traffic must pass both.
5. **Orphaned ENIs** — if pods crash or nodes are terminated ungracefully, branch ENIs can be left dangling. The VPC CNI has cleanup logic, but monitor for orphaned ENIs in AWS console.

---

## 11. Summary

```
EKS Security Groups at a glance:
──────────────────────────────────────────────────────
Cluster SG       → auto-created, applied to control plane + all nodes
Node Group SGs   → additional SGs on specific node groups
SGP (pod-level)  → branch ENI per pod, Nitro instances only

Setup flow for SGP:
  1. Enable ENABLE_POD_ENI on aws-node DaemonSet
  2. Create AWS Security Group with desired rules
  3. Create SecurityGroupPolicy CRD linking labels → SG
  4. Deploy pods with matching labels
  5. Verify via pod annotations and aws-node logs
──────────────────────────────────────────────────────
```


