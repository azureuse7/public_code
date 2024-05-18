terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "=3.30.0"
    }
  }
}

provider "azurerm" {
  features {
    resource_group {
      prevent_deletion_if_contains_resources = false
    }
  }
}

resource "azurerm_resource_group" "main_resource_group" {
  name     = "RG-Terraform-on-Azure"
  location = "West Europe"
}


# Create Virtual-Network
resource "azurerm_virtual_network" "virtual_network" {
  name                = "Vnet"
  address_space       = ["10.0.0.0/16"]
  location            = azurerm_resource_group.main_resource_group.location
  resource_group_name = azurerm_resource_group.main_resource_group.name
}


# Create subnet for virtual-machine
resource "azurerm_subnet" "virtual_network_subnet" {
  name                 = "vm_subnet"
  resource_group_name  = azurerm_resource_group.main_resource_group.name
  virtual_network_name = azurerm_virtual_network.virtual_network.name
  address_prefixes     = ["10.0.1.0/24"]
}

# Create subnet for storage account
resource "azurerm_subnet" "storage_account_subnet" {
  name                 = "storage_account_subnet"
  resource_group_name  = azurerm_resource_group.main_resource_group.name
  virtual_network_name = azurerm_virtual_network.virtual_network.name
  address_prefixes     = ["10.0.2.0/24"]
}

# Create Linux Virtual machine
resource "azurerm_linux_virtual_machine" "example" {
  name                            = "example-machine"
  location                        = azurerm_resource_group.main_resource_group.location
  resource_group_name             = azurerm_resource_group.main_resource_group.name
  size                            = "Standard_F2"
  admin_username                  = "adminuser"
  admin_password                  = "14394Las?"
  disable_password_authentication = false
  network_interface_ids           = [
    azurerm_network_interface.virtual_machine_network_interface.id,
  ]


  os_disk {
    caching              = "ReadWrite"
    storage_account_type = "Standard_LRS"
  }

  source_image_reference {
    publisher = "Canonical"
    offer     = "UbuntuServer"
    sku       = "16.04-LTS"
    version   = "latest"
  }
}

resource "azurerm_network_interface" "virtual_machine_network_interface" {
  name                = "vm-nic"
  location            = azurerm_resource_group.main_resource_group.location
  resource_group_name = azurerm_resource_group.main_resource_group.name

  ip_configuration {
    name                          = "internal"
    subnet_id                     = azurerm_subnet.virtual_network_subnet.id
    private_ip_address_allocation = "Dynamic"
    public_ip_address_id          = azurerm_public_ip.vm_public_ip.id
  }
}

# Create Network-interface and public-ip for virtual-machien
resource "azurerm_public_ip" "vm_public_ip" {
  name                = "vm-public-ip-for-rdp"
  location            = azurerm_resource_group.main_resource_group.location
  resource_group_name = azurerm_resource_group.main_resource_group.name
  allocation_method   = "Static"
  sku                 = "Standard"
}

resource "azurerm_network_interface" "virtual_network_nic" {
  name                = "storage-private-endpoint-nic"
  location            = azurerm_resource_group.main_resource_group.location
  resource_group_name = azurerm_resource_group.main_resource_group.name

  ip_configuration {
    name                          = "storage-private-endpoint-ip-config"
    subnet_id                     = azurerm_subnet.virtual_network_subnet.id
    private_ip_address_allocation = "Dynamic"
  }
}

# Setup an Inbound rule because we need to connect to the virtual-machine using RDP (remote-desktop-protocol)
resource "azurerm_network_security_group" "traffic_rules" {
  name                = "vm_traffic_rules"
  location            = azurerm_resource_group.main_resource_group.location
  resource_group_name = azurerm_resource_group.main_resource_group.name

  security_rule {
    name                       = "virtual_network_permission"
    priority                   = 100
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "*"
    source_port_range          = "*"
    destination_port_range     = "22"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }
}

resource "azurerm_subnet_network_security_group_association" "private_nsg_asso" {
  subnet_id                 = azurerm_subnet.virtual_network_subnet.id
  network_security_group_id = azurerm_network_security_group.traffic_rules.id

}

# Setup storage_account and its container
resource "azurerm_storage_account" "storage_account" {
  name                     = <STORAGE_ACCOUNT_NAME>
  location                 = azurerm_resource_group.main_resource_group.location
  resource_group_name      = azurerm_resource_group.main_resource_group.name
  account_tier             = "Standard"
  account_replication_type = "LRS"
  account_kind             = "StorageV2"
  is_hns_enabled           = "true"

}

resource "azurerm_storage_data_lake_gen2_filesystem" "data_lake_storage" {
  name               = "rawdata"
  storage_account_id = azurerm_storage_account.storage_account.id

  lifecycle {
    prevent_destroy = false
  }
}

# Setup DNS zone
resource "azurerm_private_dns_zone" "dns_zone" {
  name                = "privatelink.blob.core.windows.net"
  resource_group_name = azurerm_resource_group.main_resource_group.name
}

resource "azurerm_private_dns_zone_virtual_network_link" "network_link" {
  name                  = "vnet-link"
  resource_group_name   = azurerm_resource_group.main_resource_group.name
  private_dns_zone_name = azurerm_private_dns_zone.dns_zone.name
  virtual_network_id    = azurerm_virtual_network.virtual_network.id
}

# Setup private-link
resource "azurerm_private_endpoint" "endpoint" {
  name                = "storage-private-endpoint"
  location            = azurerm_resource_group.main_resource_group.location
  resource_group_name = azurerm_resource_group.main_resource_group.name
  subnet_id           = azurerm_subnet.storage_account_subnet.id

  private_service_connection {
    name                           = "storage-private-service-connection"
    private_connection_resource_id = azurerm_storage_account.storage_account.id
    is_manual_connection           = false
    subresource_names              = ["blob"]
  }
}

resource "azurerm_private_dns_a_record" "dns_a" {
  name                = azurerm_storage_account.storage_account.name
  zone_name           = azurerm_private_dns_zone.dns_zone.name
  resource_group_name = azurerm_resource_group.main_resource_group.name
  ttl                 = 10
  records             = [azurerm_private_endpoint.endpoint.private_service_connection.0.private_ip_address]
}


# Additionally, I'm not sure whether it is possible to ping storage accounts. 
# To test I ran nslookup <STORAGE_ACCOUNT_NAME>.blob.core.windows.net both from my local 
# machine and from the Azure VM. In the former case, I got a public IP while in the latter 
# I got a private IP in the range defined in the Terraform config, which seems to be the 
# behaviour you are looking for.