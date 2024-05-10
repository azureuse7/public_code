
#Azure provider
provider "azurerm" {
  features {}
}


#create resource group
resource "azurerm_resource_group" "rqg" {
  name     = "rg-354ample"
  location = "westus2"
}

# terraform -replace="rg-354ample"
# terraform taint rg-354ample

# For Module 
# List Resources from State
# terraform state list

# Taint a Resource
# terraform taint <RESOURCE-NAME>
# terraform taint module.vnet.azurerm_subnet.subnet[2]