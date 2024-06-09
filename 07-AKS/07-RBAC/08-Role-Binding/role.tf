resource "kubernetes_namespace" "test1" {
  metadata {
    name = "nginx1"
  }
}

resource "kubernetes_role" "example" {
  metadata {
    name = "terraform-example"
    # namespace =  "dev"
    labels = {
      test = "MyRole"
    }
  }

  rule {
    api_groups     = [""]
    resources      = ["pods"]
    resource_names = ["foo"]
    verbs          = ["get", "list", "watch"]
  }
  rule {
    api_groups = ["apps"]
    resources  = ["deployments"]
    verbs      = ["get", "list"]
  }
}
# This role binding allows Group  to read pods in the "default" namespace.

resource "kubernetes_role_binding" "example" {
  metadata {
    name = "terraform-example"
    # namespace = "dev"
  }
  role_ref {
    api_group = "rbac.authorization.k8s.io"
    kind      = "Role"              #this must be Role or ClusterRole
    name      = "terraform-example" # this must match the name of the Role or ClusterRole you wish to bind to
  }
  subject {
    kind = "Group" # or User
    # namespace = "dev"
    name      = "1072bbee-5c84-4553-a071-b2c063c62cc7" #Groudp ID 
    api_group = "rbac.authorization.k8s.io"
  }
  # subject {
  #   kind      = "ServiceAccount"
  #   name      = "default"
  #   namespace = "kube-system"
  # }
  # subject {
  #   kind      = "Group"
  #   name      = "system:masters"
  #   api_group = "rbac.authorization.k8s.io"
  # }
}