# Azure Quick Reference Notes

## Account Management

The following commands are used to manage your Azure account and subscriptions:

- `Connect-AzAccount` — Sign in to Azure using PowerShell
- `az account list --all` — List all Azure subscriptions
- `az account show` — Show the currently active subscription
- `Disconnect-AzAccount` — Sign out of Azure in PowerShell
- `az account set --subscription 'Visual Studio Professional Subscription'` — Set the active subscription

---

## Key Concepts and Rules

This section summarises important Azure rules and behaviours to remember.

- A single Availability Zone consists of more than one data centre.
- **NSG**: Must be in the same region, but can be used across Resource Groups and VNets.
- Log Analytics workspace can be in any region.
- Azure Application Gateway is a web traffic load balancer.
- A network interface must be in the same region as its VNet.
- Storage replication can be changed if the current technique is LRS or GRS.
- An App Service Plan and its Web App must be in the same region.
- .NET can run on both Windows and Linux, but ASP.NET runs on Windows only.
- A network interface can be moved to another Resource Group even if it is part of an existing virtual network.
- Fault domain count is 3; update domain count is 20.
- A gateway subnet is required for site-to-site VPN, but not for VNet peering.
- You can change the subnet connected to a VM, but not the VNet.
- A Policy Definition is used to enforce policy.
- Use `az aks create` to create an AKS cluster and `--enable-addons` to enable monitoring.
- To record connections: (1) Microsoft Insights, (2) Storage Account, (3) Enable Network Watcher flow logs.
- A client certificate must be installed on every client computer; it can be exported (used in site-to-site VPN).
- Standard Load Balancer has 99% availability.
- Connection Monitor in Network Watcher is used when an application is slow, or to monitor connectivity between two VMs.
- IP Flow Verify checks whether a security rule is blocking traffic.
- VNet peering must be configured in both directions.
