#Azure provider
provider "azurerm" {
  features {}
}
# Terraform

data "azurerm_virtual_network" "example" {
  name                = "gautam"
  resource_group_name = "gautam"
}

resource "azurerm_policy_definition" "example" {
  name        = "only-deploy-in-westeurope"
  policy_type = "Custom"
  display_name= "sana"
  mode        = "All"

  policy_rule = <<POLICY_RULE
    {
    "if": {
      "not": {
        "field": "location",
        "equals": jsonencode["westeurope", "uksouth]
      }
    },
    "then": {
      "effect": "Deny"
    }
  }
POLICY_RULE
}

resource "azurerm_resource_policy_assignment" "example" {
  name                 = "example-policy-assignment"
  resource_id          = data.azurerm_virtual_network.example.id
  policy_definition_id = azurerm_policy_definition.example.id
}