resource "kubernetes_secret" "issuer_token" {
  metadata {
    name      = "issuer-token"
    namespace = "default"

    annotations = {
      "kubernetes.io/service-account.name" = "issuer"
    }
  }

  type = "kubernetes.io/service-account-token"
}
