terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "=3.0.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~>3.0"
    }
  }
}

# Configure the Microsoft Azure Provider
provider "azurerm" {
  features {}
  subscription_id = "44678328-75c5-4e48-92c0-b2ab31d5166c"
}

resource "random_id" "prefix" {
  keepers = {
    # Generate a new ID only when a new resource group is defined
    resource_group = var.resource_group_location
  }
  byte_length = 4
}


locals {
  name_prefix = "benchmark${random_id.prefix.hex}"
  data_folder = var.benchmark_type == "normal" ? "datasets" : "datagen/synthetic-${var.benchmark_complexity_word}"
}


resource "azurerm_resource_group" "rg" {
  location = var.resource_group_location
  name     = local.name_prefix
}

# Create virtual network
resource "azurerm_virtual_network" "benchmark_network" {
  name                = "${local.name_prefix}Vnet"
  address_space       = ["10.0.0.0/16"]
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
}

# Create subnet
resource "azurerm_subnet" "benchmark_subnet" {
  name                 = "${local.name_prefix}Subnet"
  resource_group_name  = azurerm_resource_group.rg.name
  virtual_network_name = azurerm_virtual_network.benchmark_network.name
  address_prefixes     = ["10.0.1.0/24"]
}

# Create public IPs
resource "azurerm_public_ip" "benchmark_public_ip" {
  name                = "${local.name_prefix}PublicIP"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  allocation_method   = "Dynamic"
}

# Create Network Security Group and rule
resource "azurerm_network_security_group" "benchmark_nsg" {
  name                = "${local.name_prefix}NetworkSecurityGroup"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name

  security_rule {
    name                       = "SSH"
    priority                   = 1001
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "22"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }
}

# Create network interface
resource "azurerm_network_interface" "benchmark_nic" {
  name                = "${local.name_prefix}NIC"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name

  ip_configuration {
    name                          = "my_nic_configuration"
    subnet_id                     = azurerm_subnet.benchmark_subnet.id
    private_ip_address_allocation = "Dynamic"
    public_ip_address_id          = azurerm_public_ip.benchmark_public_ip.id
  }
}

# Connect the security group to the network interface
resource "azurerm_network_interface_security_group_association" "example" {
  network_interface_id      = azurerm_network_interface.benchmark_nic.id
  network_security_group_id = azurerm_network_security_group.benchmark_nsg.id
}



# Create storage account for boot diagnostics
resource "azurerm_storage_account" "boot_diagnostics" {
  name                     = "${local.name_prefix}sa"
  location                 = azurerm_resource_group.rg.location
  resource_group_name      = azurerm_resource_group.rg.name
  account_tier             = "Standard"
  account_replication_type = "LRS"
}

# Create (and display) an SSH key
resource "tls_private_key" "example_ssh" {
  algorithm = "RSA"
  rsa_bits  = 4096
}

# Create virtual machine
resource "azurerm_linux_virtual_machine" "benchmark_vm" {
  name                  = "${local.name_prefix}VM"
  location              = azurerm_resource_group.rg.location
  resource_group_name   = azurerm_resource_group.rg.name
  network_interface_ids = [azurerm_network_interface.benchmark_nic.id]
  size                  = var.vm_size

  os_disk {
    name                 = "myOsDisk"
    caching              = "ReadWrite"
    storage_account_type = "Premium_LRS" # UltraSSD_LRS
    disk_size_gb         = 128
  }

  source_image_reference {
    publisher = "Canonical"
    offer     = "0001-com-ubuntu-server-jammy"
    sku       = "22_04-lts-gen2"
    version   = "latest"
  }

  computer_name                   = "myvm"
  admin_username                  = "azureuser"
  disable_password_authentication = true

  admin_ssh_key {
    username   = "azureuser"
    public_key = tls_private_key.example_ssh.public_key_openssh
  }

  boot_diagnostics {
    storage_account_uri = azurerm_storage_account.boot_diagnostics.primary_blob_endpoint
  }
}

data "azurerm_storage_account" "data_cache" {
  name                = var.storage_account_name
  resource_group_name = "Master_Thesis"
}

data "azurerm_storage_account_sas" "example" {
  connection_string = data.azurerm_storage_account.data_cache.primary_connection_string
  https_only        = true

  resource_types {
    service   = true
    container = true
    object    = true
  }

  services {
    blob  = true
    queue = true
    table = true
    file  = true
  }

  start  = timeadd(timestamp(), "-1h")
  expiry = timeadd(timestamp(), "12h")

  permissions {
    # https://github.com/hashicorp/terraform-provider-azurerm/issues/17558
    read    = true
    write   = true
    delete  = true
    list    = true
    add     = true
    create  = true
    update  = true
    process = true
    tag     = false
    filter  = false
  }
}

resource "azurerm_virtual_machine_extension" "execute_benchmark" {
  name                 = "execute_benchmark"
  virtual_machine_id   = azurerm_linux_virtual_machine.benchmark_vm.id
  publisher            = "Microsoft.Azure.Extensions"
  type                 = "CustomScript"
  type_handler_version = "2.0"

  settings = <<SETTINGS
    {
        "script": "${base64encode(templatefile("prepare.sh", {
  SAS_TOKEN        = data.azurerm_storage_account_sas.example.sas
  BENCHMARK_TYPE   = var.benchmark_type
  DATA_FOLDER      = local.data_folder
}))}"
    }
  SETTINGS
}

resource "local_file" "cert" {
  content         = tls_private_key.example_ssh.private_key_pem
  filename        = "private.key"
  file_permission = "600"
}

output "resource_group_name" {
  value = azurerm_resource_group.rg.name
}

output "public_ip_address" {
  value = azurerm_linux_virtual_machine.benchmark_vm.public_ip_address
}

output "tls_private_key" {
  value     = tls_private_key.example_ssh.private_key_pem
  sensitive = true
}

output "command" {
  value = "ssh -i private.key -o StrictHostKeyChecking=no azureuser@${azurerm_linux_virtual_machine.benchmark_vm.public_ip_address}"
}

output "host" {
  value = "azureuser@${azurerm_linux_virtual_machine.benchmark_vm.public_ip_address}"
}
