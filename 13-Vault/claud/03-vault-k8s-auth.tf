# ---------------------------------------------------------------------------
# 03-vault-k8s-auth.tf
#
# Enables and configures the Vault Kubernetes Authentication method.
#
# What this file creates:
#   1. vault_auth_backend              — Enables the kubernetes auth method
#   2. vault_kubernetes_auth_backend_config — Connects Vault to the K8s API
#   3. vault_kubernetes_auth_backend_role   — Binds a SA to a Vault policy
#
# How Kubernetes auth works end-to-end:
#   1. cert-manager reads the JWT token from the "issuer-token" Secret
#   2. cert-manager sends the JWT to Vault at: POST /v1/auth/kubernetes/login
#   3. Vault calls the Kubernetes TokenReview API to verify the JWT is valid
#      and checks the Service Account name / namespace match the auth role
#   4. If valid, Vault returns a short-lived Vault token with the
#      "pki-cert-manager" policy attached
#   5. cert-manager uses that token to call pki/sign/example-dot-com
#
# This replaces static Vault tokens — no long-lived secrets are stored
# in Kubernetes for Vault authentication.
#
# Prerequisites:
#   - 01-vault-install.tf must be applied and Vault must be unsealed
#   - 02-vault-pki.tf must be applied (policy must exist before binding it)
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# 1. Enable the Kubernetes Auth Method
# ---------------------------------------------------------------------------

resource "vault_auth_backend" "kubernetes" {
  type        = "kubernetes"
  path        = "kubernetes"
  description = "Kubernetes auth — allows pods to authenticate via Service Account JWT tokens"

  depends_on = [vault_policy.pki_cert_manager]
}

# ---------------------------------------------------------------------------
# 2. Read the Vault Service Account token from the cluster
# ---------------------------------------------------------------------------
# Vault uses its own Service Account token to call the Kubernetes
# TokenReview API when verifying incoming JWT tokens from other pods.
#
# The Vault Helm chart creates a ServiceAccount named "vault" in the
# vault namespace. We reference its token secret here.
#
# Note: If the secret doesn't exist yet (e.g. Vault just started),
# you may need to run terraform apply twice, or use a null_resource
# with a local-exec to wait for it.

data "kubernetes_secret" "vault_sa_token" {
  metadata {
    # The Vault Helm chart creates this ServiceAccount automatically.
    # The secret name follows the convention <sa-name>-token or is
    # auto-generated on Kubernetes 1.24+ (check with: kubectl get secrets -n vault)
    name      = "vault-token"
    namespace = var.vault_namespace
  }

  depends_on = [helm_release.vault]
}

# ---------------------------------------------------------------------------
# 3. Configure the Kubernetes Auth Backend
# ---------------------------------------------------------------------------
# This tells Vault:
#   - The Kubernetes API server URL (so it can call TokenReview)
#   - The cluster CA cert (so it can verify the API server's TLS cert)
#   - The Vault SA JWT token (so it can authenticate to the API server)

resource "vault_kubernetes_auth_backend_config" "k8s_config" {
  backend = vault_auth_backend.kubernetes.path

  # The Kubernetes API server URL.
  # "kubernetes.default.svc.cluster.local" is the standard in-cluster address.
  kubernetes_host = "https://kubernetes.default.svc.cluster.local:443"

  # The cluster CA certificate — used by Vault to verify the K8s API server TLS cert.
  # This is the same CA cert available to every pod at:
  # /var/run/secrets/kubernetes.io/serviceaccount/ca.crt
  kubernetes_ca_cert = base64decode(
    data.kubernetes_secret.vault_sa_token.data["ca.crt"]
  )

  # Vault's own JWT token — presented when calling the TokenReview API.
  # Vault periodically re-reads this value to support short-lived token rotation.
  token_reviewer_jwt = data.kubernetes_secret.vault_sa_token.data["token"]

  # The JWT issuer — must match the cluster's --service-account-issuer flag.
  # The default value below is correct for most clusters.
  issuer = "https://kubernetes.default.svc.cluster.local"

  depends_on = [vault_auth_backend.kubernetes]
}

# ---------------------------------------------------------------------------
# 4. Create the Kubernetes Auth Role for cert-manager
# ---------------------------------------------------------------------------
# This role defines:
#   - Which Kubernetes Service Accounts may authenticate (bound_service_account_names)
#   - Which namespaces those SAs must be in (bound_service_account_namespaces)
#   - Which Vault policy the resulting token will carry (token_policies)
#   - How long the resulting Vault token is valid (token_ttl)
#
# When cert-manager presents a JWT from the "issuer" ServiceAccount in the
# "cert-manager" or "default" namespace, Vault:
#   1. Verifies the JWT via TokenReview
#   2. Confirms the SA name matches "issuer"
#   3. Confirms the namespace is in the allowed list
#   4. Returns a Vault token with the "pki-cert-manager" policy

resource "vault_kubernetes_auth_backend_role" "issuer" {
  backend   = vault_auth_backend.kubernetes.path
  role_name = "issuer"

  # The name of the Kubernetes Service Account cert-manager will use.
  # This SA is created in 04-certmanager.tf.
  bound_service_account_names = ["issuer"]

  # Namespaces where the above SA is allowed to exist.
  # Add any namespace where you create cert-manager Issuer resources.
  bound_service_account_namespaces = [
    var.cert_manager_namespace,
    "default",
  ]

  # The Vault policy granted upon successful authentication.
  # "pki-cert-manager" is defined in 02-vault-pki.tf.
  token_policies = [vault_policy.pki_cert_manager.name]

  # Vault token TTL — cert-manager will re-authenticate before this expires.
  # 20 minutes is sufficient; cert-manager renews its token proactively.
  token_ttl = 1200   # seconds

  # Maximum total TTL including renewals
  token_max_ttl = 3600   # 1 hour

  depends_on = [vault_kubernetes_auth_backend_config.k8s_config]
}
