resource "helm_release" "vault" {
  name       = "vault"
  namespace  = "vault"
  repository = "https://helm.releases.hashicorp.com"
  chart      = "vault"

  create_namespace = true

  values = [
    yamlencode({
      server = {
        standalone = {
          enabled = true
        }
      }
    })
  ]
}
