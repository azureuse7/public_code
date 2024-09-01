#Installing HashiCorp Vault for terraform provider

terraform {
  required_providers {
    vault = {
      source = "hashicorp/vault"
      version = "3.1.1"
            }
        }
    }

provider "vault" {
    address         = "http://85.210.169.36:8200/" # IP of the UI of vault 
    # skip_tls_verify = false
    token           = "hvs.XUeFe6XdDUsPD8pw9yc2PyUP" #root token 
}

#helm install vault hashicorp/vault --set='ui.enabled=true' --set='ui.serviceType=LoadBalancer'
#k exec -it vault-0 /bin/sh     #Login to the vault pod
#vault status                    # Notice its sealed  
#vault operator init             #Init the pod Copy the keys and token
#vault operator unseal           # Use the keys to unseal 
# copy the keys and Repeat three times and Notice it would say sealed false 
# Copy The Ip and test

# The vault_mount resource in Terraform is used to configure and manage the "mounts" or "engines" within HashiCorp Vault. 
# A mount in Vault is essentially a backend where different types of secrets can be stored and managed. 
# Each mount point is associated with a particular type of secret engine, such as PKI (Public Key Infrastructure), 
# KV (Key/Value), Transit, etc.


#Configuring the Vault PKI engine as a Certificate Authority
#  vault intermediate pki mount point /pki
resource "vault_mount"  "pki" {
  path                  = "pki"
  type                  = "pki"
  description           = "Self signed Vault root CA"
  max_lease_ttl_seconds = 20 * 365 * 24 * 3600
}


# The vault_pki_secret_backend_intermediate_cert_request resource in Terraform is used to create a 
# Certificate Signing Request (CSR) for an intermediate certificate authority (CA) in HashiCorp Vault's PKI 
# (Public Key Infrastructure) secret engine. An intermediate CA is a certificate authority that is not 
# the root CA but is instead signed by the root CA or another intermediate CA. 
# This setup is common in a hierarchical CA infrastructure, providing additional security and 
# delegation capabilities

# certificate request
resource "vault_pki_secret_backend_intermediate_cert_request" "pki" {
  backend            = vault_mount.pki.path
  type               = "exported"
  common_name        = "vault-active.vault.svc"
  alt_names          = ["vault.vault.svc", "vault-standby.vault.svc"]
  format             = "pem"
  private_key_format = "der"
  key_type           = "rsa"
  key_bits           = 2048
}


# The vault_pki_secret_backend_config_urls resource is part of the Terraform provider for HashiCorp Vault, 
# and it is used to configure the URLs for a Public Key Infrastructure (PKI) secrets backend in Vault. 
# This resource allows you to specify the various URLs that clients will use to interact with the PKI backend, 
# such as the issuing certificate, CRL (Certificate Revocation List), and others.

# # vault root pki urls
# resource "vault_pki_secret_backend_config_urls" "pkirootca" {
#   backend                 = vault_mount.pkirootca.path
#   issuing_certificates    = ["http://vault-active.vault.svc:8200/v1/${vault_mount.pkirootca.path}/ca"]
#   crl_distribution_points = ["http://vault-active.vault.svc:8200/v1/${vault_mount.pkirootca.path}/crl"]
# }


# # The vault_pki_secret_backend_role resource in Terraform is used to manage roles within a PKI 
# # (Public Key Infrastructure) secret backend in HashiCorp Vault. A PKI backend in Vault is used 
# # to generate and manage X.509 certificates, and roles within the PKI backend define the parameters 
# # and policies for issuing certificates.

# # pki roles
# resource "vault_pki_secret_backend_role" "pki-application" {
#   backend            = vault_mount.pki.path
#   name               = "application"
#   ttl                = 35.5 * 24 * 3600
#   max_ttl            = 36 * 24 * 3600
#   generate_lease     = false
#   allow_bare_domains = true
#   allow_glob_domains = true
#   allow_ip_sans      = true
#   allow_localhost    = true
#   allow_subdomains   = false
#   allowed_domains = [
#     "*.default.svc",
#     "*.default.svc.cluster.local",
#   ]
#   key_bits  = 2048
#   key_type  = "rsa"
#   key_usage = ["DigitalSignature", "KeyAgreement", "KeyEncipherment"]
# }


# resource "vault_policy" "certs" {
#   name   = "certs"
#   policy = file("policies/cert.hcl")
# }

# # The vault_auth_backend resource is used in HashiCorp Vault's Terraform provider to manage 
# # authentication backends in a Vault server. An authentication backend is a way for users 
# # or machines to authenticate themselves to the Vault server to gain access to secrets or
# #  perform operations.

# resource "vault_auth_backend" "kubernetes" {
#   type                  = "kubernetes"
#   path                  = "kubernetes"
#   description           = "Kubernetes authentication backend mount"
# }


# # The vault_kubernetes_auth_backend_config resource in Terraform is used to configure the Kubernetes 
# # authentication backend in HashiCorp Vault. This configuration allows Vault to authenticate Kubernetes 
# # service accounts and generate tokens or secrets for workloads running in a Kubernetes cluster.

# resource "vault_kubernetes_auth_backend_config" "kubernetes" {
#   backend            = vault_auth_backend.kubernetes.path
#   kubernetes_host    = "https://kubernetes.default.svc"
# # kubernetes_ca_cert = base64decode("<your k8s certificate>")
#   kubernetes_ca_cert = "sanaloveyou"
# }


# # The vault_kubernetes_auth_backend_role resource in Terraform is used to define roles within 
# # the Kubernetes authentication backend in HashiCorp Vault. These roles map Kubernetes service 
# # accounts to Vault policies, allowing Kubernetes workloads (like pods) to authenticate with Vault 
# # and gain access to secrets based on the permissions defined by those policies.

# resource "vault_kubernetes_auth_backend_role" "kubernetes-certs" {
#   role_name                        = "certs"
#   backend                          = vault_auth_backend.kubernetes.path
#   bound_service_account_names      = ["cert-manager"]
#   bound_service_account_namespaces = ["cert-manager"]
#   token_policies = [
#     "certs",
#   ]
# }

