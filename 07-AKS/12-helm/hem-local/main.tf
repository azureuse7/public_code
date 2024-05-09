resource "helm_release" "global_network_policies" {
  name = "gautam"
  chart       = "${path.module}/charts/global-network-policies"
  values      = [templatefile("${path.module}/files/global-network-policies/values.yaml", {})]
  namespace   = "gautam"
  max_history = 5
  postrender {
  binary_path = "${path.module}/kustomize/kustomize.sh"
  }
}


provider "azurerm" {
  features {}
}

provider "helm" {
  kubernetes {
    config_path = pathexpand(var.kube_config)
  }
}

provider "kubernetes" {
  config_path = pathexpand(var.kube_config)
}

variable "kube_config" {
  type    = string
  default = "~/.kube/config"
}