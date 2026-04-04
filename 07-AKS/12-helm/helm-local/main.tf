resource "helm_release" "global_network_policies" {
  name      = "global-network-policies"
  chart     = "${path.module}/charts/global-network-policies"
  namespace = var.namespace

  max_history = 5

  postrender {
    binary_path = "${path.module}/kustomize/kustomize.sh"
  }
}
