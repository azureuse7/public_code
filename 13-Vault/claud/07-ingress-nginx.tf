# ---------------------------------------------------------------------------
# 07-ingress-nginx.tf
#
# Installs the NGINX Ingress Controller into the cluster.
#
# What this file creates:
#   1. kubernetes_namespace — Dedicated namespace for ingress-nginx
#   2. helm_release         — NGINX Ingress Controller Helm chart
#
# Role of the NGINX Ingress Controller:
#   - Listens on the LoadBalancer external IP (or NodePort) for HTTP/HTTPS traffic
#   - Reads Ingress resources to know which hostname maps to which backend Service
#   - Reads the TLS Secret (created by cert-manager) to terminate HTTPS
#   - Proxies decrypted traffic to the backend pods
#   - Automatically reloads configuration when Ingress or Secret resources change
#
# TLS termination flow:
#   Client ──HTTPS──► NGINX (terminates TLS using example-com-tls secret)
#                      └── HTTP ──► web Service ──► web Pod
#
# Prerequisites:
#   - 06-certificate.tf must be applied so the TLS secret exists before
#     the Ingress resource references it (see 08-demo-app.tf)
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Namespace
# ---------------------------------------------------------------------------

resource "kubernetes_namespace" "ingress_nginx" {
  metadata {
    name = var.ingress_namespace

    labels = {
      "app.kubernetes.io/managed-by" = "terraform"
      "app.kubernetes.io/component"  = "ingress-nginx"
    }
  }
}

# ---------------------------------------------------------------------------
# Helm Release — NGINX Ingress Controller
# ---------------------------------------------------------------------------
# The ingress-nginx Helm chart installs:
#   - A Deployment for the NGINX controller
#   - A LoadBalancer Service to receive external traffic
#   - An IngressClass resource named "nginx"
#   - RBAC resources allowing the controller to watch Ingress/Secret resources
#
# Key configuration choices:
#   - service.type: LoadBalancer for cloud (AKS, EKS), NodePort for local clusters
#   - replicaCount: set >1 for production availability
#   - ssl-redirect: enforce HTTPS for all HTTP requests
#   - use-forwarded-headers: trust X-Forwarded-For from upstream load balancers

resource "helm_release" "ingress_nginx" {
  name       = "ingress-nginx"
  repository = "https://kubernetes.github.io/ingress-nginx"
  chart      = "ingress-nginx"
  namespace  = kubernetes_namespace.ingress_nginx.metadata[0].name

  # Block until the ingress controller pod is Running and the
  # LoadBalancer Service has been assigned an external IP/hostname
  wait    = true
  timeout = 300

  # ----- Service type -----
  # LoadBalancer: cloud clusters provision an external IP automatically
  # NodePort: use for local clusters (kind, minikube) — no cloud LB needed
  set {
    name  = "controller.service.type"
    value = var.ingress_service_type
  }

  # ----- Replicas -----
  set {
    name  = "controller.replicaCount"
    value = "2"   # Minimum 2 for production availability
  }

  # ----- SSL redirect -----
  # Redirect all HTTP requests to HTTPS automatically
  set {
    name  = "controller.config.ssl-redirect"
    value = "true"
  }

  set {
    name  = "controller.config.force-ssl-redirect"
    value = "true"
  }

  # ----- Proxy headers -----
  # Trust X-Forwarded-For and X-Real-IP from upstream load balancers
  set {
    name  = "controller.config.use-forwarded-headers"
    value = "true"
  }

  # ----- Metrics -----
  # Enable Prometheus metrics endpoint on the controller
  set {
    name  = "controller.metrics.enabled"
    value = "true"
  }

  depends_on = [kubernetes_namespace.ingress_nginx]
}

# ---------------------------------------------------------------------------
# How to find the external IP after apply
# ---------------------------------------------------------------------------
# Cloud clusters (AKS / EKS):
#   kubectl get svc -n ingress-nginx ingress-nginx-controller
#   # The EXTERNAL-IP column shows the assigned IP or hostname
#
# Local clusters (NodePort):
#   kubectl get svc -n ingress-nginx ingress-nginx-controller
#   # Use <NodeIP>:<NodePort> to access ingress resources
#
# Add a local hosts entry for testing:
#   echo "<EXTERNAL-IP> demo.example.com" | sudo tee -a /etc/hosts
# ---------------------------------------------------------------------------
