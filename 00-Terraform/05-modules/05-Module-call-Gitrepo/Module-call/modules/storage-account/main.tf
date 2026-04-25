#Create resource group
resource "azurerm_resource_group" "rg" {
    name     = "rg-myapp"
    location = "uksouth"
}