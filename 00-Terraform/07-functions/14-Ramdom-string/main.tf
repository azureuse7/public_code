# Terraform Block
terraform {
  required_version = ">= 0.15"
  required_providers {
    azurerm = {
      source = "hashicorp/azurerm"
      version = "1.44.0"
      #version = ">= 2.0" 
    }
    random = {
      source = "hashicorp/random"
      version = ">= 3.0"
    }
  }
}

# Provider Block
provider "azurerm" {
# features {}          
}

# Resource-1: Azure Resource Group
resource "azurerm_resource_group" "myrg1" {
  name = "myrg-1"
  location = "East US"
}

# Resource-2: Random String 
resource "random_string" "myrandom" {
  length = 16
  upper = false 
  special = false
}

# Resource-3: Azure Storage Account 
resource "azurerm_storage_account" "mysa" {
  name                     = "mysa${random_string.myrandom.id}"
  resource_group_name      = azurerm_resource_group.myrg1.name
  location                 = azurerm_resource_group.myrg1.location
  account_tier             = "Standard"
  account_replication_type = "GRS"
  account_encryption_source = "Microsoft.Storage"

  tags = {
    environment = "staging"
  }
}

#------------------------------------------------------
# random_integer
#------------------------------------------------------

resource "random_integer" "demo07_random_number" {
  min = 5
  max = 100
}

output "demo07_random_number" {
  value = random_integer.demo07_random_number.result
}

#------------------------------------------------------
# random_uuid
#------------------------------------------------------

resource "random_uuid" "demo08_random_id" {}

output "demo08_random_id" {
  value = random_uuid.demo08_random_id.result
}

#------------------------------------------------------
# random_string
#------------------------------------------------------

resource "random_string" "demo06_random_password" {
  length           = 20
  special          = true
  override_special = "!@#$%&*()-_=+[]{}<>:?"
  min_special      = 2
  min_upper        = 2
  min_lower        = 5
  min_numeric      = 3
}

output "demo06_random_password" {
  value = random_string.demo06_random_password.result
}