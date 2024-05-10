#Azure provider
provider "azurerm" {
  features {}
}

# Location Variable
variable "location" {
    type = string
    description = "Azure location of terraform server environment"
    default = "uksouth"
}

resource "azurerm_resource_group" "rg" {
    name     = "rg-testcondition"
    location =  try(local.access_policy.AzureDevOps.location1, "southcentralus")
                    # If var.location is null, than var.location should be "southcentralus"
}

locals {
  access_policy = {
    AzureDevOps = {
      location1          = uksouth
      location2         = eastus,
      location3         = qatarcentral
    }
  }
}