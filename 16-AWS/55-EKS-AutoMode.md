# EKS Auto Mode: Fully Managed Kubernetes Nodes

> EKS Auto Mode extends AWS-managed operations to the data plane — compute, networking, and storage are provisioned and managed automatically. You define workloads; AWS handles node lifecycle, patching, scaling, and IAM wiring.

---

## What EKS Auto Mode Does

| Without Auto Mode | With Auto Mode |
|---|---|
| You create and manage node groups | AWS provisions nodes on demand |
| You patch and upgrade nodes | AWS handles OS patching |
| You configure kube-proxy, VPC CNI | AWS manages all node add-ons |
| You create instance profiles manually | AWS manages instance profiles |
| You set up cluster autoscaler | Built-in node autoscaling |

---

## IAM Roles Required

EKS Auto Mode requires two IAM roles: a **Cluster Role** and a **Node Role**.

### Cluster IAM Role

Used by the EKS control plane to manage cluster resources on your behalf.

**Trust policy:**

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": { "Service": "eks.amazonaws.com" },
    "Action": ["sts:AssumeRole", "sts:TagSession"]
  }]
}
```

**Required policies (attach all 5):**

```bash
aws iam create-role \
  --role-name AmazonEKSAutoClusterRole \
  --assume-role-policy-document file://cluster-trust-policy.json

for policy in \
  arn:aws:iam::aws:policy/AmazonEKSClusterPolicy \
  arn:aws:iam::aws:policy/AmazonEKSComputePolicy \
  arn:aws:iam::aws:policy/AmazonEKSBlockStoragePolicy \
  arn:aws:iam::aws:policy/AmazonEKSLoadBalancingPolicy \
  arn:aws:iam::aws:policy/AmazonEKSNetworkingPolicy; do
  aws iam attach-role-policy \
    --role-name AmazonEKSAutoClusterRole \
    --policy-arn $policy
done
```

### Node IAM Role

Used by EC2 instances running as Kubernetes worker nodes.

**Trust policy:**

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": { "Service": "ec2.amazonaws.com" },
    "Action": "sts:AssumeRole"
  }]
}
```

**Required policies:**

```bash
aws iam create-role \
  --role-name AmazonEKSAutoNodeRole \
  --assume-role-policy-document file://node-trust-policy.json

aws iam attach-role-policy \
  --role-name AmazonEKSAutoNodeRole \
  --policy-arn arn:aws:iam::aws:policy/AmazonEKSWorkerNodeMinimalPolicy

aws iam attach-role-policy \
  --role-name AmazonEKSAutoNodeRole \
  --policy-arn arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryPullOnly
```

---

## Creating an EKS Auto Mode Cluster

```bash
aws eks create-cluster \
  --name my-auto-cluster \
  --region us-east-1 \
  --kubernetes-version 1.31 \
  --role-arn arn:aws:iam::ACCOUNT_ID:role/AmazonEKSAutoClusterRole \
  --resources-vpc-config subnetIds=subnet-aaa,subnet-bbb,securityGroupIds=sg-xxx \
  --compute-config enabled=true,nodePools=[general-purpose,system],nodeRoleArn=arn:aws:iam::ACCOUNT_ID:role/AmazonEKSAutoNodeRole \
  --kubernetes-network-config elasticLoadBalancing={enabled=true} \
  --storage-config blockStorage={enabled=true} \
  --access-config authenticationMode=API
```

---

## Access Entry for Nodes (Required)

EKS Auto Mode uses Access Entries — the `aws-auth` ConfigMap is **not used**.

```bash
# Create access entry for the node role
aws eks create-access-entry \
  --cluster-name my-auto-cluster \
  --principal-arn arn:aws:iam::ACCOUNT_ID:role/AmazonEKSAutoNodeRole \
  --type EC2

# Associate the Auto Mode node policy
aws eks associate-access-policy \
  --cluster-name my-auto-cluster \
  --principal-arn arn:aws:iam::ACCOUNT_ID:role/AmazonEKSAutoNodeRole \
  --policy-arn arn:aws:eks::aws:cluster-access-policy/AmazonEKSAutoNodePolicy \
  --access-scope type=cluster
```

---

## Custom Node Classes

Use custom NodeClass resources when you need nodes with specific configuration (instance types, subnets, security groups, or a custom IAM role).

### Step 1: Create a custom Node IAM Role

```bash
aws iam create-role \
  --role-name CustomNodeClassRole \
  --assume-role-policy-document file://node-trust-policy.json

aws iam attach-role-policy \
  --role-name CustomNodeClassRole \
  --policy-arn arn:aws:iam::aws:policy/AmazonEKSWorkerNodeMinimalPolicy

aws iam attach-role-policy \
  --role-name CustomNodeClassRole \
  --policy-arn arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryPullOnly

# Create instance profile (required for custom node classes)
aws iam create-instance-profile \
  --instance-profile-name CustomNodeClassInstanceProfile

aws iam add-role-to-instance-profile \
  --instance-profile-name CustomNodeClassInstanceProfile \
  --role-name CustomNodeClassRole
```

