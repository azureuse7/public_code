# "namespace" omitted since ClusterRoles are not namespaced

resource "kubernetes_cluster_role" "example" {
  metadata {
    name = "aks-cluster-readonly-role"
  }

  rule {
    api_groups = [""]
    resources  = ["namespaces", "pods"]
    verbs      = ["get", "list", "watch"]
  }
}

resource "kubernetes_cluster_role_binding" "example" {
  metadata {
    name = "aks-cluster-readonly-rolebinding"
  }
  role_ref {
    api_group = "rbac.authorization.k8s.io"
    kind      = "ClusterRole"
    name      = "aks-cluster-readonly-role"
  }
  # subject {
  #   kind      = "User"
  #   name      = "admin"
  #   api_group = "rbac.authorization.k8s.io"
  # }
#   subject {
#     kind      = "ServiceAccount"
#     name      = "default"
#     namespace = "kube-system"
#   }
  subject {
    kind      = "Group"
    name      = "e8f709f7-4029-4fdb-b786-d0af29445fc9"
    api_group = "rbac.authorization.k8s.io"
    # name: groupObjectId # Your Azure AD Group Object ID: aksreadonly
  }
}