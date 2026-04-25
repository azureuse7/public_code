resource "kubernetes_manifest" "certificate" {
  manifest = {
    apiVersion = "cert-manager.io/v1"
    kind       = "Certificate"

    metadata = {
      name      = "demo-example-com"
      namespace = "default"
    }

    spec = {
      secretName = "example-com-tls"

      issuerRef = {
        name = "vault-issuer"
      }

      commonName = "demo.example.com"

      dnsNames = [
        "demo.example.com"
      ]
    }
  }
}
