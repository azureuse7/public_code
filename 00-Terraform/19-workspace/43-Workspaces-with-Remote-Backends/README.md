# Terraform Workspaces with Remote Backend

## Step-01: Introduction

This section demonstrates how Terraform workspaces work with a remote backend (Azure Storage). Each workspace gets its own isolated state file in the storage container.

- Use a Terraform remote backend (Azure Storage)
- Create 3 additional workspaces (`dev`, `staging`, `prod`) alongside the default workspace
- Understand how Terraform state files are stored in Azure Storage Account for multiple workspaces

## Step-02: `c1-versions.tf`

Add the backend block to the Terraform settings block to configure remote state storage:

```hcl
# Terraform state storage to Azure Storage Container
backend "azurerm" {
  resource_group_name  = "terraform-storage-rg"
  storage_account_name = "terraformstate201"
  container_name       = "tfstatefiles"
  key                  = "cliworkspaces-terraform.tfstate"
}
```

## Step-03: Create Workspaces and Verify State Files in the Storage Account

```bash
# Terraform initialize
# Observation:
# 1. Go to Azure Management Console -> terraform-storage-rg -> terraformstate201 -> tfstatefiles
# 2. Verify the file named "cliworkspaces-terraform.tfstate"
# 3. Verify the file size (approximately 155 B)
terraform init

# List workspaces
terraform workspace list

# Show current workspace
terraform workspace show

# Create workspaces
terraform workspace new dev
terraform workspace new staging
terraform workspace new prod

# Verify the workspace-specific state file names in the storage account:
# cliworkspaces-terraform.tfstate:dev
# cliworkspaces-terraform.tfstate:staging
# cliworkspaces-terraform.tfstate:prod

# Delete workspaces
terraform workspace select default
terraform workspace delete dev
terraform workspace delete staging
terraform workspace delete prod

# Verify the storage account after deletion
# Observation:
# 1. All workspace-specific state files should be deleted automatically when workspaces are deleted.
# 2. Only "cliworkspaces-terraform.tfstate" (the default workspace file) should remain,
#    because the default workspace cannot be deleted.
```

## Step-04: Clean Up the Local Folder

```bash
rm -rf .terraform*
```

## References

- [Terraform Workspaces](https://www.terraform.io/docs/language/state/workspaces.html)
- [Managing Workspaces](https://www.terraform.io/docs/cli/workspaces/index.html)
