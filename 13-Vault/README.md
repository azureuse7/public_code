# HashiCorp Vault: Secrets Management

> Vault is a secrets management platform that centralises storage, access control, and auditing for secrets (API keys, passwords, certificates, SSH keys). This section covers deployment on Kubernetes (AKS), authentication, secret engines, policies, and advanced use cases.

---

## Contents

| File | Topic |
|------|-------|
| [01-Initial-setup.md](01-Initial-setup.md) | Deploy Vault on AKS with Helm, unseal, and first login |
| [03-Vault-Authentication.md](03-Vault-Authentication.md) | Authentication methods — UI, CLI, tokens, Kubernetes auth |
| [04-Secret-engine.md](04-Secret-engine.md) | KV (Key-Value) secret engine — read/write/delete secrets |
| [05-High availability.md](05-High%20availability.md) | HA Vault setup with multiple replicas |
| [06-policy.md](06-policy.md) | ACL policies — grant read/write access to paths |
| [07-Injecting-value-sidecar.md](07-Injecting-value-sidecar.md) | Inject secrets into pods via the Vault Agent sidecar |
| [08-ssh.md](08-ssh.md) | Dynamic SSH credentials with the SSH secret engine |
| [09-PKI Secret Engine Overview.md](09-PKI%20Secret%20Engine%20Overview.md) | PKI engine — issue TLS certificates from Vault |

| Directory | Topic |
|-----------|-------|
| [01-Creating time-bound SSH keys using HashiCorp Vault/](01-Creating%20time-bound%20SSH%20keys%20using%20HashiCorp%20Vault/) | Terraform + Vault to generate time-limited SSH keys for AKS nodes |
| [02-Vault as Certificate Issuer on a Kubernetes Cluster/](02-Vault%20as%20Certificate%20Issuer%20on%20a%20Kubernetes%20Cluster/) | Use Vault PKI engine as a certificate authority in Kubernetes |

---

## Quick Start: Deploy Vault on AKS

```bash
# Add the HashiCorp Helm repo
helm repo add hashicorp https://helm.releases.hashicorp.com
helm repo update

# Install Vault with the UI exposed
helm install vault hashicorp/vault \
  --set='ui.enabled=true' \
  --set='ui.serviceType=LoadBalancer'

# Check pods
kubectl get pods

# Initialise Vault (generates unseal keys and root token)
kubectl exec -it vault-0 -- vault operator init

# Unseal (run 3 times with different keys)
kubectl exec -it vault-0 -- vault operator unseal <key>

# Access UI: http://<external-ip>:8200
```

---

## Core Concepts

| Concept | Description |
|---------|-------------|
| **Unseal keys** | Required to decrypt the Vault storage after a restart |
| **Root token** | Initial superuser token — store securely, rotate after setup |
| **Secret engine** | Plugin that stores or generates secrets (KV, PKI, SSH, AWS, etc.) |
| **Policy** | HCL document that grants `read`/`write`/`list` on secret paths |
| **Auth method** | How clients prove identity (token, Kubernetes SA, AppRole, etc.) |
| **Lease** | Time-limited credential — Vault automatically revokes expired leases |
| **Sidecar injection** | Vault Agent runs as a container in the pod and writes secrets to a shared volume |
