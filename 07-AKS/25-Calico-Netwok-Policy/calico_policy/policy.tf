provider "kubernetes" {
  config_path = "~/.kube/config"
}

# resource "kubernetes_network_policy" "example" {
#   metadata {
#     name      = "backend-policy"
#     namespace = "dev3"
#   }

#   spec {
#     policy_types = ["Ingress"]
#     pod_selector {
#       match_labels = {
#         web = "dev3"
#       }
#     }
#     ingress {
#       from {
#         namespace_selector {
#           match_labels = {
#             web : "dev1"
#           }
#         }
#       }
#     }
#   }
# }
resource "kubernetes_network_policy" "example" {
  metadata {
    name      = "backend-policy"
    namespace = "dev3"
  }
  spec {
    pod_selector {}
    ingress {}
    egress {}
    }
  policy_types = ["Egress"]
  }