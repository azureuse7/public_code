#############################################
# Required Terraform Version
terraform {
  required_version = ">= 1.0.0" 

#############################################
# Required Providers and their Versions (here we have declared azurem that is Azure Resource Manager )
  required_providers {            
    azurerm = {
      source  = "hashicorp/azurerm"
      version = ">= 2.0" # Optional but recommended
    }
  }

#############################################
# Terraform Backend
  backend "azurerm" { 
    resource_group_name   = "terraform-storage-rg"
    storage_account_name  = "terraformstate201"
    container_name        = "tfstatefiles"
    key                   = "terraform.tfstate"
  }  
  experiments = [ example ]# Experimental (Not required)
  provider_meta "my-provider" { # Super Advanced (Not required)
    hello = "world"
  }
}
