# ---------------------------------------------------------------------------
# 05-issuer.tf
#
# Creates the cert-manager Issuer resource that connects cert-manager to Vault.
#
# What this file creates:
#   1. kubectl_manifest (Issuer) — tells cert-manager how to reach Vault,
#      which PKI path to use for signing, and how to authenticate
#
# Issuer vs ClusterIssuer:
#   - Issuer:        Namespace-scoped. Only Certificate resources in the
#                    same namespace can reference it.
#   - ClusterIssuer: Cluster-scoped. Any namespace can reference it.
#                    Use this if you need certificates in multiple namespaces.
#
# This file creates a namespace-scoped Issuer in "default".
# To use a ClusterIssuer instead, change kind to "ClusterIssuer" and
# update the Certificate's issuerRef.kind accordingly.
#
# Prerequisites:
#   - 04-certmanager.tf must be applied (cert-manager CRDs must exist,
#     "issuer-token" secret must exist)
#   - 02-vault-pki.tf must be applied (the pki/sign path must exist in Vault)
#   - 03-vault-k8s-auth.tf must be applied (the Vault auth role must exist)
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# cert-manager Issuer — Vault backend
# ---------------------------------------------------------------------------
# The Issuer resource is a cert-manager CRD. We use the kubectl provider
# to apply it as raw YAML because the kubernetes provider does not support
# custom CRDs natively.
#
# How this Issuer works:
#   1. cert-manager reads the "issuer-token" secret to get the SA JWT
#   2. It POSTs the JWT to Vault: POST <vault_server>/v1/auth/kubernetes/login
#      with role=issuer
#   3. Vault verifies the JWT via TokenReview and returns a Vault token
#   4. cert-manager uses the Vault token to call: POST <vault_server>/v1/pki/sign/example-dot-com
#   5. Vault signs the CSR and returns the certificate + chain
#   6. cert-manager stores the result in the Certificate's secretName

resource "kubectl_manifest" "vault_issuer" {
  yaml_body = yamlencode({
    apiVersion = "cert-manager.io/v1"
    kind       = "Issuer"

    metadata = {
      name      = "vault-issuer"
      namespace = "default"

      labels = {
        "app.kubernetes.io/managed-by" = "terraform"
        "app.kubernetes.io/component"  = "vault-issuer"
      }
    }

    spec = {
      vault = {
        # The Vault server URL — must be reachable from the cert-manager pod.
        # Using the ClusterIP DNS ensures this works without external access.
        server = "http://vault.${var.vault_namespace}.svc.cluster.local:8200"

        # The Vault PKI path where cert-manager will submit CSRs.
        # Format: <mount>/sign/<role>
        # This must match the path in the Vault PKI policy (02-vault-pki.tf).
        path = "pki/sign/example-dot-com"

        # If Vault is using TLS (recommended for production), specify the CA
        # bundle cert-manager should use to verify Vault's TLS certificate.
        # Uncomment and populate for TLS-enabled Vault:
        # caBundle = base64encode(file("vault-ca.crt"))

        auth = {
          kubernetes = {
            # The Vault path where the Kubernetes auth method is mounted.
            # Must match vault_auth_backend.kubernetes.path (03-vault-k8s-auth.tf).
            mountPath = "/v1/auth/kubernetes"

            # The Vault auth role cert-manager authenticates as.
            # Must match vault_kubernetes_auth_backend_role.issuer.role_name.
            role = "issuer"

            # The Kubernetes Secret containing the Service Account JWT token.
            # cert-manager reads the "token" key from this secret and presents
            # it to Vault for authentication.
            secretRef = {
              name = kubernetes_secret.issuer_token.metadata[0].name
              key  = "token"
            }
          }
        }
      }
    }
  })

  depends_on = [
    helm_release.cert_manager,
    kubernetes_secret.issuer_token,
    vault_kubernetes_auth_backend_role.issuer,
    vault_pki_secret_backend_role.example_dot_com,
  ]
}

# ---------------------------------------------------------------------------
# Verify the Issuer after apply
# ---------------------------------------------------------------------------
# Run the following to confirm cert-manager successfully connected to Vault:
#
#   kubectl describe issuer vault-issuer -n default
#
# You should see in the Status section:
#   Conditions:
#     Type:    Ready
#     Status:  True
#     Reason:  VaultVerified
#     Message: Vault verified
#
# If the status shows False, check:
#   1. Vault is unsealed:        kubectl exec -n vault vault-0 -- vault status
#   2. Vault URL is reachable:   kubectl run debug --image=curlimages/curl -it --rm -- \
#                                  curl http://vault.vault.svc.cluster.local:8200/v1/sys/health
#   3. SA token exists:          kubectl describe secret issuer-token -n default
#   4. Auth role is configured:  vault read auth/kubernetes/role/issuer
# ---------------------------------------------------------------------------
