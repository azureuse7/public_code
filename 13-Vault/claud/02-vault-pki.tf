# ---------------------------------------------------------------------------
# 02-vault-pki.tf
#
# Configures the Vault PKI secrets engine as an internal Certificate Authority.
#
# What this file creates (in dependency order):
#   1. vault_mount         — Enables the PKI secrets engine at path "pki"
#   2. vault_pki_secret_backend_root_cert — Generates the self-signed root CA
#   3. vault_pki_secret_backend_config_urls — Sets the CA and CRL URLs
#   4. vault_pki_secret_backend_role       — Defines certificate issuance rules
#   5. vault_policy                        — Grants cert-manager minimum permissions
#
# Prerequisites:
#   - Vault must be initialised and unsealed (see 01-vault-install.tf notes)
#   - VAULT_ADDR and TF_VAR_vault_root_token must be set in your shell
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# 1. Enable the PKI Secrets Engine
# ---------------------------------------------------------------------------
# The PKI secrets engine is Vault's built-in Certificate Authority.
# Mounting it at "pki" is conventional for a single root CA.
# You can mount multiple PKI engines (e.g. pki_int for an intermediate CA).
#
# max_lease_ttl_seconds sets the ceiling for any certificate issued
# from this mount. The role's max_ttl (below) cannot exceed this value.

resource "vault_mount" "pki" {
  path        = "pki"
  type        = "pki"
  description = "PKI secrets engine — Internal Certificate Authority"

  # 10 years: sets the upper bound for the root CA certificate TTL
  default_lease_ttl_seconds = 3600          # 1 hour default for issued certs
  max_lease_ttl_seconds     = 315360000     # 10 years — root CA lifetime ceiling
}

# ---------------------------------------------------------------------------
# 2. Generate the Root CA Certificate
# ---------------------------------------------------------------------------
# Vault generates the root CA key pair internally. The private key NEVER
# leaves Vault — this is the core security property of using Vault as a CA.
#
# type = "internal" means: generate and store the key inside Vault.
# Use type = "existing" if you want to import an externally generated key.

resource "vault_pki_secret_backend_root_cert" "root_ca" {
  backend = vault_mount.pki.path
  type    = "internal"

  common_name  = var.vault_pki_root_cn
  organization = var.vault_pki_organisation
  country      = var.vault_pki_country
  ttl          = "87600h"   # 10 years for the root CA itself

  key_type = "rsa"
  key_bits = 4096           # 4096-bit for root CA (stronger than leaf cert keys)

  depends_on = [vault_mount.pki]
}

# ---------------------------------------------------------------------------
# 3. Configure the PKI URLs
# ---------------------------------------------------------------------------
# Every issued certificate embeds two URLs:
#   issuing_certificates:    Where to download the CA certificate chain
#   crl_distribution_points: Where to check for revoked certificates
#
# These must be reachable by anything that validates TLS certificates issued
# by this CA. Within the cluster, the Vault ClusterIP service DNS is used.
# For external services validating these certs, expose Vault externally or
# use a reverse proxy and update these URLs accordingly.

resource "vault_pki_secret_backend_config_urls" "pki_urls" {
  backend = vault_mount.pki.path

  issuing_certificates = [
    "http://vault.${var.vault_namespace}.svc.cluster.local:8200/v1/pki/ca"
  ]

  crl_distribution_points = [
    "http://vault.${var.vault_namespace}.svc.cluster.local:8200/v1/pki/crl"
  ]

  depends_on = [vault_pki_secret_backend_root_cert.root_ca]
}

# ---------------------------------------------------------------------------
# 4. Create a PKI Role
# ---------------------------------------------------------------------------
# A PKI role defines the *constraints* applied to every certificate issued
# through it. cert-manager will request certificates against this role.
#
# Key constraint decisions:
#   allowed_domains:  Only certificates for "example.com" subdomains are allowed.
#                     Change this to match your actual internal domain.
#   allow_subdomains: Permits *.example.com — needed for demo.example.com.
#   max_ttl:          Upper bound for leaf certificate duration. cert-manager
#                     can request shorter durations via the Certificate resource.
#   enforce_hostnames: Ensures the CN/SANs are valid hostnames.

resource "vault_pki_secret_backend_role" "example_dot_com" {
  backend = vault_mount.pki.path
  name    = "example-dot-com"

  allowed_domains         = ["example.com"]
  allow_subdomains        = true
  allow_bare_domains      = false
  allow_wildcard_certificates = false   # Disable wildcards unless explicitly needed

  key_type = "rsa"
  key_bits = 2048   # 2048-bit is standard for leaf/end-entity certificates

  # max_ttl must not exceed vault_mount.pki.max_lease_ttl_seconds
  max_ttl = var.pki_max_ttl   # Default: 8760h (1 year)

  enforce_hostnames = true
  require_cn        = true

  # Allow cert-manager to set key usage extensions
  key_usage = [
    "DigitalSignature",
    "KeyAgreement",
    "KeyEncipherment",
  ]

  ext_key_usage = [
    "ServerAuth",
    "ClientAuth",
  ]

  depends_on = [vault_pki_secret_backend_config_urls.pki_urls]
}

# ---------------------------------------------------------------------------
# 5. Create a Vault Policy for cert-manager
# ---------------------------------------------------------------------------
# Vault policies follow a least-privilege model. This policy grants
# cert-manager only the permissions it needs to issue certificates:
#   - Read/list the PKI mount (discovery)
#   - Create/update the role (trigger issuance)
#   - Sign a CSR (Certificate Signing Request)
#   - Issue a certificate directly
#
# This policy is bound to the Kubernetes auth role in 03-vault-k8s-auth.tf.
# cert-manager receives this policy as a Vault token upon successful
# Service Account JWT authentication.

resource "vault_policy" "pki_cert_manager" {
  name = "pki-cert-manager"

  policy = <<-EOT
    # Allow cert-manager to read and list the PKI mount metadata
    path "pki*" {
      capabilities = ["read", "list"]
    }

    # Allow cert-manager to reference the PKI role when requesting a cert
    path "pki/roles/example-dot-com" {
      capabilities = ["create", "update"]
    }

    # Allow cert-manager to submit a CSR and receive a signed certificate
    # This is the primary path used by the cert-manager Vault Issuer
    path "pki/sign/example-dot-com" {
      capabilities = ["create", "update"]
    }

    # Allow cert-manager to request a certificate directly (without a CSR)
    path "pki/issue/example-dot-com" {
      capabilities = ["create", "update"]
    }
  EOT

  depends_on = [vault_pki_secret_backend_role.example_dot_com]
}
