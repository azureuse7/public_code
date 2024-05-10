# Terraform
terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "2.40.0"
    }
  }
}

#Azure provider
provider "azurerm" {
  features {}
}

# Location Variable
variable "location" {
    type = string
    description = "Azure location of terraform server environment"
    default = ""
}


#create resource group
resource "azurerm_resource_group" "rg" {
    name     = "rg-testcondition"
    location = var.location != "" ? var.location : "southcentralus"
                    # If True Then A Else B
}

# variable "environment" {
#   type    = string
#   default = "staging"
# }
 
# resource "azurerm_storage_account" "sa" {
#   name                     = "tamopssa"
#   resource_group_name      = azurerm_resource_group.rg.name
#   location                 = azurerm_resource_group.rg.location
#   account_tier             = "Standard"
#   account_replication_type = var.environment == "production" ? "GRS" :"LRS"
# }

# Passing in the variable environment as staging will set the storage account replication type to LRS, 
# only configure GRS when the variable environment is production. A great way to save some costs and 
# only give your Production environment the more premium features.