### Step 2: Register the node role as an Access Entry

```bash
aws eks create-access-entry \
  --cluster-name my-auto-cluster \
  --principal-arn arn:aws:iam::ACCOUNT_ID:role/CustomNodeClassRole \
  --type EC2

aws eks associate-access-policy \
  --cluster-name my-auto-cluster \
  --principal-arn arn:aws:iam::ACCOUNT_ID:role/CustomNodeClassRole \
  --policy-arn arn:aws:eks::aws:cluster-access-policy/AmazonEKSAutoNodePolicy \
  --access-scope type=cluster
```

### Step 3: Create the NodeClass

```yaml
# custom-nodeclass.yaml
apiVersion: eks.amazonaws.com/v1
kind: NodeClass
metadata:
  name: custom-class
spec:
  role: CustomNodeClassRole        # or use instanceProfile: CustomNodeClassInstanceProfile
  subnetSelectorTerms:
    - tags:
        kubernetes.io/role/internal-elb: "1"
  securityGroupSelectorTerms:
    - tags:
        eks.cluster: my-auto-cluster
  amiSelectorTerms:
    - alias: al2023@latest
  tags:
    Environment: production
```

```bash
kubectl apply -f custom-nodeclass.yaml
```

### Step 4: Create a NodePool referencing the NodeClass

```yaml
# custom-nodepool.yaml
apiVersion: karpenter.sh/v1
kind: NodePool
metadata:
  name: custom-pool
spec:
  template:
    spec:
      nodeClassRef:
        group: eks.amazonaws.com
        kind: NodeClass
        name: custom-class
      requirements:
        - key: kubernetes.io/arch
          operator: In
          values: ["amd64"]
        - key: karpenter.sh/capacity-type
          operator: In
          values: ["on-demand"]
  limits:
    cpu: "100"
    memory: 400Gi
  disruption:
    consolidationPolicy: WhenEmptyOrUnderutilized
    consolidateAfter: 1m
```

```bash
kubectl apply -f custom-nodepool.yaml
```

---

## Terraform Example

```hcl
# Cluster access entry for default node role
resource "aws_eks_access_entry" "node" {
  cluster_name  = var.cluster_name
  principal_arn = aws_iam_role.node.arn
  type          = "EC2"
}

resource "aws_eks_access_policy_association" "node_policy" {
  cluster_name  = var.cluster_name
  principal_arn = aws_iam_role.node.arn
  policy_arn    = "arn:aws:eks::aws:cluster-access-policy/AmazonEKSAutoNodePolicy"

  access_scope {
    type = "cluster"
  }

  depends_on = [aws_eks_access_entry.node]
}

# Custom node class access entry
resource "aws_eks_access_entry" "custom_nodeclass" {
  cluster_name  = var.cluster_name
  principal_arn = aws_iam_role.custom_nodeclass_role.arn
  type          = "EC2"
}

resource "aws_eks_access_policy_association" "custom_nodeclass_policy" {
  cluster_name  = var.cluster_name
  principal_arn = aws_iam_role.custom_nodeclass_role.arn
  policy_arn    = "arn:aws:eks::aws:cluster-access-policy/AmazonEKSAutoNodePolicy"

  access_scope {
    type = "cluster"
  }

  depends_on = [aws_eks_access_entry.custom_nodeclass]
}
```

---

## Setup Workflow Summary

| Phase | Steps |
|---|---|
| **1. Cluster IAM Role** | Create role with 5 managed policies |
| **2. Node IAM Role** | Create role with 2 managed policies |
| **3. Create Cluster** | Enable compute, storage, load balancing |
| **4. Access Entries** | Register node role as EC2 type with AmazonEKSAutoNodePolicy |
| **5. Custom NodeClass** | (Optional) Create role + instance profile + NodeClass + NodePool |
| **6. Deploy Workloads** | `kubectl apply` — nodes provision on demand |

---

## Important Notes

- **Access Entries are required** — aws-auth ConfigMap is not supported in Auto Mode
- **Instance profile naming** for custom classes must start with `eks-` if your SCPs enforce it; otherwise use the role name directly via `spec.role`
- Changing the IAM role in a NodeClass requires a new Access Entry
- Use **EKS Pod Identity** for pod-level AWS permissions rather than adding policies to the node role
- You can have **multiple NodeClasses** each with its own role for workload isolation

---

## Summary

EKS Auto Mode delivers a fully managed Kubernetes experience by extending AWS control to the data plane. Set up the two required IAM roles, enable compute/storage/networking at cluster creation, and create Access Entries for the node role — then deploy workloads and let AWS handle the rest.
