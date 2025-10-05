



**1. What is EKS OIDC (IRSA)?**

-   **OpenID Connect (OIDC)** is an identity layer on top of OAuth 2.0.
    It lets a relying party (AWS IAM, in our case) verify the identity
    of a caller and obtain basic profile information.

-   **EKS OIDC provider**: Every EKS cluster can expose an OIDC issuer
    URL. AWS IAM can treat that URL as an external identity provider.

-   **IAM Roles for Service Accounts (IRSA)**: Kubernetes service
    accounts get mapped to IAM roles. When a pod runs under that service
    account, it automatically receives temporary AWS credentials with
    the IAM role's permissions---no static EC2 instance role or
    long-lived access keys needed.

**Why use it?**

-   **Fine-grained permissions**: Each microservice (pod) can have
    exactly the permissions it needs.

-   **Better security**: No need for node-wide instance roles.

-   **Automatic rotation**: Uses Kubernetes' projected service account
    token and AWS STS web identity federation.

**2. How it works under the hood**

1.  **Cluster OIDC issuer**\
    When you create an EKS cluster, it publishes an OIDC issuer URL,
    e.g.:
    sh
```
https://oidc.eks.us-west-2.amazonaws.com/id/ABCD1234EFGH5678IJKL
sh
```
2.  **IAM OpenID Connect provider**\
    In IAM you create an OIDC provider pointing to that URL, with the
    cluster's TLS thumbprint.

4.  **IAM role with trust policy**\
    You create an IAM role whose **trust policy** allows
    sts:AssumeRoleWithWebIdentity if the incoming token's issuer matches
    your cluster's OIDC provider and the sub claim equals
    system:serviceaccount:\<namespace\>:\<serviceaccount\>.

5.  **Annotate K8s ServiceAccount**\
    In Kubernetes you create a ServiceAccount and annotate it with the
    IAM role's ARN.\
    EKS injects a projected token into pods using that SA.

6.  **Pod uses AWS SDK**\
    The AWS SDK inside the pod automatically detects the projected token
    file and calls AWS STS to assume the IAM role, retrieving
    short-lived credentials.

**3. End-to-End Example**

We'll build a simple workflow where a pod reads from an S3 bucket. We'll
use eksctl for brevity, but you can also do each step by hand with the
AWS CLI.

**Prerequisites**

-   eksctl, kubectl, and AWS CLI configured with permissions to manage
    EKS and IAM.

-   An existing EKS cluster, or create one:
sh
```
eksctl create cluster \
  --name my-cluster \
  --region us-west-2 \
  --with-oidc \
  --nodes 2 \
  --approve
```
This automatically creates and associates the OIDC provider for you.

**3.1 Create an IAM policy**

Define an S3-read policy:


```
# s3-read-policy.json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": ["s3:GetObject", "s3:ListBucket"],
    "Resource": [
      "arn:aws:s3:::my-secure-bucket",
      "arn:aws:s3:::my-secure-bucket/*"
    ]
  }]
}

```
Create the policy:
sh
```
aws iam create-policy \
  --policy-name EKSReadMyBucket \
  --policy-document file://s3-read-policy.json

```
Take note of the returned Arn, e.g.
arn:aws:iam::111122223333:policy/EKSReadMyBucket.

**3.2 Create an IAM role for the ServiceAccount**

First, get your cluster's OIDC issuer ARN:
sh
```
aws eks describe-cluster \
  --name my-cluster \
  --region us-west-2 \
  --query "cluster.identity.oidc.issuer" \
  --output text

# Output: https://oidc.eks.us-west-2.amazonaws.com/id/ABCD1234EFGH5678IJKL

```

Then build a trust policy (trust.json):
sh
```
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": {
      "Federated": "arn:aws:iam::111122223333:oidc-provider/oidc.eks.us-west-2.amazonaws.com/id/ABCD1234EFGH5678IJKL"
    },
    "Action": "sts:AssumeRoleWithWebIdentity",
    "Condition": {
      "StringEquals": {
        "oidc.eks.us-west-2.amazonaws.com/id/ABCD1234EFGH5678IJKL:sub":
          "system:serviceaccount:demo:read-s3-sa"
      }
    }
  }]
}

```
Create the role:
```
aws iam create-role \
  --role-name EKS-S3ReadRole \
  --assume-role-policy-document file://trust.json

```
Attach the policy:
```
aws iam attach-role-policy \
  --role-name EKS-S3ReadRole \
  --policy-arn arn:aws:iam::111122223333:policy/EKSReadMyBucket

```
**3.3 Create the Kubernetes ServiceAccount**

\# sa-read-s3.yaml
sh
```
# sa-read-s3.yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: read-s3-sa
  namespace: demo
  annotations:
    eks.amazonaws.com/role-arn: arn:aws:iam::111122223333:role/EKS-S3ReadRole

```
Apply:

```
kubectl create namespace demo

kubectl apply -f sa-read-s3.yaml

```
**3.4 Deploy a Pod that Uses It**

Example Python app that lists bucket contents:

\# pod-list-s3.yaml
sh
```
apiVersion: v1

kind: Pod

metadata:

name: list-s3

namespace: demo

spec:

serviceAccountName: read-s3-sa

containers:

\- name: aws-cli

image: amazonlinux

command: \[\"sh\",\"-c\"\]

args:

\- yum install -y aws-cli python3 && \\

aws s3 ls s3://my-secure-bucket
sh
```
Deploy and inspect logs:
sh
```
kubectl apply -f pod-list-s3.yaml

kubectl logs -n demo pod/list-s3
sh
```
\# You should see the bucket contents listed

Behind the scenes:

-   The pod's projected token
    (/var/run/secrets/eks.amazonaws.com/serviceaccount/token) is
    presented to STS.

-   The AWS CLI automatically picks up AWS_ROLE_ARN and
    AWS_WEB_IDENTITY_TOKEN_FILE.

-   STS returns short-lived credentials scoped to S3 read access.

**4. Key Takeaways**

-   **Security**: No long-lived credentials in pods or node IAM roles
    that are too permissive.

-   **Granularity**: Each ServiceAccount can map to its own IAM role
    with exactly the permissions it needs.

-   **Automation**: eksctl can automate OIDC provider setup; you can
    also configure manually via AWS CLI.

This pattern scales to any AWS API: RDS, DynamoDB, SQS, Secrets Manager,
etc. Once you've defined the OIDC provider and trust policy, just create
the right IAM policy + role, annotate your ServiceAccount, and your pods
get secure access automatically.
