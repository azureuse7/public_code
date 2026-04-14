# ---------------------------------------------------------------------------
# 04-certmanager.tf
#
# Installs cert-manager and creates the Service Account + token Secret
# that cert-manager uses to authenticate with Vault.
#
# What this file creates:
#   1. kubernetes_namespace     — Dedicated namespace for cert-manager
#   2. helm_release             — cert-manager Helm chart (controller + webhook + cainjector)
#   3. kubernetes_service_account — "issuer" SA used for Vault auth
#   4. kubernetes_secret          — Long-lived SA token referenced by the Issuer
#
# How cert-manager interacts with Vault:
#   cert-manager controller
#     └── watches Certificate resources
#     └── authenticates with Vault using the "issuer" SA JWT token
#     └── submits a CSR to Vault PKI (pki/sign/example-dot-com)
#     └── stores the returned certificate in a Kubernetes Secret
#     └── monitors expiry and renews automatically
#
# Prerequisites:
#   - 03-vault-k8s-auth.tf must be applied (the Vault auth role must exist
#     before cert-manager tries to authenticate)
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# 1. cert-manager Namespace
# ---------------------------------------------------------------------------

resource "kubernetes_namespace" "cert_manager" {
  metadata {
    name = var.cert_manager_namespace

    labels = {
      "app.kubernetes.io/managed-by" = "terraform"
      "app.kubernetes.io/component"  = "cert-manager"
    }
  }
}

# ---------------------------------------------------------------------------
# 2. Install cert-manager via Helm
# ---------------------------------------------------------------------------
# cert-manager installs three Deployments:
#
#   cert-manager (controller)
#     - Watches Certificate, CertificateRequest, and Order CRDs
#     - Orchestrates the full certificate issuance lifecycle
#     - Handles renewal by monitoring NotAfter timestamps
#
#   cert-manager-webhook
#     - ValidatingWebhookConfiguration: rejects invalid cert-manager resources
#     - MutatingWebhookConfiguration: sets defaults on cert-manager resources
#     - Runs as a separate process so the APIServer can reach it
#
#   cert-manager-cainjector
#     - Injects the CA bundle into ValidatingWebhookConfiguration,
#       MutatingWebhookConfiguration, and APIService resources
#     - Required for the webhook to work correctly
#
# installCRDs=true: installs Certificate, Issuer, ClusterIssuer, etc. CRDs.
# This is preferred over a separate CRD installation step.

resource "helm_release" "cert_manager" {
  name       = "cert-manager"
  repository = "https://charts.jetstack.io"
  chart      = "cert-manager"
  version    = var.cert_manager_chart_version
  namespace  = kubernetes_namespace.cert_manager.metadata[0].name

  # Install cert-manager CRDs as part of the Helm release.
  # This means CRDs are upgraded/removed with the chart automatically.
  set {
    name  = "installCRDs"
    value = "true"
  }

  # Enable Prometheus metrics scraping
  set {
    name  = "prometheus.enabled"
    value = "true"
  }

  # Wait for all three components (controller, webhook, cainjector) to be Ready.
  # cert-manager's webhook must be Ready before Issuer/Certificate resources
  # can be applied, or the API server will reject them.
  wait    = true
  timeout = 300

  depends_on = [
    kubernetes_namespace.cert_manager,
    vault_kubernetes_auth_backend_role.issuer,
  ]
}

# ---------------------------------------------------------------------------
# 3. "issuer" Service Account
# ---------------------------------------------------------------------------
# This Service Account is the identity cert-manager presents to Vault.
# It must:
#   - Be named "issuer" (matching vault_kubernetes_auth_backend_role.issuer)
#   - Exist in a namespace that is in the Vault role's allowed namespaces list
#
# We create it in the "default" namespace here. If you want cert-manager
# to issue certificates for resources in multiple namespaces, consider
# using a ClusterIssuer instead and creating the SA in cert-manager namespace.

resource "kubernetes_service_account" "issuer" {
  metadata {
    name      = "issuer"
    namespace = "default"

    labels = {
      "app.kubernetes.io/managed-by" = "terraform"
      "app.kubernetes.io/component"  = "vault-cert-issuer"
    }
  }

  # Prevent Kubernetes from auto-mounting the default SA token.
  # We create an explicit token secret below.
  automount_service_account_token = false

  depends_on = [helm_release.cert_manager]
}

# ---------------------------------------------------------------------------
# 4. Long-lived Service Account Token Secret
# ---------------------------------------------------------------------------
# Kubernetes 1.24+ no longer auto-creates long-lived tokens for Service Accounts.
# cert-manager's Vault Issuer requires a static secretRef pointing to a token.
# We create one explicitly with the special annotation that tells Kubernetes
# to populate it with a signed JWT for the "issuer" ServiceAccount.
#
# The token in this secret is what cert-manager sends to Vault's
# POST /v1/auth/kubernetes/login endpoint.
#
# Note: This token does NOT expire (it's a long-lived SA token).
# For higher security, use the cert-manager serviceAccountRef feature
# (cert-manager >= 1.11) which uses projected short-lived tokens instead.

resource "kubernetes_secret" "issuer_token" {
  metadata {
    name      = "issuer-token"
    namespace = "default"

    annotations = {
      # This annotation tells Kubernetes to populate the secret with a
      # signed JWT for the named Service Account
      "kubernetes.io/service-account.name" = kubernetes_service_account.issuer.metadata[0].name
    }

    labels = {
      "app.kubernetes.io/managed-by" = "terraform"
      "app.kubernetes.io/component"  = "vault-cert-issuer"
    }
  }

  # This type causes Kubernetes to inject: token, ca.crt, namespace
  type = "kubernetes.io/service-account-token"

  depends_on = [kubernetes_service_account.issuer]
}
