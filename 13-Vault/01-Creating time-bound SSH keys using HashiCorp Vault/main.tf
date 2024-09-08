# - Creating time-bound SSH keys using HashiCorp Vault and using Certificate Authority (CA) certificates to 
# access Azure Kubernetes Service (AKS) nodes involves several steps.

provider "vault" {
  address = "http://4.158.91.114:8200"
  token   = "hvs.2PMF1fNc0f48CFS2NXOIFX9q"
}
provider "azurerm" {
  features {}
}

provider "tls" {
}

# Enable the SSH secrets engine
# vault_mount is used to manage secret engine mounts in Vault. 
# vault secrets enable -path=ssh ssh

resource "vault_mount" "ssh" {
  path        = "ssh-client-signer"
  type        = "ssh"
  description = "SSH Client Signing Engine"
}


# Configure the SSH role for time limit
# These roles define the rules and policies for how SSH credentials
# (such as SSH certificates or one-time passwords) are issued by Vault. 

resource "vault_ssh_secret_backend_role" "otp_role" {
  backend      = "ssh-client-signer"
  name         = "aks-role"
  key_type     = "ca"
  default_user = "azureuser"  # Default SSH user on AKS nodes
  ttl          = "1h"         # Time-bound: Certificate valid for 1 hour
  allow_user_certificates = true
  allowed_users           = "azureuser"
  allow_host_certificates = true
  # allow_user_key_ids      = "*"
}

# Configure Vault for Client Key Signing (CA)
# vault write ssh/config/ca generate_signing_key=true

resource "vault_ssh_secret_backend_ca" "ssh_ca" {
    backend = "ssh-client-signer"
    generate_signing_key = true
}

# Retrieve the Public Key for SSH Configuration CA public key (to be trusted by your Azure VMs)
data "vault_generic_secret" "ssh_ca_public_key" {
  path = "ssh-client-signer/config/ca"
}

output "my_secret_value" {
  value     = data.vault_generic_secret.ssh_ca_public_key.data["public_key"]
  sensitive = true
}

# This Can be added as below 
output "my_secret_value" {
  value     = data.vault_generic_secret.ssh_ca_public_key.data["public_key"]
  sensitive = true
}

# When you need to SSH into the VM, you will request a temporary SSH certificate from Vault:
# Generate an SSH keypair

resource "tls_private_key" "ssh" {
  algorithm = "RSA"
  rsa_bits  = 2048
}


# # Ask Vault to sign the public key
# resource "vault_generic_endpoint" "signed_ssh_key" {
#   path = "ssh-client-signer/sign/aks-role"

#   data_json = jsonencode({
#     public_key = tls_private_key.ssh_key.public_key_openssh
#   })
# }


# vault_mount is used to manage secret engine mounts in Vault. 
# In this the vault_mount resource is used to enable "Key-Value version 2," 

resource "vault_mount" "kv" {
  path = "secret"
  type = "kv-v2"
}

resource "vault_generic_secret" "ssh_key" {
  path = "secret/aks-ssh-key"
  data_json = jsonencode({
    private_key = tls_private_key.ssh.private_key_pem
    public_key  = tls_private_key.ssh.public_key_pem
  })
}


data "vault_kv_secret_v2" "example" {
  mount = "secret"
  name = "aks-ssh-key"  # Path to the secret
}

output "my_secret_value1" {
  value     = data.vault_kv_secret_v2.example.data["private_key"]
  sensitive = true
}

# 1. Requesting SSH Certificates
# When you need to access an AKS node, you'll request an SSH certificate from Vault.


# vault write -field=signed_key ssh/sign/aks \
#     public_key=@$HOME/.ssh/id_rsa.pub \
#     valid_principals="ubuntu"
# ```
# This command will return a signed SSH certificate that is valid for the duration specified in the TTL.
