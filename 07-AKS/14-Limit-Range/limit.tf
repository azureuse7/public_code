provider "kubernetes" {
  config_path = "~/.kube/config"
}

# Limit Range sets resource usage limits (e.g. memory, cpu, storage) in a namespace.

resource "kubernetes_namespace" "limit" {
  metadata {
    name = "limit"
  }
}

resource "kubernetes_limit_range" "example" {
  metadata {
    name = "terraform-example"
    namespace = "limit"
  }
  spec {
    limit {
      type = "Pod"
      max = {
        cpu    = "200m"
        memory = "1024Mi"
      }
    }
    limit {
      type = "PersistentVolumeClaim"
      min = {
        storage = "24M"
      }
    }
    limit {
      type = "Container"
      default = {
        cpu    = "50m"
        memory = "24Mi"
      }
    }
  }
}

resource "kubernetes_deployment" "limit" {
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
resource "kubernetes_service" "tffest" {
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
      # node_port   = 30201
      port        = 80
      target_port = 80
    }
  }
}