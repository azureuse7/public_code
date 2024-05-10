provider "azurerm" {
  features {}
}

variable "virtual_machine" {
  description = "The image source Id"
  default = {
    gautam = {
      name         = "gautam"
      image_source = "",
    }
    sana = {
      name         = "sana"
      image_source = "",
}
}
}

resource "azurerm_virtual_network" "example" {
  name                = "example-network"
  address_space       = ["10.0.0.0/16"]
  location            = azurerm_resource_group.cve_vm.location
  resource_group_name = azurerm_resource_group.cve_vm.name
}

resource "azurerm_subnet" "example" {
  name                 = "internal"
  resource_group_name  = azurerm_resource_group.cve_vm.location
  virtual_network_name = azurerm_virtual_network.example.name
  address_prefixes     = ["10.0.2.0/24"]
}


resource "azurerm_network_interface" "cve_vm" {
  for_each = var.virtual_machine

  name                = each.value.name
  location            = azurerm_resource_group.cve_vm.location
  resource_group_name = azurerm_resource_group.cve_vm.name

  ip_configuration {
    name                          = "internal"
    subnet_id                     = azurerm_subnet.example.id
    private_ip_address_allocation = "Dynamic"
  }
}

# Create VM
resource "azurerm_linux_virtual_machine" "cve_vm" {
  for_each = var.virtual_machine

  name                = each.value.name
  resource_group_name = azurerm_resource_group.cve_vm.name
  location            = azurerm_resource_group.cve_vm.location
  size                = "Standard_F2"
  admin_username      = "adminuser"
  network_interface_ids = [
    azurerm_network_interface.cve_vm[each.key].id
  ]

  computer_name                   = "lsadmin"
  admin_password                  = random_password.cve_password.result
  disable_password_authentication = false

  os_disk {
    caching              = "ReadWrite"
    storage_account_type = "Standard_LRS"
  }

  source_image_id = each.value.image_source
}