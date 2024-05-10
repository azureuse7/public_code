#Create resource group
resource "azurerm_resource_group" "rg" {
    name     = "version4"
    location = "uksouth"
}