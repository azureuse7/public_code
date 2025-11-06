##### IAM role
- Clustre IAM role: This role grants Amazon EKS the necessary permissions to interact with other AWS services on behalf of your cluster,(Trust: eks.amazonaws.com with sts:AssumeRole and sts:TagSession.) 

- Node IAM role: This role grants EC2 instances running as Kubernetes nodes the necessary permissions to interact with AWS services and resources, 

##### Attach policy 
- Clustre IAM --> 4 

- Node IAM role ---> 2


##### Access Entry -> s
- Clustre IAM role : No, Access entries are for IAM principals that authenticate to the Kubernetes API (humans, automation, nodes). The cluster role is a service role and doesn’t need (or use) an access entry. 

- Node IAM EKS:  You need to create an EKS Access Entry to permit the nodes to join the cluster. Create an Access Entry of type EC2 for the node role 
ss
##### EKS Access Entry + Policy Association
- Clustre IAM role: Not applicable for the cluster role.

- Node IAM role : associate the EKS access policy AmazonEKSAutoNodePolicy at cluster scope so nodes can join.


##### Instance profile – Usually yes (one of two ways).

- Clustre IAM role: For the Cluster IAM Role, you do NOT need to create an instance profile. Here's why:
The cluster IAM role is a service role that is assumed by the EKS service (eks.amazonaws.com), not by EC2 instances AWS. This role allows Amazon EKS to manage cluster resources on your behalf.
the IAM role name, and EKS Auto Mode will handle the instance profile creation for you

- Node IAM role : In the NodeClass you can set either spec.role or spec.instanceProfile (mutually exclusive). If you supply role, EKS can manage the instance profile for you; if your org’s SCPs are strict, pre-create an instance profile (name must start with eks-) and set instanceProfile instead.

   



Each custom node class can have its own IAM role (or you can reuse one across multiple custom node classes)
Requires manual EKS Access Entry creation with the AmazonEKSAutoNodePolicy access policy
Same IAM policies as the default node role, but requires additional configuration


##### Step 1: Create the IAM role (same as default node role)
``` 
bashaws iam create-role \
  --role-name CustomNodeClassRole \
  --assume-role-policy-document file://node-trust-policy.json \
  --description "Custom Node Class role for EKS Auto Mode"
``` 
#### Step 2: Attach required policies
``` 
bashaws iam attach-role-policy \
  --role-name CustomNodeClassRole \
  --policy-arn arn:aws:iam::aws:policy/AmazonEKSWorkerNodeMinimalPolicy

aws iam attach-role-policy \
  --role-name CustomNodeClassRole \
  --policy-arn arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryPullOnly
  ``` 
##### Step 3: Create an EC2 instance profile (required for custom node classes)
``` 
bashaws iam create-instance-profile \
  --instance-profile-name CustomNodeClassInstanceProfile

aws iam add-role-to-instance-profile \
  --instance-profile-name CustomNodeClassInstanceProfile \
  --role-name CustomNodeClassRole
  ``` 
#### Step 4: Get the role ARN for use in NodeClass YAML
``` 
bashaws iam get-role --role-name CustomNodeClassRole --query 'Role.Arn' --output text
``` 
- EKS Access Entry Configuration (REQUIRED for Custom Node Classes)
- When creating access entries for EKS Auto Mode node classes, you need to use the EC2 access entry type and associate the EKS Auto Node Policy. AWSTrevorrobertsjr

##### Step 1: Create the access entry
``` 
bashaws eks create-access-entry \
  --cluster-name <your-cluster-name> \
  --principal-arn arn:aws:iam::<account-id>:role/CustomNodeClassRole \
  --type EC2
  ``` 
#### Step 2: Associate the AmazonEKSAutoNodePolicy
``` 
bashaws eks associate-access-policy \
  --cluster-name <your-cluster-name> \
  --principal-arn arn:aws:iam::<account-id>:role/CustomNodeClassRole \
  --policy-arn arn:aws:eks::aws:cluster-access-policy/AmazonEKSAutoNodePolicy \
  --access-scope type=cluster
``` 
##### Terraform Example
``` 
hclresource "aws_eks_access_entry" "custom_nodeclass_entry" {
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


Complete Setup Workflow
Prerequisites

AWS CLI installed and configured
kubectl installed
Appropriate IAM permissions to create roles and policies
An existing VPC with subnets

Step-by-Step Setup
Phase 1: Create Cluster IAM Role

Create trust policy file
Create the AmazonEKSAutoClusterRole
Attach all 5 required managed policies
(Optional) Attach custom tagging policy

Phase 2: Create Default Node IAM Role

Create node trust policy file
Create the AmazonEKSAutoNodeRole
Attach the 2 required managed policies

Phase 3: Create EKS Cluster

Phase 4: Create Custom Node Class IAM Role


Phase 5: Configure EKS Access Entry

Create EC2 type access entry for the custom node role
Associate AmazonEKSAutoNodePolicy access policy

Phase 6: Create Custom NodeClass

Create NodeClass YAML with custom role reference
Apply with kubectl apply -f nodeclass.yaml

Phase 7: Create Custom NodePool

Create NodePool YAML referencing your custom NodeClass
Apply with kubectl apply -f nodepool.yaml


Important Considerations

Access Entry Requirement: If you change the node IAM role associated with a NodeClass, you will need to create a new Access Entry AWS
Multiple Custom Node Classes: You can create multiple custom node classes, each with its own IAM role, or reuse the same role across multiple node classes
Built-in vs Custom: EKS automatically creates an Access Entry for the default node IAM role during cluster creation or when you create the built-in nodeclass and nodepools AWS re:Post
Tagging: If you need custom tags on AWS resources provisioned by Auto Mode, add the custom tagging policy to your Cluster IAM Role
Pod Identity: For workload-level permissions, use EKS Pod Identity instead of attaching additional policies to the node role


This comprehensive setup ensures your EKS Auto Mode cluster with custom node classes has all the necessary IAM roles and permissions configured correctly!Retry