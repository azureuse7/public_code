# EKS


# Access Keys (for Programmatic Access):

If you selected "Programmatic access" during user creation, you will receive access keys (Access Key ID and Secret Access Key).

Store these access keys securely, as they will be used to authenticate API requests made to AWS services.

2.2 Configuring the AWS CLI and kubectl
 

# Installing the AWS CLI:

- Configuring AWS CLI Credentials:

- Open a terminal or command prompt and run the following command:



aws configure
Enter the access key ID and secret access key of the IAM user you created earlier.

Choose a default region and output format for AWS CLI commands.

Installing kubectl:

Configuring kubectl for EKS and Eksctl

Once kubectl is installed, you need to configure it to work with your EKS cluster.

In the AWS Management Console, go to the EKS service and select your cluster.

Click on the "Config" button and follow the instructions to update your kubeconfig file. Alternatively, you can use the AWS CLI to update the kubeconfig file:



aws eks update-kubeconfig --name your-cluster-name
Verify the configuration by running a kubectl command against your EKS cluster:



kubectl get nodes
 

# Create Fargate profile


eksctl create fargateprofile \
    --cluster demo-cluster \
    --region us-east-1 \
    --name alb-sample-app \
    --namespace game-2048
Once this is done 

<img src="images/5.png">
 

Deploy the deployment, service and Ingress
 



kubectl apply -f https://raw.githubusercontent.com/kubernetes-sigs/aws-load-balancer-controller/v2.5.4/docs/examples/2048/2048_full.yaml
 

- Notice no external IP 

- We have installed ingress resources but 

- We have no ingress controller 

- It will create an configure a load balancer

 

# commands to configure IAM OIDC provider


export cluster_name=demo-cluster


oidc_id=$(aws eks describe-cluster --name $cluster_name --query "cluster.identity.oidc.issuer" --output text | cut -d '/' -f 5) 
 

 

<img src="images/6.png">
 

Check if there is an IAM OIDC provider configured already
aws iam list-open-id-connect-providers | grep $oidc_id | cut -d "/" -f4\n

If not, run the below command



eksctl utils associate-iam-oidc-provider --cluster $cluster_name --approve
 

# How to setup alb add on

- Download IAM policy


curl -O https://raw.githubusercontent.com/kubernetes-sigs/aws-load-balancer-controller/v2.5.4/docs/install/iam_policy.json

- Create IAM Policy


aws iam create-policy \
    --policy-name AWSLoadBalancerControllerIAMPolicy \
    --policy-document file://iam_policy.json

- Create IAM Role


eksctl create iamserviceaccount \
  --cluster=<your-cluster-name> \
  --namespace=kube-system \
  --name=aws-load-balancer-controller \
  --role-name AmazonEKSLoadBalancerControllerRole \
  --attach-policy-arn=arn:aws:iam::<your-aws-account-id>:policy/AWSLoadBalancerControllerIAMPolicy \
  --approve


- Deploy ALB controller
Add helm repo


helm repo add eks https://aws.github.io/eks-charts

Update the repo


helm repo update eks

Install



helm install aws-load-balancer-controller eks/aws-load-balancer-controller \            
  -n kube-system \
  --set clusterName=<your-cluster-name> \
  --set serviceAccount.create=false \
  --set serviceAccount.name=aws-load-balancer-controller \
  --set region=<region> \
  --set vpcId=<your-vpc-id>
Verify that the deployments are running.



kubectl get deployment -n kube-system aws-load-balancer-controller
 

# 2.3 Preparing Networking and Security Groups for EKS
Before launching an EKS cluster, you need to prepare the networking and security groups to ensure proper communication and security within the cluster:

# Creating an Amazon VPC (Virtual Private Cloud):

- Go to the AWS Management Console and navigate to the VPC service.

- Click on "Create VPC" and enter the necessary details like VPC name, IPv4 CIDR block, and subnets.

- Create public and private subnets to distribute resources in different availability zones.

- Sure! Let's go into detail for each of the points:

# Configuring Security Groups

- Security Groups are a fundamental aspect of Amazon Web Services (AWS) that act as virtual firewalls for your AWS resources, including Amazon Elastic Kubernetes Service (EKS) clusters. Security Groups control inbound and outbound traffic to and from these resources based on rules you define. Here's a step-by-step guide on configuring Security Groups for your EKS cluster:

