
provider "azurerm" {
  features {}
}

terraform {
  backend "azurerm" {
  }
}

resource "azurerm_resource_group" "rg" {
  name     = local.vm-name
  location = var.LOCATION
}

variable "LOCATION" {
  default = "uksouth"
}

resource "random_string" "vm-name" {
  length  = 12
  upper   = false
  number  = false
  lower   = true
  special = false
}

locals {
  vm-name = "${random_string.vm-name.result}-vm"
}

