# ---------------------------------------------------------------------------
# Kubernetes / Cluster
# ---------------------------------------------------------------------------

variable "kubeconfig_path" {
  description = "Path to the kubeconfig file used to connect to the cluster"
  type        = string
  default     = "~/.kube/config"
}

variable "kubeconfig_context" {
  description = "The kubeconfig context to use. Leave empty to use the current-context."
  type        = string
  default     = ""
}

# ---------------------------------------------------------------------------
# Vault
# ---------------------------------------------------------------------------

variable "vault_address" {
  description = "The HTTP(S) address of the Vault server — used by the Vault Terraform provider"
  type        = string
  default     = "http://localhost:8200"
  # After Vault is running inside the cluster you can also use:
  # "http://vault.vault.svc.cluster.local:8200"
  # but this requires Terraform to be running inside the cluster or
  # a port-forward to be active.
}

variable "vault_root_token" {
  description = <<-EOT
    Vault root or admin token.
    NEVER hardcode this value. Supply it via the environment variable:
      export TF_VAR_vault_root_token=<token>
    or use a secrets manager integration in your CI/CD pipeline.
  EOT
  type      = string
  sensitive = true
}

variable "vault_namespace" {
  description = "Kubernetes namespace where Vault will be installed"
  type        = string
  default     = "vault"
}

variable "vault_chart_version" {
  description = "Helm chart version for the HashiCorp Vault chart"
  type        = string
  default     = "0.27.0"
}

variable "vault_ha_enabled" {
  description = "Enable Vault HA mode with Raft integrated storage. Set true for production."
  type        = bool
  default     = false
}

variable "vault_ha_replicas" {
  description = "Number of Vault replicas when HA is enabled"
  type        = number
  default     = 3
}

variable "vault_storage_class" {
  description = "StorageClass for Vault persistent volume claims (used in non-dev mode)"
  type        = string
  default     = "default"
}

variable "vault_pki_root_cn" {
  description = "Common Name for the Vault root CA certificate"
  type        = string
  default     = "Internal Root CA"
}

variable "vault_pki_organisation" {
  description = "Organisation name embedded in the root CA certificate"
  type        = string
  default     = "My Organisation"
}

variable "vault_pki_country" {
  description = "Two-letter country code for the root CA certificate"
  type        = string
  default     = "GB"
}

# ---------------------------------------------------------------------------
# cert-manager
# ---------------------------------------------------------------------------

variable "cert_manager_namespace" {
  description = "Kubernetes namespace where cert-manager will be installed"
  type        = string
  default     = "cert-manager"
}

variable "cert_manager_chart_version" {
  description = "Helm chart version for the cert-manager chart"
  type        = string
  default     = "v1.14.5"
}

# ---------------------------------------------------------------------------
# Ingress
# ---------------------------------------------------------------------------

variable "ingress_namespace" {
  description = "Kubernetes namespace for the NGINX Ingress Controller"
  type        = string
  default     = "ingress-nginx"
}

variable "ingress_service_type" {
  description = "Kubernetes Service type for the NGINX ingress controller. Use LoadBalancer for cloud clusters, NodePort for local/kind."
  type        = string
  default     = "LoadBalancer"

  validation {
    condition     = contains(["LoadBalancer", "NodePort", "ClusterIP"], var.ingress_service_type)
    error_message = "ingress_service_type must be one of: LoadBalancer, NodePort, ClusterIP."
  }
}

# ---------------------------------------------------------------------------
# Application / Certificate
# ---------------------------------------------------------------------------

variable "app_domain" {
  description = "The FQDN for the demo application (e.g. demo.example.com). Must match the PKI role allowed_domains."
  type        = string
  default     = "demo.example.com"
}

variable "cert_duration" {
  description = "Total validity duration for issued certificates (e.g. 8760h = 1 year)"
  type        = string
  default     = "8760h"
}

variable "cert_renew_before" {
  description = "How far before expiry cert-manager should start renewing (e.g. 720h = 30 days)"
  type        = string
  default     = "720h"
}

variable "pki_max_ttl" {
  description = "Maximum TTL for certificates issued by the PKI role. Must not exceed the vault_mount max_lease_ttl."
  type        = string
  default     = "8760h"
}
