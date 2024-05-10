#lookup(map,key,default)

variable "site_names" {
  type        = list(string)
  default     = ["siteA", "siteB"]
  description = "Provide a list of all Contoso site names - Will be mapped to local var 'site_configs'"
}
locals {
  site_configs = {
    siteA = {
      resource_group_name = "Demo-Inf-SiteA-RG"
      location            = "UKSouth"
      allowed_ips         = ["8.8.8.8", "8.8.8.9"]
    },
    siteB = {
      resource_group_name = "Demo-Inf-SiteB-RG"
      location            = "UKWest"
      allowed_ips         = ["7.7.7.7", "7.7.7.8"]
    }
  }
}
resource "azurerm_resource_group" "RGS" {
  for_each = toset(var.site_names)
  name     = lookup(local.site_configs[each.value], "resource_group_name", null)
  location = lookup(local.site_configs[each.value], "location", null)
}

# in the above, search for resource_group_name if not aviable than null

# > lookup({a="ay", b="bee"}, "a", "what?")
# {a="ay", b="bee"} is the map Provided to the lookup
# key is a, so value  is ay 
# ay

# > lookup({a="ay", b="bee"}, "c", "what?")
# if it can't find the map use the default 
# what?

# > lookup({a="ay", b="bee"}, "b", "what?")
# bee 