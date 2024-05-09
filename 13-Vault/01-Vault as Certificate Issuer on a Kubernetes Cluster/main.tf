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
    address         = "http://51.11.23.159:8200/" # IP of the UI of vault 
    # skip_tls_verify = false
    token           = "hvs.pzfohdXulMHRR3al0pzJ0y3X" #root token 
}

#helm install vault hashicorp/vault --set='ui.enabled=true' --set='ui.serviceType=LoadBalancer'
#k exec -it vault-0 /bin/sh     #Login to the vault pod
#vault status                    # Notice its sealed  
#vault operator init             #Init the pod Copy the keys and token
#vault operator unseal           # Use the keys to unseal 
# copy the keys and Repeat three times and Notice it would say sealed false 
# Copy The Ip and test


#Configuring the Vault PKI engine as a Certificate Authority
#  vault intermediate pki mount point /pki
resource "vault_mount"  "pki" {
  path                  = "pki"
  type                  = "pki"
  description           = "Self signed Vault root CA"
  max_lease_ttl_seconds = 20 * 365 * 24 * 3600
}


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

# vault root pki urls
resource "vault_pki_secret_backend_config_urls" "pkirootca" {
  backend                 = vault_mount.pkirootca.path
  issuing_certificates    = ["http://vault-active.vault.svc:8200/v1/${vault_mount.pkirootca.path}/ca"]
  crl_distribution_points = ["http://vault-active.vault.svc:8200/v1/${vault_mount.pkirootca.path}/crl"]
}


# pki roles
resource "vault_pki_secret_backend_role" "pki-application" {
  backend            = vault_mount.pki.path
  name               = "application"
  ttl                = 35.5 * 24 * 3600
  max_ttl            = 36 * 24 * 3600
  generate_lease     = false
  allow_bare_domains = true
  allow_glob_domains = true
  allow_ip_sans      = true
  allow_localhost    = true
  allow_subdomains   = false
  allowed_domains = [
    "*.default.svc",
    "*.default.svc.cluster.local",
  ]
  key_bits  = 2048
  key_type  = "rsa"
  key_usage = ["DigitalSignature", "KeyAgreement", "KeyEncipherment"]
}


resource "vault_policy" "certs" {
  name   = "certs"
  policy = file("policies/cert.hcl")
}


resource "vault_auth_backend" "kubernetes" {
  type                  = "kubernetes"
  path                  = "kubernetes"
  description           = "Kubernetes authentication backend mount"
}


resource "vault_kubernetes_auth_backend_config" "kubernetes" {
  backend            = vault_auth_backend.kubernetes.path
  kubernetes_host    = "https://kubernetes.default.svc"
# kubernetes_ca_cert = base64decode("<your k8s certificate>")
  kubernetes_ca_cert = "sanaloveyou"
}

resource "vault_kubernetes_auth_backend_role" "kubernetes-certs" {
  role_name                        = "certs"
  backend                          = vault_auth_backend.kubernetes.path
  bound_service_account_names      = ["cert-manager"]
  bound_service_account_namespaces = ["cert-manager"]
  token_policies = [
    "certs",
  ]
}

