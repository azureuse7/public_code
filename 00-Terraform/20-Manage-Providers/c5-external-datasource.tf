# Terraform Block
terraform {
  required_version = ">= 1.0.0"
  required_providers {
    random = {
      source = "hashicorp/random"
      version = ">= 3.0"
    }
    external = {
      source = "hashicorp/external"
      version = ">= 2.0"
    }        
  }
}

# Provider Block
provider "azurerm" {
 features {}          
}

# Random String Resource
resource "random_string" "myrandom" {
  length = 6
  upper = false 
  special = false
  number = false   
}


# Resource-1: Azure Resource Group
resource "azurerm_resource_group" "myrg" {
  name = "myrg-1"
  location = "East US"
}

# ssh key generator data source expects the below 3 inputs, and produces 3 outputs for use:
#  "${data.external.ssh_key_generator.result.public_key}" (contents)
#  "${data.external.ssh_key_generator.result.private_key}" (contents)
#  "${data.external.ssh_key_generator.result.private_key_file}" (path)
data "external" "ssh_key_generator" {
  program = ["bash", "${path.module}/shell-scripts/ssh_key_generator.sh"]
  
  query = {
    key_name = "terraformdemo"
    key_environment = "dev"
  }
}

# Outputs
output "public_key" {
  description = "public_key"
  value = data.external.ssh_key_generator.result.public_key
}

output "private_key" {
  description = "private_key"
  value = data.external.ssh_key_generator.result.private_key
}

output "private_key_file" {
  description = "private_key_file"
  value = data.external.ssh_key_generator.result.private_key_file 
}

# If we were cretaing a VM we could us this as   
# public_key = data.external.ssh_key_generator.result.public_key

