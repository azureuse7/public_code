### What is a Trust Policy?
- A trust policy is a JSON document attached to an IAM role that specifies which principals (users, services, accounts) are allowed to assume that role. Think of it as the "gatekeeper" that controls access to the role itself, before any permissions attached to the role come into play.
  
#### Two-Step Permission Model
##### When using IAM roles, there are two layers of permissions:

- Trust Policy - Who can assume the role
- Permissions Policy - What can the role do once assumed?

Both must allow an action for it to succeed.
Trust Policy Structure
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

#### Key Components


- Principal: Specifies who can assume the role
- Action: Typically "sts:AssumeRole" (or variants like "sts:AssumeRoleWithWebIdentity")
