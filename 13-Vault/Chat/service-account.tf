resource "kubernetes_service_account" "issuer" {
  metadata {
    name      = "issuer"
    namespace = "default"
  }
}
