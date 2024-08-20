#### PKI Secret Engine Overview
- The PKI (Public Key Infrastructure) secret engine in Vault allows you to create and manage Certificate Authorities (CAs) and issue certificates. 
- It provides a simple way to generate dynamic X.509 certificates, which are often used for TLS (Transport Layer Security) and other cryptographic protocols.

##### When you mount a PKI engine in Vault, you can:

- Generate a root CA or intermediate CA.
- Issue new certificates signed by the CA.
- Revoke certificates.
- Manage certificate roles and policies.
##### Usage Example in Terraform
- Here's an expanded example that shows how you might use the vault_mount resource to configure a PKI backend and then configure the PKI settings:

```tf
# Mount the PKI engine at the path "pki"
resource "vault_mount" "pki" {
  path = "pki"
  type = "pki"
}

# Set the maximum Time To Live (TTL) for certificates issued by this engine
resource "vault_pki_secret_backend_config_urls" "pki" {
  backend = vault_mount.pki.path

  issuing_certificates = ["http://vault.example.com/v1/pki/ca"]
  crl_distribution_points = ["http://vault.example.com/v1/pki/crl"]
}

# Generate a root certificate for the PKI engine
resource "vault_pki_secret_backend_root_cert" "root_cert" {
  backend = vault_mount.pki.path

  common_name = "example.com"
  ttl         = "87600h" # 10 years
}

# Create a role to issue certificates
resource "vault_pki_secret_backend_role" "example_dot_com" {
  backend      = vault_mount.pki.path
  name         = "example-dot-com"
  allowed_domains = ["example.com"]
  allow_subdomains = true
  max_ttl         = "72h"
}
```
#### Steps in the Example
##### Mount the PKI Engine:

- The **vault_mount** resource mounts the PKI secret engine at the /pki path.
##### Configure URLs for the PKI Backend:

- **vault_pki_secret_backend_config_urls** configures the issuing certificates and CRL (Certificate Revocation List) distribution points URLs.
##### Generate a Root Certificate:

- **vault_pki_secret_backend_root_cert** generates a root certificate for the PKI backend. This root certificate will be used to sign other certificates.
##### Create a Role:

- vault_pki_secret_backend_role creates a role within the PKI backend that can issue certificates for the example.com domain and its subdomains, with a maximum TTL of 72 hours.