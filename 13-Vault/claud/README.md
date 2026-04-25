# vault-certmanager-tf

Terraform module deploying HashiCorp Vault as an internal PKI Certificate Authority,
integrated with cert-manager for automated TLS certificate management on Kubernetes.

## File Structure

| File | Purpose |
|---|---|
| `providers.tf` | Terraform and provider version pinning |
| `variables.tf` | All input variables with descriptions and defaults |
| `terraform.tfvars.example` | Copy to `terraform.tfvars` and fill in values |
| `01-vault-install.tf` | Installs Vault via Helm |
| `02-vault-pki.tf` | Configures PKI engine, root CA, role, policy |
| `03-vault-k8s-auth.tf` | Enables Kubernetes auth method in Vault |
| `04-certmanager.tf` | Installs cert-manager + issuer ServiceAccount |
| `05-issuer.tf` | Creates the cert-manager Vault Issuer |
| `06-certificate.tf` | Declares the TLS Certificate resource |
| `07-ingress-nginx.tf` | Installs the NGINX Ingress Controller |
| `08-demo-app.tf` | Deploys demo app + Ingress with TLS |
| `outputs.tf` | Useful output values |

## Apply Order

Vault must be initialised and unsealed before the Vault provider can configure it.
Apply in two stages:

```bash
# Stage 1 — infrastructure only
terraform init
terraform apply \
  -target=helm_release.vault \
  -target=helm_release.cert_manager \
  -target=helm_release.ingress_nginx

# --- Manual steps: initialise and unseal Vault ---
kubectl port-forward -n vault svc/vault 8200:8200 &
export VAULT_ADDR=http://localhost:8200
vault operator init -key-shares=5 -key-threshold=3 -format=json > vault-init.json
vault operator unseal $(jq -r '.unseal_keys_b64[0]' vault-init.json)
vault operator unseal $(jq -r '.unseal_keys_b64[1]' vault-init.json)
vault operator unseal $(jq -r '.unseal_keys_b64[2]' vault-init.json)
export TF_VAR_vault_root_token=$(jq -r '.root_token' vault-init.json)

# Stage 2 — full apply
terraform apply
```

## .gitignore

```
terraform.tfvars
vault-init.json
*.tfstate
*.tfstate.backup
.terraform/
.terraform.lock.hcl
```
