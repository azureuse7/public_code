#Azure provider
provider "azurerm" {
  features {}
}

terraform {
  backend "local" {
    path = "C:/Users/Lenovo/Music/tfsqtate.tfstate"
  }
}
#create resource group
resource "azurerm_resource_group" "rqg" {
  name     = "rg-35435qraexample"
  location = "westus2"
}


# List state file       --> terraform state list
# Filtering by Resource --> terraform state list azurerm_resource_group.rqg 
# Filtering by ID       --> terraform state list -id=rqg 
# List attribues        --> terraform state show azurerm_resource_group.rqg
# Rename a rescouce     --> terraform state mv azurerm_resource_group.rqg azurerm_resource_group.rqggautam

# Using Terraform Import with Azure Resources
# https://www.youtube.com/watch?v=hgiVbjgy9cU&ab_channel=CloudSkillsFM
