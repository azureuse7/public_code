provider "azurerm" {
  features {}
}

# Create Keyvault to store VM passwords
resource "azurerm_key_vault" "cve" {
  name                       = "cve354"
  location                   = azurerm_resource_group.cve_vm.location
  resource_group_name        = azurerm_resource_group.cve_vm.name
  sku_name                   = var.keyvault_sku_name
  soft_delete_retention_days = var.keyvault_soft_delete_retention_days
  tenant_id                  = data.azurerm_client_config.current.tenant_id
  purge_protection_enabled   = false

# Add access policy to the user running the code 
# basically this will create three policy, togther 

  dynamic "access_policy" {
    for_each = local.access_policy
    content {
      tenant_id          = access_policy.value["tenant_id"]
      object_id          = access_policy.value["object_id"]
      secret_permissions = access_policy.value["secret_permissions"]
    }
  }
}

locals {
  access_policy = {
    AzureDevOps = {
      tenant_id          = "a9a2d5a7-17e6-463b-9fc5-uetuteueu"
      object_id          = "837f1a08-6407-4639-b1dd-uetyutuuu",  #object_id  of usr azuredevops
      secret_permissions = ["Get", "Set"]
    }
    gautam = {
      tenant_id          = "a9a2d5a7-17e6-463b-9fc5-utyutyyu"
      object_id          = "a3ca9a64-e073-45fd-8dd4-utyututu",  #object_id  of user gautam
      secret_permissions = ["Get", "Set"]
    }
    gautam1 = {
      tenant_id          = "a9a2d5a7-17e6-463b-9fc5-utyutu"
      object_id          = "8421d496-292b-4522-8640-tyutyuytu",
      secret_permissions = ["Get", "Set"]
    }
  }
}