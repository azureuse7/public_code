#Now how to use it on line 69 
resource "azurerm_network_interface" "adds_nic0" {
  name                            = ""
  resource_group_name             = azurerm_resource_group.adds-rg.name
  location                        = azurerm_resource_group.adds-rg.location
  count                           = var.zone_count
  enable_ip_forwarding            = false

  ip_configuration {
    name                          = ""
    subnet_id                     = data.azurerm_subnet.subnet.id
    private_ip_address_allocation = "Static"
    private_ip_address            = ""
    primary                       = true
  }
}


# Get details on the current connection to Azure
data "azurerm_client_config" "current" {
}

resource "azurerm_key_vault" "adds" {
  name                            = ""
  enabled_for_deployment          = true
  enabled_for_template_deployment = true
  location                        = azurerm_resource_group.adds-rg.location
  resource_group_name             = azurerm_resource_group.adds-rg.name
  sku_name                        = var.keyvalut_sku_name
  soft_delete_retention_days      = var.keyvalut_soft_delete_retention_days
  tenant_id                       = data.azurerm_client_config.current.tenant_id
  purge_protection_enabled        = false
  lifecycle {
    ignore_changes = [tags]
  }

  # Add access to the user running the code (should be the SPN)
  access_policy {
    tenant_id = data.azurerm_client_config.current.tenant_id
    object_id = data.azurerm_client_config.current.object_id

    secret_permissions = [
      "delete",
      "get",
      "list",
      "purge",
      "set"
    ]
  }
}