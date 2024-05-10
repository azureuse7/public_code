# resource to create application_security_group
resource "azurerm_application_security_group" "item" {
  for_each            = toset(var.asg_names)
  name                = each.key
  location            = "uksouth"
  resource_group_name = "gautam"
}


variable "asg_names" {
  type = list(string)
  default = ["group1","group2"]

}

provider "azurerm" {
  features {}
}