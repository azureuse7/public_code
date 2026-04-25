# Explanation
# Sometimes you need to build infrastructure on more than 1 provider.
# Azure: Maybe you’ve got resources running on Azure and would like to add Cloudflare as a CDN.

terraform {
  required_version = ">= 0.13"
  required_providers {
    azurerm = {                      # this is just a name, it can be any thing abc 
      source = "hashicorp/azurerm"   # This is the real name
      version = "2.45.1"
    }
    cloudflare = {
      source = "cloudflare/cloudflare"  # Azure: Maybe you’ve got resources running on Azure and would like to add Cloudflare as a CDN.
      version = "2.13.2"
    }
  }
}

provider "azurerm" { # use the same name here 
  features {}
}

# The terraform providers schema command is used to print detailed schemas for the providers used in the current configuration.