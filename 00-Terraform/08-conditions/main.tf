terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "2.40.0"
    }
  }
}

provider "azurerm" {
  features {}
}

variable "location" {
    type        = string
    description = "Azure location of terraform server environment"
    default     = ""
}

resource "azurerm_resource_group" "rg" {
    name     = "rg-testcondition"
    location = var.location != "" ? var.location : "southcentralus"
}
