provider "kubernetes" {
  config_path = "~/.kube/config"
}
# Terraform
terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "2.40.0"
    }
  }
}

#Azure provider
provider "azurerm" {
  features {}
}

resource "azurerm_resource_group" "example" {
  name     = "aks-rg1"
  location = "West Europe"
}

# az aks get-credentials --resource-group aks-rg1 --name aksdemo1 --overwrite-existing && kubelogin convert-kubeconfig

resource "azurerm_kubernetes_cluster" "example" {
  name                = "aksdemo1"
  location            = azurerm_resource_group.example.location
  resource_group_name = azurerm_resource_group.example.name
  dns_prefix          = "exampleaks1"

  default_node_pool {
    name       = "default"
    node_count = 1
    vm_size    = "Standard_D2_v2"
  }

  identity {
    type = "SystemAssigned"
  }

}
