# Multiple variants of the same provider
# Sometimes you may need to create resources on one provider, but using different account or subscriptions. In such a case alias can be used uin the provider block:


provider "azurerm" {
  features {}
}

provider "azurerm" {
  features {}
  alias       = "foo"
  environment = "german"
}

resource "azurerm_resource_group" "default" {
  name     = "something"
  location = "westeurope"
}

resource "azurerm_resource_group" "foo" {
  name     = "someotherthing"
  location = "westeurope"
  provider = azurerm.foo
}

# The terraform providers command shows information about the provider requirements
# terraform providers