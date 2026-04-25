provider "kubernetes" {
  config_path = "~/.kube/config"
}
# A pod is a group of one or more containers, the shared storage for those containers, 
# and options about how to run the containers.
resource "kubernetes_namespace" "pod" {
  metadata {
    name = "pod"
  }
}
resource "kubernetes_pod" "pod" {
  metadata {
    name      = "pod"
    namespace = kubernetes_namespace.pod.metadata.0.name
  }
  spec {
    container {
      image = "nginx"
      name  = "pod"
      port {
        container_port = 80   #Number of port to expose on the pod's IP address.
      }
    }
  }
}
#create service
resource "kubernetes_service" "pod" {
  metadata {
    name      = "pod"
    namespace = kubernetes_namespace.pod.metadata.0.name
  }
  spec {
    type = "LoadBalancer" # ClusterIp, # NodePort
    selector = {
        app = "pod" #This should match the pod 
    }
    port {
      port        = 80
      target_port = 80
    }
  }
}