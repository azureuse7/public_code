# https://www.techielass.com/using-terraform-with-azure-key-vault-to-retrieve-secret-values-2/

# Step 1: create the Key Vault:

# az keyvault create --name "Techielasskeyvault" --resource-group "techielassrg" --location "East US"


# Step 2: Create a secret in the Azure Key Vault
# az keyvault secret set --vault-name "techielasskeyvault" --name "techielass-secret" --value "scotlandrules"


# Step 3: Retrieve an Azure Key Vault secret using Terraform
# provider "azurerm" {
#   features {}
# }

# data "azurerm_key_vault" "existing" {
#   name                = "techielasskeyvault"
#   resource_group_name = "techielassrg"
# }

# The next section we add to our Terraform file is:

# data "azurerm_key_vault_secret" "example" {
#   name         = "techielasssecret"
#   key_vault_id = data.azurerm_key_vault.existing.id
# }

# This is instructing Terraform to retrieve a specific secret from our key vault.

# output "secret_value" {
#   value = nonsensitive(data.azurerm_key_vault_secret.example.value)
# }


provider "azurerm" {
  features {}
}

data "azurerm_key_vault" "techielasskv" {
  name                = "techielasssecrets"
  resource_group_name = "techielassrg"
}

data "azurerm_key_vault_secret" "techielasssecret" {
  name         = "techielass-secret"
  key_vault_id = data.azurerm_key_vault.techielasskv.id
}

resource "azurerm_resource_group" "rg" {
  name     = "techielassstorage"
  location = "eastus"
}

resource "azurerm_storage_account" "techielasssa" {
  name                     = data.azurerm_key_vault_secret.techielasssecret.value
  resource_group_name      = azurerm_resource_group.rg.name
  location                 = azurerm_resource_group.rg.location
  account_tier             = "Standard"
  account_replication_type = "LRS"

  depends_on = [
    azurerm_resource_group.rg
  ]
}