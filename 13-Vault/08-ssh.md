#### Time-bound SSH keys

- Generating time-bound SSH keys using HashiCorp Vault with Terraform involves a few steps. 
- You'll use Vault's SSH secret backend to create dynamic SSH keys that are valid only for a specified duration. 

#### Steps to Configure Time-Bound SSH Keys

##### 1. Configure the Vault Provider in Terraform
```tf
provider "vault" {
  address = "https://your-vault-server:8200"
  token   = "your-vault-token"
}
```
##### 2. Enable and Configure the SSH Secret Backend
```tf
resource "vault_secret_backend" "ssh" {
  path        = "ssh"
  description = "SSH Secret Backend"
}
```
##### 3 Create SSH Roles with Time-Bound Keys
Define roles in Vault that specify the properties of the SSH keys, including time-bound aspects like TTL (Time-To-Live).

```tf
resource "vault_ssh_secret_backend_role" "example_role" {
  name             = "example-role"
  backend          = "ssh"  # Path where the SSH backend is mounted
  key_type         = "otp"  # One-time password (OTP) based SSH key
  default_user     = "ubuntu"  # Default username for SSH access
  cidr_list        = "0.0.0.0/0"  # IP range allowed to connect via SSH
  port             = 22  # Port for SSH
  default_ttl      = "5m"  # Time-to-Live for issued keys (e.g., 5 minutes)
  max_ttl          = "10m"  # Maximum TTL for issued keys (e.g., 10 minutes)
}
```

##### 4. Generate SSH Keys Using the Role
To generate an SSH key pair using the role created, you would typically use Vault's CLI or API, but you can also create a Terraform null_resource to execute these commands if needed. For example:
```tf
data "vault_ssh_secret_backend_credentials" "example" {
  backend = "ssh"  # Path where the SSH backend is mounted
  role    = vault_ssh_secret_backend_role.example_role.name
}

output "ssh_private_key" {
  value = data.vault_ssh_secret_backend_credentials.example.private_key
}

output "ssh_public_key" {
  value = data.vault_ssh_secret_backend_credentials.example.public_key
}
```

##### In this example:

- **data "vault_ssh_secret_backend_credentials"** retrieves a new SSH key pair based on the role's configuration.
- **output** blocks display the generated private and public keys.

##### Summary
Setup: Configure the Vault provider and enable the SSH backend.
Roles: Define SSH roles with time-bound key properties.
Generation: Use the roles to generate time-bound SSH keys.
By following these steps, you can manage dynamic, time-bound SSH keys using Vault and Terraform, enhancing your security posture with automated key management.


#####  Generate SSH Key and Obtain Certificate from Vault
```tf
resource "tls_private_key" "example" {
  algorithm = "RSA"
  rsa_bits  = 2048
}

resource "vault_ssh_secret_cert" "ssh_cert" {
  backend        = "ssh"
  role           = "azure-vm-role"
  public_key     = tls_private_key.example.public_key_openssh
  time_to_live   = "1h"
}

resource "vault_generic_secret" "ssh_cert" {
  path = "ssh/sign/azure-vm-role"

  data_json = jsonencode({
    public_key = tls_private_key.example.public_key_openssh
  })
}
```