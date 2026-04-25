resource "kubernetes_manifest" "vault_issuer" {
  manifest = {
    apiVersion = "cert-manager.io/v1"
    kind       = "Issuer"

    metadata = {
      name      = "vault-issuer"
      namespace = "default"
    }

    spec = {
      vault = {
        server = "http://vault.vault:8200"
        path   = "pki/sign/example-dot-com"

        auth = {
          kubernetes = {
            mountPath = "/v1/auth/kubernetes"
            role      = "issuer"

            secretRef = {
              name = "issuer-token"
              key  = "token"
            }
          }
        }
      }
    }
  }
}
