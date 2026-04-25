# https://github.com/falcosecurity/charts/tree/master/charts/falco
resource "helm_release" "falco" {
  name             = "falco"
  repository       = "https://falcosecurity.github.io/charts"
  chart            = "falco"
  version          = var.falco_chart_version
  namespace        = var.falco_namespace
  create_namespace = true

  # Load the external values file
  values = [
    file("${path.module}/falco-values.yaml")
  ]
}
