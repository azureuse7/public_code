# ---------------------------------------------------------------------------
# 01-vault-install.tf
#
# Installs HashiCorp Vault into the cluster using the official Helm chart.
#
# What this file creates:
#   - A dedicated Kubernetes namespace for Vault
#   - A Helm release for Vault (single-node or HA Raft depending on variables)
#
# After applying this file you MUST manually initialise and unseal Vault
# before the remaining Terraform files can be applied. See README / Step 2.
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Namespace
# ---------------------------------------------------------------------------

resource "kubernetes_namespace" "vault" {
  metadata {
    name = var.vault_namespace

    labels = {
      "app.kubernetes.io/managed-by" = "terraform"
      "app.kubernetes.io/component"  = "vault"
    }
  }
}

# ---------------------------------------------------------------------------
# Helm Release — Vault
# ---------------------------------------------------------------------------
# The HashiCorp Vault Helm chart installs:
#   - A StatefulSet for the Vault server pod(s)
#   - A ClusterIP Service (vault) for internal cluster access
#   - An Agent Injector Deployment (mutating webhook for sidecar injection)
#   - Required RBAC resources
#
# Key design decisions:
#   - Service type is ClusterIP — Vault is only reachable inside the cluster.
#     cert-manager connects via vault.<namespace>.svc.cluster.local:8200
#   - Dev mode is NEVER enabled — it uses an in-memory backend and a
#     well-known root token, which is insecure even for testing.
#   - HA mode and Raft storage are controlled by var.vault_ha_enabled.
# ---------------------------------------------------------------------------

resource "helm_release" "vault" {
  name       = "vault"
  repository = "https://helm.releases.hashicorp.com"
  chart      = "vault"
  version    = var.vault_chart_version
  namespace  = kubernetes_namespace.vault.metadata[0].name

  # Block Terraform until all Vault pods report Ready
  wait    = true
  timeout = 300

  # ----- Server: disable dev mode -----
  set {
    name  = "server.dev.enabled"
    value = "false"
  }

  # ----- HA / Raft storage -----
  set {
    name  = "server.ha.enabled"
    value = tostring(var.vault_ha_enabled)
  }

  dynamic "set" {
    for_each = var.vault_ha_enabled ? [1] : []
    content {
      name  = "server.ha.replicas"
      value = tostring(var.vault_ha_replicas)
    }
  }

  dynamic "set" {
    for_each = var.vault_ha_enabled ? [1] : []
    content {
      name  = "server.ha.raft.enabled"
      value = "true"
    }
  }

  # ----- Standalone storage (single node) -----
  dynamic "set" {
    for_each = var.vault_ha_enabled ? [] : [1]
    content {
      name  = "server.standalone.enabled"
      value = "true"
    }
  }

  # ----- Persistent storage -----
  set {
    name  = "server.dataStorage.storageClass"
    value = var.vault_storage_class
  }

  set {
    name  = "server.dataStorage.size"
    value = "10Gi"
  }

  # ----- Networking -----
  # ClusterIP keeps Vault internal — no external exposure needed.
  set {
    name  = "server.service.type"
    value = "ClusterIP"
  }

  # ----- UI -----
  # Enable the Vault web UI for debugging and operational visibility.
  # In production you may want to restrict access via a NetworkPolicy or
  # disable the UI entirely.
  set {
    name  = "ui.enabled"
    value = "true"
  }

  set {
    name  = "ui.serviceType"
    value = "ClusterIP"
  }

  # ----- Agent Injector -----
  # The agent injector enables automatic secret injection into pods via
  # annotations. We keep it enabled as it's useful for other workloads,
  # but cert-manager does not use it.
  set {
    name  = "injector.enabled"
    value = "true"
  }

  depends_on = [kubernetes_namespace.vault]
}

# ---------------------------------------------------------------------------
# Notes — Post-install manual steps required
# ---------------------------------------------------------------------------
#
# After this file is applied, Vault will be Running but SEALED (locked).
# You MUST complete the following before applying the remaining .tf files:
#
# 1. Port-forward Vault to your local machine:
#      kubectl port-forward -n <vault_namespace> svc/vault 8200:8200 &
#      export VAULT_ADDR=http://localhost:8200
#
# 2. Initialise Vault (first time only):
#      vault operator init \
#        -key-shares=5 \
#        -key-threshold=3 \
#        -format=json > vault-init.json
#      # Store vault-init.json securely — this contains your unseal keys and root token.
#      # NEVER commit it to version control.
#
# 3. Unseal Vault (required after every pod restart unless auto-unseal is configured):
#      vault operator unseal $(jq -r '.unseal_keys_b64[0]' vault-init.json)
#      vault operator unseal $(jq -r '.unseal_keys_b64[1]' vault-init.json)
#      vault operator unseal $(jq -r '.unseal_keys_b64[2]' vault-init.json)
#
# 4. Export the root token for Terraform:
#      export TF_VAR_vault_root_token=$(jq -r '.root_token' vault-init.json)
#
# 5. Continue with: terraform apply
#
# ---------------------------------------------------------------------------
# Production: Auto-Unseal
# ---------------------------------------------------------------------------
# To avoid manual unsealing after pod restarts, configure auto-unseal.
#
# AWS KMS (EKS) — add to the Helm release above:
#   set { name = "server.extraEnvironmentVars.VAULT_SEAL_TYPE",         value = "awskms" }
#   set { name = "server.extraEnvironmentVars.VAULT_AWSKMS_SEAL_KEY_ID", value = "<kms-key-arn>" }
#
# Azure Key Vault (AKS) — add to the Helm release above:
#   set { name = "server.extraEnvironmentVars.VAULT_SEAL_TYPE",              value = "azurekeyvault" }
#   set { name = "server.extraEnvironmentVars.VAULT_AZUREKEYVAULT_VAULT_NAME", value = "<akv-name>" }
#   set { name = "server.extraEnvironmentVars.VAULT_AZUREKEYVAULT_KEY_NAME",   value = "<akv-key-name>" }
# ---------------------------------------------------------------------------
