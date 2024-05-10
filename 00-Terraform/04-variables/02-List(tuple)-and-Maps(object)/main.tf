# Terraform Block
terraform {
  required_version = ">= 1.0.0"
  required_providers {
    azurerm = {
      source = "hashicorp/azurerm"
      version = ">= 2.0" 
    }
  }
}

# Provider Block
provider "azurerm" {
 features {}          
}

# Resource-1: Azure Resource Group
resource "azurerm_resource_group" "myrg" {
  name = "gautam-rg"
  location = "uksouth"
  tags = var.common_tags
}

# Input Variables
# Common Tags
variable "common_tags" {
  description = "Common Tags for Azure Resources"
  type = map(string)
  default = {
    "CLITool" = "Terraform",
    "Tag1" = "Azure"
  }
}

#####################################

# Create Virtual Network
resource "azurerm_virtual_network" "myvnet" {
  name                = "gautam-vnet"
  #address_space      = ["10.0.0.0/16"]
  address_space       = var.virtual_network_address_space
  #address_space       = [var.virtual_network_address_space[0]]
  location            = "uksouth"
  resource_group_name = azurerm_resource_group.myrg.name
  tags = var.common_tags
}


# Input Variables
#  Virtual Network address_space
variable "virtual_network_address_space" {
  description = "Virtual Network Address Space"
  type = list(string)
  default = ["10.0.0.0/16", "10.1.0.0/16", "10.2.0.0/16"]
}