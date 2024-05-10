# Go to Terraform Console
# terraform console

# Test lower() function
# Template: lower("STRING")
# lower("KALYAN REDDY")
# lower("STACKSIMPLIFY")

# Test upper() function
# Template: lower("string")
# upper("kalyan reddy")
# upper("stacksimplify")


#------------------------------------------------------
# locals, lower
#------------------------------------------------------

locals {
  common_tags = {
    CostCenter = var.cost_center_id
    Production = var.is_production
  }
}

resource "azurerm_resource_group" "demo01_rg" {
  name     = lower(var.rg_name)
  location = var.location

  tags = local.common_tags
}
