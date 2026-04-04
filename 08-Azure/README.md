# Microsoft Azure Services

> Reference guides, Terraform configurations, and CLI commands for core Azure services — covering policy, Key Vault, networking, identity, load balancing, and serverless.

---

## Contents

| Directory / File | Topic |
|-----------------|-------|
| [02-text/](02-text/) | Azure fundamentals overview |
| [03-Custom-Policy/](03-Custom-Policy/) | Custom Azure Policy — write and assign custom policy definitions |
| [04-azure_policy/](04-azure_policy/) | Built-in Azure Policy examples |
| [05-azure_policy_custom/](05-azure_policy_custom/) | Custom policy with Terraform |
| [06-Private-endpoint and service-endpoint/](06-Private-endpoint%20and%20service-endpoint/) | Private Endpoints vs Service Endpoints — when to use each |
| [07-Keyvault/](07-Keyvault/) | Azure Key Vault — secrets, keys, certificates |
| [08-Managed-Idenity/](08-Managed-Idenity/) | System-assigned and user-assigned Managed Identity |
| [09-Application-Gateway/](09-Application-Gateway/) | Application Gateway — layer-7 load balancing and WAF |
| [10-Refresh/](10-Refresh/) | Terraform refresh-only for Azure resources |
| [11-Terratest/](11-Terratest/) | Terratest — Go-based infrastructure tests for Azure |
| [13-Networking/](13-Networking/) | VNet, subnets, NSGs, peering, UDRs |
| [15-WAF/](15-WAF/) | Web Application Firewall policies and rules |
| [16-Azure Private DNS/](16-Azure%20Private%20DNS/) | Private DNS zones — custom DNS resolution inside VNets |
| [17-Azure Service Tags/](17-Azure%20Service%20Tags/) | Service Tags — simplify NSG rules for Azure services |
| [18-Loadbalancer/](18-Loadbalancer/) | Azure Load Balancer — layer-4 inbound/outbound rules |
| [19-Managed-Idenity/](19-Managed-Idenity/) | Managed Identity advanced patterns |
| [20-RBAC/](20-RBAC/) | Azure RBAC — built-in and custom roles, role assignments |
| [21-Azure Cosmos DB.md](21-Azure%20Cosmos%20DB.md) | Cosmos DB — NoSQL, APIs, partitioning, consistency levels |
| [22-Azure Cosmos DB-cli.md](22-Azure%20Cosmos%20DB-cli.md) | Cosmos DB CLI commands |
| [23-Azure Function.md](23-Azure%20Function.md) | Azure Functions — serverless compute triggers and bindings |
| [24-Azure Logic Apps.md](24-Azure%20Logic%20Apps.md) | Logic Apps — low-code workflow automation |
| [25-Azure Table Storage.md](25-Azure%20Table%20Storage.md) | Table Storage — lightweight NoSQL key-value store |
| [26-Azure Event Grid.md](26-Azure%20Event%20Grid.md) | Event Grid — event-driven messaging and routing |

---

## Key Concepts

### Managed Identity vs Service Principal

| | Managed Identity | Service Principal |
|-|-----------------|-------------------|
| Credentials | None — Azure manages automatically | Client secret or certificate required |
| Rotation | Automatic | Manual |
| Scope | Azure resources only | Any OAuth2 client |
| Best for | Azure-to-Azure auth | External apps, CI/CD pipelines |

### Private Endpoint vs Service Endpoint

| | Private Endpoint | Service Endpoint |
|-|-----------------|-----------------|
| Traffic path | Through Azure private network via NIC | Optimised route but still exits VNet conceptually |
| IP | Private IP in your VNet | Public IP of the service |
| DNS | Requires private DNS zone | No DNS change needed |
| Use case | Maximum isolation (PaaS behind VNet) | Simpler setup, lower latency to Azure services |

### RBAC Quick Reference
```bash
# List role assignments
az role assignment list --assignee <object-id> --output table

# Assign a role
az role assignment create \
  --assignee <object-id> \
  --role "Contributor" \
  --scope /subscriptions/<sub-id>/resourceGroups/<rg>
```

### Key Vault Quick Reference
```bash
# Create a key vault
az keyvault create --name <kv-name> --resource-group <rg> --location <region>

# Set a secret
az keyvault secret set --vault-name <kv-name> --name "MySecret" --value "MyValue"

# Read a secret
az keyvault secret show --vault-name <kv-name> --name "MySecret" --query value -o tsv
```
