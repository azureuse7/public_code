#Azure provider
provider "azurerm" {
  features {}
}

#create resource group
resource "azurerm_resource_group" "rqg" {
  name     = "rg-354ample"
  location = "westus2"
}

# Destroy-->  terraform destroy -target="rqg.rg-354ample"