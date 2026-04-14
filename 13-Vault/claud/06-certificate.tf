# ---------------------------------------------------------------------------
# 06-certificate.tf
#
# Declares the TLS certificate cert-manager should obtain from Vault.
#
# What this file creates:
#   1. kubectl_manifest (Certificate) — the certificate request declaration
#
# What cert-manager does with this resource:
#   1. Reads the Certificate spec
#   2. Generates a private key (RSA 2048)
#   3. Creates a CertificateRequest with a CSR
#   4. Authenticates with Vault (via the Issuer in 05-issuer.tf)
#   5. Submits the CSR to Vault PKI (pki/sign/example-dot-com)
#   6. Receives the signed certificate and CA chain from Vault
#   7. Stores them in the Kubernetes Secret named by spec.secretName:
#        tls.crt  — the signed certificate (PEM)
#        tls.key  — the private key (PEM)
#        ca.crt   — the CA certificate chain (PEM)
#   8. Watches the certificate NotAfter time and renews automatically
#      when the renewBefore threshold is reached
#
# Prerequisites:
#   - 05-issuer.tf must be applied and the Issuer must be Ready
# ---------------------------------------------------------------------------

resource "kubectl_manifest" "demo_certificate" {
  yaml_body = yamlencode({
    apiVersion = "cert-manager.io/v1"
    kind       = "Certificate"

    metadata = {
      name      = "demo-example-com"
      namespace = "default"

      labels = {
        "app.kubernetes.io/managed-by" = "terraform"
        "app.kubernetes.io/component"  = "tls-certificate"
      }
    }

    spec = {
      # ---------------------------------------------------------------------------
      # secretName — where the issued certificate will be stored
      # ---------------------------------------------------------------------------
      # cert-manager creates (or updates) this Kubernetes Secret with:
      #   tls.crt  — the signed leaf certificate in PEM format
      #   tls.key  — the private key in PEM format
      #   ca.crt   — the CA certificate chain in PEM format
      #
      # The NGINX Ingress controller reads from this secret for TLS termination.
      secretName = "example-com-tls"

      # ---------------------------------------------------------------------------
      # Certificate lifetime and renewal
      # ---------------------------------------------------------------------------
      # duration:    Total validity period. Vault's PKI role max_ttl is the ceiling.
      # renewBefore: cert-manager starts the renewal process this far before expiry.
      #              A rolling renewal (e.g. at 70% of lifetime) is common practice.
      #
      # Example: duration=8760h, renewBefore=720h
      #   → Certificate valid for 1 year
      #   → cert-manager renews it 30 days before expiry
      #   → Zero downtime: new cert is stored in the secret before old one expires
      duration    = var.cert_duration     # Default: 8760h (1 year)
      renewBefore = var.cert_renew_before # Default: 720h (30 days)

      # ---------------------------------------------------------------------------
      # Subject
      # ---------------------------------------------------------------------------
      # commonName: embedded in the certificate Subject CN field.
      # Modern TLS clients use SANs (dnsNames) for hostname verification, not CN.
      # Both are set here for maximum compatibility.
      commonName = var.app_domain

      # dnsNames: Subject Alternative Names (SANs) — what clients actually verify.
      # Add all hostnames this certificate should be valid for.
      dnsNames = [var.app_domain]

      # ---------------------------------------------------------------------------
      # Issuer reference
      # ---------------------------------------------------------------------------
      # Points cert-manager to the Issuer created in 05-issuer.tf.
      # kind = "Issuer" means namespace-scoped.
      # kind = "ClusterIssuer" for a cluster-wide issuer.
      issuerRef = {
        name = "vault-issuer"
        kind = "Issuer"
      }

      # ---------------------------------------------------------------------------
      # Private key settings
      # ---------------------------------------------------------------------------
      # These settings control the private key generated for the *leaf* certificate
      # (not the CA key, which lives inside Vault).
      #
      # rotationPolicy = "Always": generate a fresh private key on every renewal.
      # This is the recommended setting — it limits exposure if a key is compromised.
      # rotationPolicy = "Never": reuse the existing key (not recommended).
      privateKey = {
        algorithm      = "RSA"
        size           = 2048
        rotationPolicy = "Always"
      }

      # ---------------------------------------------------------------------------
      # Additional Secret labels (optional)
      # ---------------------------------------------------------------------------
      # Labels applied to the resulting TLS Secret.
      # Useful for RBAC policies or tooling that needs to find cert secrets.
      secretTemplate = {
        labels = {
          "cert-manager.io/issuer-name" = "vault-issuer"
          "app.kubernetes.io/component" = "tls-secret"
        }
      }
    }
  })

  depends_on = [kubectl_manifest.vault_issuer]
}

# ---------------------------------------------------------------------------
# Verify the Certificate after apply
# ---------------------------------------------------------------------------
# Watch the certificate status until it shows READY=True:
#   kubectl get certificate demo-example-com -n default -w
#
# Inspect the issued certificate details:
#   kubectl get secret example-com-tls -n default \
#     -o jsonpath='{.data.tls\.crt}' | base64 -d | openssl x509 -noout -text
#
# Check CertificateRequest events for Vault interaction details:
#   kubectl describe certificaterequest -n default
#
# Watch cert-manager controller logs in real time:
#   kubectl logs -n cert-manager -l app=cert-manager -f --tail=50
# ---------------------------------------------------------------------------
