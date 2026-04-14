# ---------------------------------------------------------------------------
# 08-demo-app.tf
#
# Deploys a demo web application and wires it to TLS via an Ingress resource.
#
# What this file creates:
#   1. kubernetes_deployment — The demo web application
#   2. kubernetes_service    — ClusterIP Service exposing the app within the cluster
#   3. kubectl_manifest (Ingress) — Wires the domain, TLS secret, and backend Service
#
# Traffic flow after apply:
#
#   Browser ──HTTPS──► LoadBalancer IP
#                        └──► NGINX Ingress Controller
#                               └── Reads TLS from: example-com-tls Secret
#                               └── Routes demo.example.com to: web Service :8080
#                                     └──► web Pod(s)
#
# Prerequisites:
#   - 06-certificate.tf: the "example-com-tls" Secret must exist
#   - 07-ingress-nginx.tf: the NGINX controller must be Running
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# 1. Demo Application Deployment
# ---------------------------------------------------------------------------
# A simple "Hello World" HTTP server for demonstrating TLS end-to-end.
# Replace this with your actual application in a real deployment.

resource "kubernetes_deployment" "web" {
  metadata {
    name      = "web"
    namespace = "default"

    labels = {
      "app"                          = "web"
      "app.kubernetes.io/name"       = "web"
      "app.kubernetes.io/managed-by" = "terraform"
    }
  }

  spec {
    # Run 2 replicas for availability; cert-manager and NGINX handle rolling cert updates
    replicas = 2

    selector {
      match_labels = { app = "web" }
    }

    template {
      metadata {
        labels = { app = "web" }
      }

      spec {
        # Ensure pods are spread across nodes for availability
        topology_spread_constraint {
          max_skew           = 1
          topology_key       = "kubernetes.io/hostname"
          when_unsatisfiable = "DoNotSchedule"
          label_selector {
            match_labels = { app = "web" }
          }
        }

        container {
          name  = "web"
          image = "gcr.io/google-samples/hello-app:1.0"

          port {
            container_port = 8080
            protocol       = "TCP"
          }

          # Resource requests and limits — always set in production
          resources {
            requests = {
              cpu    = "50m"
              memory = "64Mi"
            }
            limits = {
              cpu    = "100m"
              memory = "128Mi"
            }
          }

          # Liveness probe — restart pod if it becomes unresponsive
          liveness_probe {
            http_get {
              path = "/"
              port = 8080
            }
            initial_delay_seconds = 5
            period_seconds        = 10
          }

          # Readiness probe — only send traffic when pod is ready
          readiness_probe {
            http_get {
              path = "/"
              port = 8080
            }
            initial_delay_seconds = 3
            period_seconds        = 5
          }
        }

        # Security context — run as non-root
        security_context {
          run_as_non_root = true
          run_as_user     = 1000
        }
      }
    }
  }

  depends_on = [helm_release.ingress_nginx]
}

# ---------------------------------------------------------------------------
# 2. ClusterIP Service
# ---------------------------------------------------------------------------
# Exposes the web pods within the cluster.
# The Ingress resource references this Service as the backend.
# ClusterIP is sufficient — NGINX handles external access.

resource "kubernetes_service" "web" {
  metadata {
    name      = "web"
    namespace = "default"

    labels = {
      "app"                          = "web"
      "app.kubernetes.io/managed-by" = "terraform"
    }
  }

  spec {
    selector = { app = "web" }

    port {
      name        = "http"
      port        = 8080
      target_port = 8080
      protocol    = "TCP"
    }

    type = "ClusterIP"
  }

  depends_on = [kubernetes_deployment.web]
}

# ---------------------------------------------------------------------------
# 3. Ingress Resource
# ---------------------------------------------------------------------------
# This Ingress resource tells the NGINX controller:
#   - For requests to var.app_domain (e.g. demo.example.com)
#   - Use the TLS certificate in the "example-com-tls" Secret
#   - Proxy traffic to the "web" Service on port 8080
#
# The TLS Secret must already exist when NGINX reads this Ingress.
# cert-manager (06-certificate.tf) ensures it does.
#
# Annotations control NGINX-specific behaviour:
#   ssl-redirect:       Redirect HTTP → HTTPS
#   proxy-body-size:    Maximum request body size
#   proxy-read-timeout: Backend response timeout

resource "kubectl_manifest" "example_ingress" {
  yaml_body = yamlencode({
    apiVersion = "networking.k8s.io/v1"
    kind       = "Ingress"

    metadata = {
      name      = "example-ingress"
      namespace = "default"

      labels = {
        "app.kubernetes.io/managed-by" = "terraform"
        "app.kubernetes.io/component"  = "ingress"
      }

      annotations = {
        # Force HTTPS — redirect any HTTP request to HTTPS
        "nginx.ingress.kubernetes.io/ssl-redirect"       = "true"
        "nginx.ingress.kubernetes.io/force-ssl-redirect" = "true"

        # Max upload size (adjust for your app)
        "nginx.ingress.kubernetes.io/proxy-body-size" = "10m"

        # Timeout settings
        "nginx.ingress.kubernetes.io/proxy-read-timeout"    = "60"
        "nginx.ingress.kubernetes.io/proxy-connect-timeout" = "60"
      }
    }

    spec = {
      # References the IngressClass installed by the NGINX Helm chart
      ingressClassName = "nginx"

      tls = [
        {
          hosts = [var.app_domain]
          # This Secret was created by cert-manager in 06-certificate.tf.
          # NGINX reads tls.crt and tls.key from this Secret to serve HTTPS.
          secretName = "example-com-tls"
        }
      ]

      rules = [
        {
          host = var.app_domain
          http = {
            paths = [
              {
                path     = "/"
                pathType = "Prefix"
                backend = {
                  service = {
                    name = kubernetes_service.web.metadata[0].name
                    port = { number = 8080 }
                  }
                }
              }
            ]
          }
        }
      ]
    }
  })

  depends_on = [
    kubectl_manifest.demo_certificate,
    kubernetes_service.web,
  ]
}

# ---------------------------------------------------------------------------
# Verify end-to-end TLS after apply
# ---------------------------------------------------------------------------
# 1. Get the ingress external IP:
#      kubectl get svc -n ingress-nginx ingress-nginx-controller
#
# 2. Add a hosts entry (replace <IP>):
#      echo "<IP> demo.example.com" | sudo tee -a /etc/hosts
#
# 3. Test HTTPS and inspect the certificate:
#      curl -kivL https://demo.example.com
#
#    Expect to see:
#      subject: CN=demo.example.com
#      issuer:  CN=<vault_pki_root_cn>
#      start date / expire date matching duration in 06-certificate.tf
#
# 4. Verify the certificate in the secret:
#      kubectl get secret example-com-tls -n default \
#        -o jsonpath='{.data.tls\.crt}' | base64 -d | openssl x509 -noout -text
# ---------------------------------------------------------------------------