# Create a Security Group:

- Go to the AWS Management Console and navigate to the Amazon VPC service.

- Click on "Security Groups" in the left-hand navigation pane.

- Click on "Create Security Group."

- Provide a name and description for the Security Group.

- Select the appropriate VPC for the Security Group.

# Inbound Rules:

- Define inbound rules to control incoming traffic to your EKS worker nodes.

- By default, all inbound traffic is denied unless you explicitly allow it.

- Common inbound rules include allowing SSH (port 22) access for administrative purposes and allowing ingress traffic from specific CIDR blocks or Security Groups.

# Outbound Rules:

- Define outbound rules to control the traffic leaving your EKS worker nodes.

- By default, all outbound traffic is allowed unless you explicitly deny it.

- For security purposes, you can restrict outbound traffic to specific destinations or ports.

# Security Group IDs:

 After creating the Security Group, you'll receive a Security Group ID. This ID will be used when launching your EKS worker nodes.

Attach Security Group to EKS Worker Nodes:

When launching the EKS worker nodes, specify the Security Group ID in the launch configuration. This associates the Security Group with the worker nodes, allowing them to communicate based on the defined rules.

Configuring Security Groups ensures that only the necessary traffic is allowed to and from your EKS worker nodes, enhancing the security of your EKS cluster.

# Setting Up Internet Gateway (IGW)

- An Internet Gateway (IGW) is a horizontally scaled, redundant, and highly available AWS resource that allows communication between your VPC and the internet. To enable EKS worker nodes to access the internet for tasks like pulling container images, you need to set up an Internet Gateway in your VPC. Here's how to do it:

# Create an Internet Gateway:

- Go to the AWS Management Console and navigate to the Amazon VPC service.

- Click on "Internet Gateways" in the left-hand navigation pane.

- Click on "Create Internet Gateway."

- Provide a name for the Internet Gateway and click "Create Internet Gateway."

# Attach Internet Gateway to VPC:

- After creating the Internet Gateway, select the Internet Gateway in the list and click on "Attach to VPC."

- Choose the VPC to which you want to attach the Internet Gateway and click "Attach."

# Update Route Tables:

- Go to "Route Tables" in the Amazon VPC service.

- Identify the Route Table associated with the private subnets where your EKS worker nodes will be deployed.

- Edit the Route Table and add a route with the destination 0.0.0.0/0 (all traffic) and the Internet Gateway ID as the target.

- By setting up an Internet Gateway and updating the Route Tables, you provide internet access to your EKS worker nodes, enabling them to interact with external resources like container registries and external services.

# Configuring IAM Policies

- Identity and Access Management (IAM) is a service in AWS that allows you to manage access to AWS resources securely. IAM policies define permissions that specify what actions are allowed or denied on specific AWS resources. For your EKS cluster, you'll need to configure IAM policies to grant necessary permissions to your worker nodes and other resources. Here's how to do it:

# Create a Custom IAM Policy:

- Go to the AWS Management Console and navigate to the IAM service.

- Click on "Policies" in the left-hand navigation pane.

- Click on "Create policy."

- Choose "JSON" as the policy language and define the permissions required for your EKS cluster. For example, you might need permissions for EC2 instances, Auto Scaling, Elastic Load Balancing, and accessing ECR (Elastic Container Registry).

# Attach the IAM Policy to IAM Roles:

- Go to "Roles" in the IAM service and select the IAM role that your EKS worker nodes will assume.

- Click on "Attach policies" and search for the custom IAM policy you created in the previous step.

- Attach the policy to the IAM role.

# Update EKS Worker Node Launch Configuration:

- When launching your EKS worker nodes, specify the IAM role ARN (Amazon Resource Name) of the IAM role that includes the necessary IAM policy.

- The IAM role allows the worker nodes to authenticate with the EKS cluster and access AWS resources based on the permissions defined in the attached IAM policy.

By configuring IAM policies and associating them with IAM roles, you grant specific permissions to your EKS worker nodes, ensuring they can interact with AWS resources as needed while maintaining security and access control.

By completing these steps, your AWS environment is ready to host an Amazon EKS cluster. You can proceed with creating an EKS cluster using the AWS Management Console or AWS CLI as described in section 3.