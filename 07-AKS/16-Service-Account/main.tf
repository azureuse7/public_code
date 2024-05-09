# k get serviceaccount -A
# k delete  serviceaccount terraform-example -n default/
# k get serviceaccount -n serviceaccountg 

provider "kubernetes" {
  config_path = "~/.kube/config"
}

resource "kubernetes_namespace" "serviceaccountg" {
  metadata {
    name = "serviceaccountg"
  }
}


# resource "kubernetes_service_account" "example" {
#   metadata {
#     name      = "terraform-example"
#     namespace = "serviceaccountg"
#   }
#   secret {
#     name = kubernetes_secret.example.metadata.0.name
#   }
# }


resource "kubernetes_secret" "example" {
  metadata {
    name      = "terraform-example1"
    namespace = "serviceaccountg"
    # annotations = {
    #   "kubernetes.io/service-account.name" = kubernetes_service_account.example.metadata[0].name
    # }
  }

#   type = "kubernetes.io/service-account-token"
}

# resource "kubernetes_secret" "example" {
#   metadata {
#     name = "terraform-example"
#   }
# }