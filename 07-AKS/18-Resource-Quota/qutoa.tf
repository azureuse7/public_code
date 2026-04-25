provider "kubernetes" {
  config_path = "~/.kube/config"
}

resource "kubernetes_namespace" "lquota" {
  metadata {
    name = "quota"
  }
}

# A resource quota provides constraints that limit  resource consumption 
# per namespace.

resource "kubernetes_resource_quota" "example" {
  metadata {
    name = "terraform-example"
  }
  spec {
    hard = {
      pods = 10
    }
    scopes = ["BestEffort"]
  }
}

resource "kubernetes_deployment" "test7" {
  metadata {
    name      = "frontend-nginxapp"
    namespace = "limit"
  }
  spec {
    replicas = 2
    selector {
      match_labels = {
        app = "MyTestApp"
      }
    }
    template {
      metadata {
        labels = {
          app = "MyTestApp"
        }
      }
      spec {
        container {
          image = "nginx"
          name  = "nginx-container"
          port {
            container_port = 80
          }
        }
      }
    }
  }
}
resource "kubernetes_service" "tes6t" {
  metadata {
    name      = "nginx"
    namespace = "limit"
  }
  spec {
    type = "LoadBalancer"
    selector = {
      app = kubernetes_deployment.test.spec.0.template.0.metadata.0.labels.app
    }
    port {
      # node_port   = 320201
      port        = 80
      target_port = 80
    }
  }
}