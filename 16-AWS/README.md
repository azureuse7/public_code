# Amazon Web Services (AWS)

> Reference guides for core AWS services — covering compute, networking, storage, databases, security, serverless, containers, and monitoring.

---

## Contents

| File | Service | Category |
|------|---------|----------|
| [02-IAM.md](02-IAM.md) | IAM | Security & Identity |
| [03-EC2.md](03-EC2.md) | EC2 | Compute |
| [04-VPC.md](04-VPC.md) | VPC | Networking |
| [06-Security.md](06-Security.md) | Security Groups & NACL | Networking |
| [09-EKS.md](09-EKS.md) | EKS | Containers |
| [10-CloudWatch.md](10-CloudWatch.md) | CloudWatch | Monitoring |
| [12-DynamoDB.md](12-DynamoDB.md) | DynamoDB | Database |
| [13-ELB.md](13-ELB.md) | Elastic Load Balancing | Networking |
| [14-Fargate.md](14-Fargate.md) | Fargate | Containers |
| [15-Lambda.md](15-Lambda.md) | Lambda | Serverless |
| [16-Lightsail.md](16-Lightsail.md) | Lightsail | Compute |
| [17-RDS.md](17-RDS.md) | RDS | Database |
| [18-Route-53.md](18-Route-53.md) | Route 53 | DNS |
| [19-S3.md](19-S3.md) | S3 | Storage |
| [20-SecurityGroupd.md](20-SecurityGroupd.md) | Security Groups | Security |
| [21-WAF.md](21-WAF.md) | WAF | Security |
| [22-Direct-Connect.md](22-Direct-Connect.md) | Direct Connect | Networking |
| [23-CloudFront.md](23-CloudFront.md) | CloudFront | CDN |
| [25-Config.md](25-Config.md) | AWS Config | Governance |
| [26-Amazon EBS.md](26-Amazon%20EBS.md) | EBS | Storage |
| [27-AWS CloudFormation.md](27-AWS%20CloudFormation.md) | CloudFormation | IaC |
| [28-AWS SSM Parameter.md](28-AWS%20SSM%20Parameter.md) | SSM Parameter Store | Secrets |
| [29-AWS Step Functions.md](29-AWS%20Step%20Functions.md) | Step Functions | Serverless |
| [30-Aws-Step_function-and-lamba.md](30-Aws-Step_function-and-lamba.md) | Step Functions + Lambda | Serverless |
| [31-CloudFront.md](31-CloudFront.md) | CloudFront (detailed) | CDN |
| [36-Access-Entry.md](36-Access-Entry.md) | EKS Access Entry | Containers |
| [37InstanceProfile.md](37InstanceProfile.md) | EC2 Instance Profile | Security |
| [38-EKS OIDC.md](38-EKS%20OIDC.md) | EKS OIDC / IRSA | Containers |
| [39-kube-proxy.md](39-kube-proxy.md) | kube-proxy on EKS | Containers |
| [40NodeClass & NodePool.md](40NodeClass%20%26%20NodePool.md) | EKS NodeClass & NodePool | Containers |
| [41-Amazon VPC CNI.md](41-Amazon%20VPC%20CNI.md) | VPC CNI | Networking |
| [43-aws-auth.md](43-aws-auth.md) | aws-auth ConfigMap | Containers |
| [50-Trustpolicy.md](50-Trustpolicy.md) | IAM Trust Policies | Security |
| [55-EKS-AutoMode.md](55-EKS-AutoMode.md) | EKS Auto Mode | Containers |

---

## Service Overview

### Compute
| Service | When to use |
|---------|------------|
| EC2 | Full control over the OS, persistent workloads, lift-and-shift |
| Fargate | Containers without managing nodes |
| Lambda | Event-driven, short-lived functions |
| Lightsail | Simple VPS for small projects |

### Networking
| Service | Purpose |
|---------|---------|
| VPC | Isolated virtual network |
| Security Groups | Stateful firewall per resource |
| NACL | Stateless firewall per subnet |
| ELB | Distribute traffic (ALB layer 7, NLB layer 4) |
| Route 53 | DNS routing and health checks |
| CloudFront | CDN — cache content at edge locations |
| Direct Connect | Dedicated private link from on-premises to AWS |

### Storage
| Service | Type |
|---------|------|
| S3 | Object storage — files, backups, static sites |
| EBS | Block storage — attached to a single EC2 instance |
| EFS | Shared file storage — multiple EC2 instances |

### Database
| Service | Type |
|---------|------|
| RDS | Managed relational (MySQL, PostgreSQL, SQL Server, Aurora) |
| DynamoDB | Serverless NoSQL key-value / document store |

### Security
| Service | Purpose |
|---------|---------|
| IAM | Authentication and authorisation for all AWS resources |
| WAF | Block malicious web requests |
| AWS Config | Audit and compliance — track config changes |

---

## IAM Cheat Sheet

```bash
# List all users
aws iam list-users

# Get current identity
aws sts get-caller-identity

# Attach a policy to a role
aws iam attach-role-policy \
  --role-name MyRole \
  --policy-arn arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess

# Create an inline policy
aws iam put-role-policy \
  --role-name MyRole \
  --policy-name MyPolicy \
  --policy-document file://policy.json
```
