# Creating Time-Bound SSH Keys Using HashiCorp Vault

Creating time-bound SSH keys using HashiCorp Vault and Certificate Authority (CA) certificates to access Azure Kubernetes Service (AKS) nodes involves several steps.

## 1. Configure Vault

```hcl
provider "vault" {
  address = "http://4.158.34.185:8200"
  token   = ""
}
```

### a. Enable the SSH Secrets Engine

```bash
vault secrets enable -path=ssh ssh
```

```hcl
# Enable the SSH secrets engine
resource "vault_mount" "ssh" {
  path        = "ssh"  # Just a name
  type        = "ssh"
  description = "SSH secrets engine"
}
```

### b. Configure the SSH Role

You need to define a role that specifies the parameters for the SSH certificates. This includes the TTL (time-to-live), which controls how long the SSH key is valid.

```hcl
# Configure the SSH role
resource "vault_ssh_secret_backend_role" "otp_role" {
  backend                 = vault_mount.ssh.path
  name                    = "aks-role"
  key_type                = "ca"
  default_user            = "azureuser"  # Default SSH user on AKS nodes
  ttl                     = "1h"         # Time-bound: Certificate valid for 1 hour
  allow_user_certificates = true
  allowed_users           = "azureuser"
  allow_host_certificates = true
  # allow_user_key_ids    = "*"
}
```

### c. Configure Vault for Client Key Signing (CA)

```bash
vault write ssh/config/ca generate_signing_key=true
```

```hcl
resource "vault_ssh_secret_backend_ca" "ssh_ca" {
  backend              = "ssh-client-signer"
  generate_signing_key = true
}
```

Vault will create a private key for signing SSH certificates.

#### Retrieve the Public Key for SSH Configuration

To distribute the CA public key (to be trusted by your Azure VMs):

```bash
vault read -field=public_key ssh/config/ca
```

```hcl
data "vault_generic_secret" "ssh_ca_public_key" {
  path = "ssh-client-signer/config/ca"
}

output "my_secret_value" {
  value     = data.vault_generic_secret.ssh_ca_public_key.data["public_key"]
  sensitive = true
}
```

#### Create a Terraform File for Provisioning an Azure VM

When configuring an Azure VM to trust the Vault CA, add the public key to the VM's SSH configuration:

```hcl
admin_ssh_key {
  username   = "adminuser"
  public_key = file("path/to/your/ca-public-key.pub")
}
```

## 2. Request Time-Bound SSH Certificates from Vault

When you need to SSH into the VM, you will request a temporary SSH certificate from Vault.

### Generate an SSH Key Pair

```hcl
resource "tls_private_key" "ssh" {
  algorithm = "RSA"
  rsa_bits  = 2048
}
```

### vault_mount for Key-Value Storage

`vault_mount` is used to manage secret engine mounts in Vault. In this case, the `vault_mount` resource enables "Key-Value version 2", which is the second version of the Key-Value secrets engine in Vault.

```hcl
resource "vault_mount" "kv" {
  path = "secret"
  type = "kv-v2"
}
```

### Store the SSH Key as a Secret

```hcl
resource "vault_generic_secret" "ssh_key" {
  path = "secret/aks-ssh-key"
  data_json = jsonencode({
    private_key = tls_private_key.ssh.private_key_pem
    public_key  = tls_private_key.ssh.public_key_pem
  })
}
```

### d. Configure the Vault SSH Client Helper (Optional)

If you are using Vault's SSH client helper, configure it to automatically request and sign SSH certificates.

```bash
export VAULT_ADDR='https://your-vault-address:8200'
vault write -field=signed_key ssh/sign/aks \
    public_key=@$HOME/.ssh/id_rsa.pub
```

## What This Terraform Code Does

- **`tls_private_key`**: Generates an SSH key pair.
- **`vault_ssh_secret_backend_role`**: Configures Vault with the role that will issue time-bound SSH certificates.
- **`vault_generic_secret`**: Stores the SSH key in Vault for later use.

## 3. Use the SSH Key to Access AKS Nodes

Configure access to AKS nodes using the generated SSH certificate.

```hcl
resource "azurerm_kubernetes_cluster_node_pool" "example" {
  # Your AKS node pool configuration

  ssh_config {
    public_key = tls_private_key.ssh.public_key_openssh
  }
}
```

When you apply this configuration, Terraform will:

- Generate a new SSH key.
- Store the private key securely in Vault.
- Configure your AKS node pool to accept connections using the public key.

## 4. Requesting SSH Certificates

When you need to access an AKS node, request an SSH certificate from Vault:

```bash
vault write -field=signed_key ssh/sign/aks \
    public_key=@$HOME/.ssh/id_rsa.pub \
    valid_principals="ubuntu"
```

This command returns a signed SSH certificate that is valid for the duration specified in the TTL.

## 5. Accessing the AKS Node

Use the signed SSH certificate to access your AKS nodes:

```bash
ssh -i ~/.ssh/id_rsa-cert.pub ubuntu@<AKS-node-IP>
```

## 6. Automating the Workflow

You can automate the entire workflow by integrating the SSH certificate request process into your deployment pipelines or other automation tools.

## Conclusion

This setup provides a secure and time-bound mechanism for accessing AKS nodes using SSH, leveraging Vault's dynamic secret management capabilities. It ensures that access is temporary and controlled, minimizing the risk of unauthorized access. Terraform plays a crucial role in automating the infrastructure setup and ensuring consistency across environments.
