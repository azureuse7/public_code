# Terraform Provider Dependency Lock File

## Step-01: Introduction

The Terraform dependency lock file (`.terraform.lock.hcl`) was introduced in Terraform v0.14. It records the exact provider versions used in a configuration so that the same versions are installed consistently across different machines and environments.

- Understand the importance of the dependency lock file introduced in `Terraform v0.14`

## Step-02: Create or Review `c1-versions.tf`

- Discusses Terraform, Azure, and Random Pet provider versions
- Discusses Azure RM provider version `1.44.0`
- Note: the `features {}` block is not required in Azure RM provider version `1.44.0`
- Reference: [Azure Provider v1.44.0 Documentation](https://registry.terraform.io/providers/hashicorp/azurerm/1.44.0/docs)

```hcl
# Terraform Block
terraform {
  required_version = ">= 1.0.0"
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "1.44.0"
      #version = ">= 2.0" # Commented for dependency lock file demo
    }
    random = {
      source  = "hashicorp/random"
      version = ">= 3.0"
    }
  }
}

# Provider Block
provider "azurerm" {
  # features {}  # Commented for dependency lock file demo
}
```

## Step-03: Create or Review `c2-resource-group-storage-container.tf`

- [Azure Resource Group resource](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/resource_group)
- [Random String resource](https://registry.terraform.io/providers/hashicorp/random/latest/docs/resources/string)
- [Azure Storage Account resource - Latest](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/storage_account)
- [Azure Storage Account resource - v1.44.0](https://registry.terraform.io/providers/hashicorp/azurerm/1.44.0/docs/resources/storage_account)

```hcl
# Resource-1: Azure Resource Group
resource "azurerm_resource_group" "myrg1" {
  name     = "myrg-1"
  location = "East US"
}

# Resource-2: Random String
resource "random_string" "myrandom" {
  length  = 16
  upper   = false
  special = false
}

# Resource-3: Azure Storage Account
resource "azurerm_storage_account" "mysa" {
  name                      = "mysa${random_string.myrandom.id}"
  resource_group_name       = azurerm_resource_group.myrg1.name
  location                  = azurerm_resource_group.myrg1.location
  account_tier              = "Standard"
  account_replication_type  = "GRS"
  account_encryption_source = "Microsoft.Storage"

  tags = {
    environment = "staging"
  }
}
```

## Step-04: Initialize and Apply the Configuration

```bash
# Start with the base v1.44 lock file
cp .terraform.lock.hcl-v1.44 .terraform.lock.hcl
# Observation: This ensures that when terraform init runs, provider versions
# are resolved from this lock file.

# Initialize Terraform
terraform init

# Compare both files
diff .terraform.lock.hcl-v1.44 .terraform.lock.hcl

# Validate Terraform configuration files
terraform validate

# Execute Terraform plan
terraform plan

# Create resources
terraform apply
```

The `.terraform.lock.hcl` file records three key items for each provider:

1. Provider version
2. Version constraints
3. Hashes

## Step-05: Upgrade the Azure Provider Version

For the Azure provider, changing the version constraint to `">= 2.0.0"` and running `terraform init -upgrade` will upgrade to the latest matching version.

```bash
# In c1-versions.tf, comment out 1.44.0 and uncomment ">= 2.0"
#   version = "1.44.0"
    version = ">= 2.0"

# Upgrade the Azure provider version
terraform init -upgrade

# Back up the updated lock file
cp .terraform.lock.hcl terraform.lock.hcl-V2.X.X
```

Review `.terraform.lock.hcl` after the upgrade:

1. Note the updated Azure provider version
2. Compare `.terraform.lock.hcl-v1.44` and `terraform.lock.hcl-V2.X.X`

## Step-06: Run Terraform Apply with the Latest Azure Provider

Running `terraform plan` after the upgrade will fail because the `account_encryption_source` argument was removed in Azure provider v2.x.

```bash
# Terraform plan
terraform plan

# Terraform apply
terraform apply
```

**Error message:**

```log
╷
│ Error: Unsupported argument
│
│   on c2-resource-group-storage-container.tf line 21, in resource "azurerm_storage_account" "mysa":
│   21:   account_encryption_source = "Microsoft.Storage"
│
│ An argument named "account_encryption_source" is not expected here.
╵
```

## Step-07: Comment Out `account_encryption_source`

When performing a major provider version upgrade, some arguments may be removed or renamed. The `.terraform.lock.hcl` file helps avoid unexpected breakage by pinning provider versions consistently across environments.

```hcl
# Resource-3: Azure Storage Account
resource "azurerm_storage_account" "mysa" {
  name                     = "mysa${random_string.myrandom.id}"
  resource_group_name      = azurerm_resource_group.myrg1.name
  location                 = azurerm_resource_group.myrg1.location
  account_tier             = "Standard"
  account_replication_type = "GRS"
  #account_encryption_source = "Microsoft.Storage"

  tags = {
    environment = "staging"
  }
}
```

## Step-08: Uncomment the `features {}` Block in the Azure Provider Block

Azure provider v2.x and later require a `features {}` block in the provider configuration. Uncomment it now.

```hcl
# Provider Block
provider "azurerm" {
  features {}
}
```

**Error when `features {}` is missing:**

```log
╷
│ Error: Insufficient features blocks
│
│   on  line 0:
│   (source code not available)
│
│ At least 1 "features" blocks are required.
╵
```

## Step-09: Run Terraform Plan and Apply

After commenting out `account_encryption_source` and uncommenting `features {}`, the plan and apply should succeed. The storage account will migrate to `StorageV2` as a result of Azure provider v2.x default changes.

```bash
# Terraform plan
terraform plan

# Terraform apply
terraform apply
```

## Step-10: Clean Up

```bash
# Destroy resources
terraform destroy

# Delete Terraform files
# Note: .terraform.lock.hcl-V2.X.X and .terraform.lock.hcl-V1.44 are kept for demo purposes
rm -rf .terraform
rm -rf .terraform.lock.hcl

# Delete Terraform state file
rm -rf terraform.tfstate*
```

## Step-11: Reset to Original Demo State

To allow others to run through this demo from the beginning:

```hcl
# Change-1: c1-versions.tf - pin back to v1.44.0
      version = "1.44.0"
      #version = ">= 2.0"

# Change-2: c1-versions.tf - leave features block commented
# features {}

# Change-3: c2-resource-group-storage-container.tf - restore account_encryption_source
  account_encryption_source = "Microsoft.Storage"
```

## References

- [Random Pet Provider](https://registry.terraform.io/providers/hashicorp/random/latest/docs/resources/pet)
- [Dependency Lock File](https://www.terraform.io/docs/configuration/dependency-lock.html)
- [Terraform New Features in v0.14](https://learn.hashicorp.com/tutorials/terraform/provider-versioning?in=terraform/0-14)
