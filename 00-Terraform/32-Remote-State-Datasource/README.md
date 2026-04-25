# Terraform Remote State Datasource

## Step-01: Introduction

The Terraform remote state datasource allows one Terraform project to read the output values from another project's state file. This enables a multi-project architecture where infrastructure is split across separate configurations (for example, network resources managed separately from compute resources).

- Reference: [Terraform Remote State Datasource](https://www.terraform.io/docs/language/state/remote-state-data.html)
- Demo: Remote state storage with two projects

## Step-02: Project-1: Create/Review Terraform Configs

The following files define the network infrastructure for Project-1:

1. `c1-versions.tf`
2. `c2-variables.tf`
3. `c3-locals.tf`
4. `c4-resource-group.tf`
5. `c5-virtual-network.tf`
6. `c6-outputs.tf`
7. `terraform.tfvars`

## Step-03: Project-1: Execute Terraform Commands

```bash
# Change to the project-1 directory
cd project-1-network

# Terraform initialize
terraform init

# Terraform validate
terraform validate

# Terraform plan
terraform plan

# Terraform apply
terraform apply -auto-approve

# Verify the following resources were created:
# 1. Resource Group
# 2. Virtual Network
# 3. Virtual Network Subnet
# 4. Public IP
# 5. Network Interface
# 6. Storage Account (for TF state file)
```

## Step-04: Project-2: Create/Review Terraform Configs

The following files define the compute infrastructure for Project-2, which reads networking outputs from Project-1's remote state:

1. `c0-terraform-remote-state-datasource.tf`
2. `c1-versions.tf`
3. `c2-variables.tf`
4. `c3-locals.tf`
5. `c4-linux-virtual-machine.tf`
6. `c5-outputs.tf`
7. `terraform.tfvars`

## Step-05: Project-2: `c0-terraform-remote-state-datasource.tf`

This file configures the remote state datasource that reads outputs from Project-1's state file stored in Azure Storage.

```hcl
# Terraform Remote State Datasource
data "terraform_remote_state" "project1" {
  backend = "azurerm"
  config = {
    resource_group_name  = "terraform-storage-rg"
    storage_account_name = "terraformstate201"
    container_name       = "tfstatefiles"
    key                  = "network-terraform.tfstate"
  }
}

/*
Outputs accessible from Project-1:
1. Resource Group Name:
   data.terraform_remote_state.project1.outputs.resource_group_name
2. Resource Group Location:
   data.terraform_remote_state.project1.outputs.resource_group_location
3. Network Interface ID:
   data.terraform_remote_state.project1.outputs.network_interface_id
*/
```

## Step-06: Project-2: `c4-linux-virtual-machine.tf`

The core change in the Virtual Machine resource is replacing hardcoded or local references with values read from the Project-1 remote state datasource.

```hcl
# Before (using a single project)
resource_group_name   = azurerm_resource_group.myrg.name
location              = azurerm_resource_group.myrg.location
network_interface_ids = [azurerm_network_interface.myvmnic.id]

# After (using two projects with the Terraform Remote State Datasource)
resource_group_name   = data.terraform_remote_state.project1.outputs.resource_group_name
location              = data.terraform_remote_state.project1.outputs.resource_group_location
network_interface_ids = [data.terraform_remote_state.project1.outputs.network_interface_id]
```

## Step-07: Project-2: Execute Terraform Commands

```bash
# Change to the project-2 directory
cd project-2-app1

# Terraform initialize
terraform init

# Terraform validate
terraform validate

# Terraform plan
terraform plan

# Terraform apply
terraform apply -auto-approve

# Verify the following resources:
# 1. Resource Group
# 2. Virtual Network
# 3. Virtual Network Subnet
# 4. Public IP
# 5. Network Interface
# 6. Virtual Machine (verify the location and network interface it used)
# 7. Storage Account (for TF state file)
```

## Step-08: Project-2: Clean Up

```bash
# Change to the project-2 directory
cd project-2-app1

# Destroy resources
terraform destroy -auto-approve

# Delete local Terraform files
rm -rf .terraform*
```

## Step-09: Project-1: Clean Up

```bash
# Change to the project-1 directory
cd project-1-network

# Destroy resources
terraform destroy -auto-approve

# Delete local Terraform files
rm -rf .terraform*
```
