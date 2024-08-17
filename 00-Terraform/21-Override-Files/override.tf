# Resource-1: Azure Resource Group
resource "azurerm_resource_group" "myrg" {
  name = "gagan"  
  location = "westus"
}

#Notice we have same rescource name. but override.tf takes prioprty , it can also be abc-override.tf
