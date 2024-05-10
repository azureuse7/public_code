locals {
  customer_subnets = { for gautam, sana in try(var.virtual) :
    gautam => { for bikram, vickey in sana :
      bikram => {
        name                                           = try(vickey.name, bikram)
        cidr                                           = vickey.cidr
        enforce_private_link_endpoint_network_policies = vickey.private_link_endpoint_enabled
        enforce_private_link_service_network_policies  = vickey.private_link_service_enabled
        nsg                                            = vickey.nsg       
        subnet_type = vickey.subnet_type
      }
    }
  }
}

variable "virtual" {
  default = {
    subnets = {
      aks1 = {
        name                          = "sana"
        cidr                          = "0.0.0.0/24"
        private_link_endpoint_enabled = true
        private_link_service_enabled  = false
        service_endpoints             = []
        subnet_type                   = "standard"
        nsg                           = "gautam"
      }
      aks2 = {
        cidr                          = "1.1.1.1/25"
        private_link_endpoint_enabled = true
        private_link_service_enabled  = false
        service_endpoints             = []
        subnet_type                   = "standard"
        nsg                           = "sana"
      }
    }
  }
}

output "sana" {
  value = local.customer_subnets
}