# Terraform Layout

This package separates each major component into its own Terraform file:

- providers.tf
- vault.tf
- cert-manager.tf
- ingress-nginx.tf
- service-account.tf
- issuer-token.tf
- vault-issuer.tf
- certificate.tf
- outputs.tf

Note: Vault PKI / auth bootstrap commands must still be run manually or automated separately.
