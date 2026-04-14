# ---------------------------------------------------------------------------
# outputs.tf
#
# Exposes useful values after terraform apply.
# Reference these in CI/CD pipelines or pass them to dependent modules.
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Vault
# ---------------------------------------------------------------------------

output "vault_namespace" {
  description = "Kubernetes namespace where Vault is installed"
  value       = kubernetes_namespace.vault.metadata[0].name
}

output "vault_internal_url" {
  description = "Vault ClusterIP URL — reachable from within the cluster"
  value       = "http://vault.${kubernetes_namespace.vault.metadata[0].name}.svc.cluster.local:8200"
}

output "vault_chart_version" {
  description = "Helm chart version deployed for Vault"
  value       = helm_release.vault.version
}

output "vault_pki_mount_path" {
  description = "Vault PKI secrets engine mount path"
  value       = vault_mount.pki.path
}

output "vault_pki_role_name" {
  description = "Vault PKI role name used for certificate issuance"
  value       = vault_pki_secret_backend_role.example_dot_com.name
}

output "vault_pki_sign_path" {
  description = "Full Vault API path for signing certificates (used by the cert-manager Issuer)"
  value       = "pki/sign/${vault_pki_secret_backend_role.example_dot_com.name}"
}

output "vault_policy_name" {
  description = "Vault policy name granted to cert-manager upon authentication"
  value       = vault_policy.pki_cert_manager.name
}

output "vault_k8s_auth_role" {
  description = "Vault Kubernetes auth role name that cert-manager authenticates as"
  value       = vault_kubernetes_auth_backend_role.issuer.role_name
}

# ---------------------------------------------------------------------------
# cert-manager
# ---------------------------------------------------------------------------

output "cert_manager_namespace" {
  description = "Kubernetes namespace where cert-manager is installed"
  value       = kubernetes_namespace.cert_manager.metadata[0].name
}

output "cert_manager_chart_version" {
  description = "Helm chart version deployed for cert-manager"
  value       = helm_release.cert_manager.version
}

output "issuer_service_account" {
  description = "Name of the Kubernetes Service Account used by cert-manager to authenticate with Vault"
  value       = kubernetes_service_account.issuer.metadata[0].name
}

output "issuer_token_secret" {
  description = "Name of the Kubernetes Secret containing the issuer SA JWT token"
  value       = kubernetes_secret.issuer_token.metadata[0].name
}

# ---------------------------------------------------------------------------
# Certificates
# ---------------------------------------------------------------------------

output "tls_secret_name" {
  description = "Name of the Kubernetes Secret where cert-manager stores the issued TLS certificate"
  value       = "example-com-tls"
}

output "certificate_domain" {
  description = "The domain the TLS certificate is issued for"
  value       = var.app_domain
}

output "certificate_duration" {
  description = "Certificate validity duration"
  value       = var.cert_duration
}

output "certificate_renew_before" {
  description = "How far in advance cert-manager begins renewing the certificate"
  value       = var.cert_renew_before
}

# ---------------------------------------------------------------------------
# Ingress
# ---------------------------------------------------------------------------

output "ingress_namespace" {
  description = "Kubernetes namespace where NGINX Ingress Controller is installed"
  value       = kubernetes_namespace.ingress_nginx.metadata[0].name
}

output "ingress_chart_version" {
  description = "Helm chart version deployed for NGINX Ingress Controller"
  value       = helm_release.ingress_nginx.version
}

# ---------------------------------------------------------------------------
# Useful kubectl commands (informational)
# ---------------------------------------------------------------------------

output "helpful_commands" {
  description = "Useful kubectl commands for verifying the deployment"
  value       = <<-EOT
    # Check Vault status
    kubectl exec -n ${kubernetes_namespace.vault.metadata[0].name} vault-0 -- vault status

    # Port-forward Vault locally
    kubectl port-forward -n ${kubernetes_namespace.vault.metadata[0].name} svc/vault 8200:8200

    # Watch certificate issuance
    kubectl get certificate -n default -w

    # Inspect the issued certificate
    kubectl get secret example-com-tls -n default \
      -o jsonpath='{.data.tls\.crt}' | base64 -d | openssl x509 -noout -text

    # Get ingress external IP
    kubectl get svc -n ${kubernetes_namespace.ingress_nginx.metadata[0].name} ingress-nginx-controller

    # Test HTTPS
    curl -kivL https://${var.app_domain}
  EOT
}
