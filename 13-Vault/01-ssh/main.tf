provider "vault" {
  address = "http://85.210.168.91:8200/"
  token   = "hvs.WrvC1Oixs8l8tEhQO34gfoTD"
}

# vault_mount is used to manage secret engine mounts in Vault. 
# In this the vault_mount resource is used to enable the SSH secrets engine.
resource "vault_mount" "ssh" {
  path = "ssh"  #Just a name 
  type = "ssh"
  description = "SSH secrets engine"
}

# The vault_ssh_secret_backend_ca resource in Terraform is used to manage the Certificate Authority (CA) 
# for the SSH secrets engine in HashiCorp Vault. 
# This resource allows you to configure the SSH secrets engine to act as a CA, 
# which can sign SSH certificates that are used to authenticate SSH users or hosts.
resource "vault_ssh_secret_backend_ca" "foo" {
    backend = vault_mount.ssh.path
    generate_signing_key = true
}

output "ssh_ca_backend" {
  value = vault_ssh_secret_backend_ca.foo.backend
}

# used to manage roles within the SSH secrets engine in HashiCorp Vault. 
# These roles define the rules and policies for how SSH credentials 
# (such as SSH certificates or one-time passwords) are issued by Vault.
resource "vault_ssh_secret_backend_role" "otp_role" {
  backend      = vault_ssh_secret_backend.ssh.path
  name         = "aks-role"
  key_type     = "ca"
  default_user = "azureuser"  # Default SSH user on AKS nodes
  ttl          = "1h"         # Time-bound: Certificate valid for 1 hour
  allow_user_certificates = true
  allowed_users           = "azureuser"
  allow_host_certificates = false
  allow_user_key_ids      = "*"
}



# The tls_private_key resource in Terraform is used to generate a private key that can be used for 
# cryptographic operations, such as securing SSH connections, signing certificates, or encrypting data. 
# This resource can generate various types of private keys, including RSA, ECDSA, and Ed25519.
resource "tls_private_key" "example" {
  algorithm = "RSA"
  rsa_bits  = 2048
}

# vault_mount is used to manage secret engine mounts in Vault. 
# In this the vault_mount resource is used to enable "Key-Value version 2," 
# which is the second version of the Key-Value secrets engine in Vault.
resource "vault_mount" "kv" {
  path = "secret"
  type = "kv-v2"
}

resource "vault_generic_secret" "ssh_cert" {
  path = "secret/foo"

  data_json = jsonencode({
    username = "myuser"
    password = "mypassword"
  })
}

# The data "vault_kv_secret_v2" block in Terraform is used to retrieve a secret from a 
# Key-Value (KV) version 2 secrets engine in HashiCorp Vault. 
# Data sources in Terraform allow you to fetch or reference data from external systems or from the current infrastructure.

data "vault_kv_secret_v2" "example" {
  mount = "secret"
  name = "myapp/config"  # Path to the secret
}

output "my_secret_value" {
  value     = data.vault_kv_secret_v2.example.data["username"]
  sensitive = true
}








