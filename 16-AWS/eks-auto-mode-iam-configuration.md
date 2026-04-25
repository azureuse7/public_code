# EKS Auto Mode — IAM Roles & Access Configuration

## Overview of IAM Roles

There are two distinct IAM roles required for an EKS Auto Mode cluster:

**Cluster IAM Role** — Grants Amazon EKS the permissions it needs to interact with AWS services on behalf of the cluster. The trust policy allows `eks.amazonaws.com` to assume this role via `sts:AssumeRole` and `sts:TagSession`.

**Node IAM Role** — Grants EC2 instances running as Kubernetes nodes the permissions they need to interact with AWS services and resources.

---

## Policy Attachments

| Role | Managed Policies to Attach |
|---|---|
| Cluster IAM Role | 4 (+ optional custom tagging policy) |
| Node IAM Role | 2 |

---

## EKS Access Entry Requirements

| Role | Needs Access Entry? | Details |
|---|---|---|
| Cluster IAM Role | **No** | This is a service role assumed by the EKS control plane, not an authenticating principal. Access entries are for IAM principals that authenticate to the Kubernetes API (users, automation, nodes). |
| Node IAM Role | **Yes** | Create an Access Entry of type `EC2` for the node role, then associate the `AmazonEKSAutoNodePolicy` at cluster scope so nodes can join. |

---

## Instance Profile Requirements

**Cluster IAM Role** — No instance profile is needed. This role is assumed by the EKS service (`eks.amazonaws.com`), not by EC2 instances. If you supply the IAM role name during cluster creation, EKS Auto Mode handles instance profile creation automatically.

**Node IAM Role** — In a NodeClass, set either `spec.role` or `spec.instanceProfile` (these are mutually exclusive):
- Use `spec.role` to let EKS manage the instance profile for you.
- Use `spec.instanceProfile` if your organisation's SCPs are strict — in this case, pre-create an instance profile (the name must start with `eks-`) and reference it directly.

---

## Custom Node Classes

Each custom NodeClass can use its own IAM role, or share one role across multiple NodeClasses. Key differences from the default node role:

- Requires manual EKS Access Entry creation with the `AmazonEKSAutoNodePolicy` access policy.
- Requires manual EC2 instance profile creation (EKS does not create it automatically for custom NodeClasses).
- Attaches the same two IAM policies as the default node role.

### Step 1 — Create the IAM Role

```bash
aws iam create-role \
  --role-name CustomNodeClassRole \
  --assume-role-policy-document file://node-trust-policy.json \
  --description "Custom Node Class role for EKS Auto Mode"
```

### Step 2 — Attach Required Policies

```bash
aws iam attach-role-policy \
  --role-name CustomNodeClassRole \
  --policy-arn arn:aws:iam::aws:policy/AmazonEKSWorkerNodeMinimalPolicy

aws iam attach-role-policy \
  --role-name CustomNodeClassRole \
  --policy-arn arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryPullOnly
```

### Step 3 — Create an EC2 Instance Profile

> This step is required for custom NodeClasses (unlike the default node role).

```bash
aws iam create-instance-profile \
  --instance-profile-name CustomNodeClassInstanceProfile

aws iam add-role-to-instance-profile \
  --instance-profile-name CustomNodeClassInstanceProfile \
  --role-name CustomNodeClassRole
```

### Step 4 — Retrieve the Role ARN

```bash
aws iam get-role \
  --role-name CustomNodeClassRole \
  --query 'Role.Arn' \
  --output text
```

---

## EKS Access Entry Configuration

> **Required for all custom NodeClasses.** Use the `EC2` access entry type and associate the `AmazonEKSAutoNodePolicy`.

### Step 1 — Create the Access Entry

```bash
aws eks create-access-entry \
  --cluster-name <your-cluster-name> \
  --principal-arn arn:aws:iam::<account-id>:role/CustomNodeClassRole \
  --type EC2
```

### Step 2 — Associate the AmazonEKSAutoNodePolicy

```bash
aws eks associate-access-policy \
  --cluster-name <your-cluster-name> \
  --principal-arn arn:aws:iam::<account-id>:role/CustomNodeClassRole \
  --policy-arn arn:aws:eks::aws:cluster-access-policy/AmazonEKSAutoNodePolicy \
  --access-scope type=cluster
```

### Terraform Equivalent

```hcl
resource "aws_eks_access_entry" "custom_nodeclass_entry" {
  cluster_name      = var.cluster_name
  principal_arn     = aws_iam_role.custom_nodeclass_role.arn
  kubernetes_groups = []
  type              = "EC2"
}

resource "aws_eks_access_policy_association" "custom_nodeclass_policy" {
  cluster_name  = var.cluster_name
  principal_arn = aws_iam_role.custom_nodeclass_role.arn
  policy_arn    = "arn:aws:eks::aws:cluster-access-policy/AmazonEKSAutoNodePolicy"

  access_scope {
    type = "cluster"
  }

  depends_on = [aws_eks_access_entry.custom_nodeclass_entry]
}
```

---

## Complete Setup Workflow

### Prerequisites

- AWS CLI installed and configured
- `kubectl` installed
- IAM permissions to create roles and policies
- An existing VPC with subnets

### Phases

| Phase | Action |
|---|---|
| 1 | Create Cluster IAM Role — trust policy, `AmazonEKSAutoClusterRole`, attach 4 managed policies, optionally attach custom tagging policy |
| 2 | Create Default Node IAM Role — trust policy, `AmazonEKSAutoNodeRole`, attach 2 managed policies |
| 3 | Create the EKS Cluster |
| 4 | Create Custom NodeClass IAM Role (Steps 1–4 above) |
| 5 | Configure EKS Access Entry — create `EC2` type entry, associate `AmazonEKSAutoNodePolicy` |
| 6 | Create Custom NodeClass — apply NodeClass YAML referencing the role |
| 7 | Create Custom NodePool — apply NodePool YAML referencing the NodeClass |

---

## Important Considerations

**Access Entry on role change** — If you change the node IAM role associated with a NodeClass, you must create a new Access Entry for the new role.

**Multiple custom NodeClasses** — You can assign a unique IAM role per NodeClass or reuse one role across several NodeClasses.

**Built-in vs custom NodeClasses** — EKS automatically creates an Access Entry for the default node IAM role during cluster creation. Custom NodeClasses always require manual Access Entry setup.

**Custom resource tagging** — If you need custom tags on AWS resources provisioned by Auto Mode, attach a custom tagging policy to the Cluster IAM Role.

**Workload-level permissions** — Use EKS Pod Identity for per-workload AWS permissions rather than adding policies directly to the node IAM role.
