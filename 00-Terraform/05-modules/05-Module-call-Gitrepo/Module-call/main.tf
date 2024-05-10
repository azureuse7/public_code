# Terraform
# terraform {
#   required_providers {
#     azurerm = {
#       source  = "hashicorp/azurerm"
#       version = "2.40.0"
#     }
#   }
# }

#Azure provider
provider "azurerm" {
  features {}
}


#Create resource group from local module 
# module "storage_account1" {
#   source    = "./modules/storage-account"
# }


#Create resource group from remote git (here the module is in the folder)
# module "storage_account2" {
#   source    = "github.com/gautam-thakur786/terraform-module1/01-modules-call-web/storage-account"
# }

# Create resource group from remote git
# module "storage_account3" {
#   source    = "github.com/gautam-thakur786/terraform-module1"
#  }

#Create resource group from remote git using feature branch
# module "storage_account3" {
#   source    = "github.com/gautam-thakur786/terraform-module1?ref=main"
# }

#Create resource group from remote git using tag (just to prove it change version from 4 to 3)
# module "storage_account3" {
#   source    = "github.com/gautam-thakur786/terraform-module1?ref=v.04"
# }

# To push Tags 
# Make changes
# git add .      
# git commit -m "w"
# git tag v.02 
# git push --tags