# Terraform Workspaces with Local Backend

## Step-01: Introduction

Terraform workspaces allow you to manage multiple distinct sets of infrastructure resources from a single configuration directory. This section uses a local backend to demonstrate workspace isolation.

- Use the Terraform local backend
- Create 2 workspaces (`default` and `dev`) in addition to the default workspace
- Update Terraform manifests to support `terraform.workspace`
- Master the following `terraform workspace` commands:
  1. `terraform workspace show`
  2. `terraform workspace list`
  3. `terraform workspace new`
  4. `terraform workspace select`
  5. `terraform workspace delete`

## Step-02: Review Terraform Configs and Make Changes

Copy `terraform-manifests` from `38-Terraform-Remote-State-Storage-and-Locking` and make the following changes.

## Step-03: `c1-versions.tf`

Remove the backend block from the Terraform settings block if one is present.

```hcl
# Remove this block if present
backend "azurerm" {
  resource_group_name  = "terraform-storage-rg"
  storage_account_name = "terraformstate201"
  container_name       = "tfstatefiles"
  key                  = "terraform.tfstate"
}
```

## Step-04: `c3-locals.tf`

- **`${terraform.workspace}`** — evaluates to the name of the currently active workspace
- **Common use case 1:** Use the workspace name as part of resource naming or tagging
- **Common use case 2:** Reference the workspace name to change behavior per environment (for example, using smaller VM sizes in non-default workspaces)

Replace all occurrences of `${var.environment}` with `${terraform.workspace}` in resource names:

```hcl
rg_name  = "${var.business_unit}-${terraform.workspace}-${var.resoure_group_name}"
vnet_name = "${var.business_unit}-${terraform.workspace}-${var.virtual_network_name}"
snet_name = "${var.business_unit}-${terraform.workspace}-${var.subnet_name}"
pip_name  = "${var.business_unit}-${terraform.workspace}-${var.publicip_name}"
nic_name  = "${var.business_unit}-${terraform.workspace}-${var.network_interface_name}"
vm_name   = "${var.business_unit}-${terraform.workspace}-${var.virtual_machine_name}"
```

## Step-05: `c5-virtual-network.tf`

Update the Public IP `domain_name_label` to include `${terraform.workspace}`:

```hcl
# Create Public IP Address
resource "azurerm_public_ip" "mypublicip" {
  name                = local.pip_name
  resource_group_name = azurerm_resource_group.myrg.name
  location            = azurerm_resource_group.myrg.location
  allocation_method   = "Static"
  domain_name_label   = "app1-${terraform.workspace}-${random_string.myrandom.id}"
  tags                = local.common_tags
}
```

## Step-06: Create Resources in the Default Workspace

Every initialized working directory starts with a workspace named `default`. Only one workspace can be selected at a time.

```bash
# Terraform initialize
terraform init

# List workspaces
terraform workspace list

# Show current workspace
terraform workspace show

# Terraform plan
# Observation:
# 1. Resource names will include "default" in place of the environment variable
# 2. Resource Group Name: it-default-rg
# 3. Virtual Network: it-default-vnet
# 4. Subnet Name: it-default-subnet
# 5. Public IP Name: it-default-publicip
# 6. Network Interface Name: it-default-nic
# 7. Virtual Machine Name: it-default-vm
terraform plan

# Terraform apply
terraform apply -auto-approve

# Verify in the Azure Management Console that resource names contain "default"

# Access the application (replace with actual DNS name)
# http://<public-ip-dns-name>
```

## Step-07: Create a New Workspace and Provision Infrastructure

```bash
# Create the dev workspace
terraform workspace new dev

# Verify the new workspace folder was created
cd terraform.tfstate.d
cd dev
ls
cd ../../

# Terraform plan
# Observation:
# 1. Resource names will include "dev" in place of the environment variable
# 2. Resource Group Name: it-dev-rg
# 3. Virtual Network: it-dev-vnet
# 4. Subnet Name: it-dev-subnet
# 5. Public IP Name: it-dev-publicip
# 6. Network Interface Name: it-dev-nic
# 7. Virtual Machine Name: it-dev-vm
terraform plan

# Terraform apply
terraform apply -auto-approve

# Verify the dev workspace state file
# Observation: terraform.tfstate should now exist at:
# <working-directory>/terraform.tfstate.d/dev/terraform.tfstate
cd terraform.tfstate.d/dev
ls
cd ../../

# Verify resources in the Azure Management Console

# Access the application (replace with actual DNS name)
# http://<public-ip-dns-name>
```

## Step-08: Switch Workspace and Destroy Resources

Switch from `dev` to `default` and destroy resources in the default workspace.

```bash
# Show current workspace
terraform workspace show

# List workspaces
terraform workspace list

# Select the default workspace
terraform workspace select default

# Destroy resources in the default workspace
terraform destroy -auto-approve

# Verify in the Azure Management Console that all resources are deleted
```

## Step-09: Delete the `dev` Workspace

The `default` workspace cannot be deleted. Other workspaces can be deleted only after their resources are destroyed.

```bash
# Attempt to delete the dev workspace (will fail if not empty)
terraform workspace delete dev
# Observation:
# Workspace "dev" is not empty.
# Deleting "dev" can result in dangling resources: resources that
# exist but are no longer manageable by Terraform. Please destroy
# these resources first. If you want to delete this workspace
# anyway and risk dangling resources, use the '-force' flag.

# Switch to the dev workspace
terraform workspace select dev

# Destroy resources in the dev workspace
terraform destroy -auto-approve

# Attempt to delete while dev is the active workspace (will fail)
terraform workspace delete dev
# Observation:
# Workspace "dev" is your active workspace.
# You cannot delete the currently active workspace. Please switch
# to another workspace and try again.

# Switch back to the default workspace
terraform workspace select default

# Delete the dev workspace
terraform workspace delete dev
# Observation: Successfully deleted workspace "dev"

# Verify in the Azure Management Console that all resources are deleted
```

## Step-10: Clean Up the Local Folder

```bash
rm -rf .terraform*
rm -rf terraform.tfstate*
```

## References

- [Terraform Workspaces](https://www.terraform.io/docs/language/state/workspaces.html)
- [Managing Workspaces](https://www.terraform.io/docs/cli/workspaces/index.html)
