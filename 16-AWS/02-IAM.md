### IAM
Idenity and Access managment 

### Components of IAM 

##### Users:
IAM users represent individual people or entities 

##### Groups: 
- IAM groups are collections of users with similar access requirements.
- Instead of managing permissions for each user individually, you can assign permissions to groups, making it easier to manage access control.
- Users can be added or removed from groups as needed.

#### Roles: 
- IAM roles are used to grant temporary access to AWS resources. 
- Roles are typically used by applications or services that need to access AWS resources on behalf of users or other services. 
- Roles have associated policies that define the permissions and actions allowed for the role.

#### Policies: 
- IAM policies are JSON documents that define permissions. 
- Policies specify the actions that can be performed on AWS resources and the resources to which the actions apply. 
- Policies can be attached to users, groups, or roles to control access. 
- IAM provides both AWS managed policies (predefined policies maintained by AWS) and customer managed policies (policies created and managed by you).

## User 

- Create a Root user, and log in à you have full access

- Create an IAM user 
<img src="images/0.png">

- log in  You will not have any permission to do anything

- Login back as a Root user and grant S3 as below to the user. 

<img src="images/1.png">

- Log in back as IAM and notice, that you have full access to S3


## Group 
- Group: Create a group, we call we Admin

<img src="images/12.png">

- Add the user to the Group
  
<img src="images/13.png">

- Login and Notice they have access to S3

# Policies

<img src="images/14.png">

-Remove user we created from the group 
-Go to the user and add permissons "IAM read only"

<img src="images/15.png">

Add and refresh, you can see the user have permission, but can it create a group, No

<img src="images/16.png">

Becuase the user has IAM read only 

- No  I am going to create a group 
<img src="images/17.png">

Add Stpehen to the group and attach policy (attach any)

<img src="images/18.png">

Add user to admin group 

<img src="images/19.png">

Now if we look at the user, we have 3 policy and look at te attached section

<img src="images/20.png">

=======================


- AWS Identity and Access Management (IAM) is a web service provided by Amazon Web Services (AWS) that helps you securely control access to AWS services and resources. 
- IAM enables you to manage permissions and access for users, groups, and roles in your AWS environment. 
- This allows you to enforce the principle of least privilege, ensuring that users and applications have only the permissions they need to perform their tasks.

#### Key Features of AWS IAM
##### 1) Users:

- Individual accounts for people or applications that need access to AWS services.
- Each user can have their own set of security credentials, such as access keys and passwords.
##### 2) Groups:

- Collections of IAM users.
- You can apply policies to groups, and all users in that group inherit those permissions.
##### 3) Roles:

- Roles are created to grant permissions to entities you trust.
- Can be assumed by users, applications, or services to perform specific tasks.
- Useful for delegating access, cross-account access, and service-to-service access.
##### 4) Policies:

- JSON documents that define permissions.
- Attach to users, groups, or roles to specify what actions they can perform on which resources.
- Managed Policies: AWS provides managed policies for common permissions.
- Inline Policies: Custom policies embedded directly in a user, group, or role.
##### 5) Identity Providers and Federation:

- Support for integrating with external identity providers using SAML 2.0, OpenID Connect (OIDC), and Web Identity Federation.
- Allows users to access AWS resources using their corporate credentials or social identity accounts.
##### 6) Multi-Factor Authentication (MFA):

- Additional layer of security that requires users to provide a second form of authentication (e.g., a code from a hardware or virtual MFA device).
#### Key Concepts and Components
##### 1. Users
- An IAM user is an entity that you create in AWS to represent the person or service that interacts with AWS. Each user has its own set of security credentials.

- Example of creating a user via AWS CLI:

sh
```
aws iam create-user --user-name Alice
```
##### 2. Groups
- An IAM group is a collection of IAM users. Groups let you specify permissions for multiple users, which can make it easier to manage permissions.

######  Example of creating a group and adding a user to it:

sh
```
aws iam create-group --group-name Developers
aws iam add-user-to-group --group-name Developers --user-name Alice
```
##### 3. Roles
- An IAM role is an IAM identity that you can create in your account that has specific permissions. A role is intended to be assumable by anyone who needs it.

##### Example of creating a role with a trust policy:

json
```
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "ec2.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
```
sh
```
aws iam create-role --role-name EC2Role --assume-role-policy-document file://trust-policy.json
```
####  4. Policies
- IAM policies define permissions for an action regardless of the method that you use to perform the operation (such as the AWS Management Console, AWS CLI, or AWS API).

- Example of a policy that allows read-only access to S3:

json
```
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::example_bucket",
        "arn:aws:s3:::example_bucket/*"
      ]
    }
  ]
}
```
You can attach this policy to a user, group, or role.

##### 5. Multi-Factor Authentication (MFA)
- MFA adds an extra layer of protection on top of your user name and password. With MFA enabled, when a user signs in to an AWS website, they will be prompted for their user name and password (the first factor—what they know), as well as for an authentication code from their AWS MFA device (the second factor—what they have).

##### Enabling MFA for a user:

sh
```
aws iam enable-mfa-device --user-name Alice --serial-number arn-of-the-mfa-device --authentication-code-1 123456 --authentication-code-2 654321
```
#### Best Practices
- **Follow the Principle of Least Privilege**: Grant only the permissions necessary for users to perform their tasks.
- **Use Roles for Applications**: Use IAM roles for EC2 instances, Lambda functions, and other AWS services instead of embedding long-term credentials in your application.
- **Enable MFA**: Require multi-factor authentication for critical users and highly privileged accounts.
- **Regularly Rotate Credentials**: Rotate access keys and passwords regularly to reduce the risk of compromised credentials.
- **Monitor and Audit IAM Activity**: Use AWS CloudTrail and other AWS services to monitor and audit IAM activities and changes.
#### Conclusion
AWS IAM is a powerful tool that helps you manage access to AWS resources securely. By using IAM's features such as users, groups, roles, policies, and MFA, you can enforce fine-grained access control and follow best security practices in your AWS environment. IAM's integration with other AWS services and its support for identity federation make it a versatile solution for managing identities and permissions in the cloud.