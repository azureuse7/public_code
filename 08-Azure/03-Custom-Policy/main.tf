locals {

  aks_seccomps_Profile = file("${path.module}/policy/initiative_policy_parameter_seccomps_Profile.json")

  aks_policies = {
    seccompsProfile = {
      policy_definition_id = "/providers/Microsoft.Authorization/policyDefinitions/975ce327-682c-4f2e-aa46-b9598289b86c"
      parameter_values     = local.aks_seccomps_Profile
      reference_id         = "seccompsProfile"
    }
  }
}

resource "azurerm_policy_set_definition" "aks" {
  name         = "gautamInitiative"
  policy_type  = "Custom"
  display_name = "Apply gautam AKS Policies"

  # Parameters for the policy definition. This field is a JSON string that maps to the Parameters field from the Policy Definition.
  parameters = file("${path.module}/policy/initiative_parameters.json")

  dynamic "policy_definition_reference" {
    for_each = local.aks_policies

    content {
      parameter_values     = policy_definition_reference.value["parameter_values"]
      policy_definition_id = policy_definition_reference.value["policy_definition_id"]
      reference_id         = policy_definition_reference.value["reference_id"]
    }
  }
}


resource "azurerm_subscription_policy_assignment" "aks" {
  name                 = "aksPolicy"
  display_name         = "Apply gautam AKS policies"
  policy_definition_id = azurerm_policy_set_definition.aks.id
  subscription_id      = data.azurerm_subscription.current.id

  parameters = templatefile("${path.module}/policy/assign_parameters.json", {
    seccomps_profile_effect = "disabled"
  })
}



provider "azurerm" {
  features {}
}
terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "2.78.0"
    }
  }
}

data "azurerm_subscription" "current" {}