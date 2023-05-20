terraform {
required_providers {
    azurerm = {
    source  = "hashicorp/azurerm"
    version = "3.55.0"
    }
}
}


variable "subscription_id" {
type =  string
description = "Please enter the suscription name"
}

variable "client_id" {
type = string 
description = "Please enter client_id"
}

variable "client_secret" {
type = string 
description = "Please enter client_secret"
}

variable "tenant_id" {
type = string 
description = "Please enter tenant_id"
}


provider "azurerm" {
subscription_id = var.subscription_id
client_id       = var.client_id
client_secret   = var.client_secret
tenant_id       = var.tenant_id
features {}
}


# Azure Resource Group
resource "azurerm_resource_group" "fligtsdb" {
name     = "fligtsdb"
location = "North Europe"
}


# Azure Storage Account
resource "azurerm_storage_account" "airlinesstore" {
name                     = "airlinesstore"
resource_group_name      = "fligtsdb"
location                 = "North Europe"
account_tier             = "Standard"
account_replication_type = "LRS"
}


# Azure in container

resource "azurerm_storage_container" "input" {
name = "input"
storage_account_name = "airlinesstore"
container_access_type = "private"
}

# Azure container

resource "azurerm_storage_container" "output" {
name = "output"
storage_account_name = "airlinesstore"
container_access_type = "private"
}

# Azure Databricks Workspace
resource "azurerm_databricks_workspace" "airlinestore" {
name                        = "airlinesstore"
resource_group_name         = "fligtsdb"
location                    = "North Europe"
sku                         = "standard"
managed_resource_group_name = "managedRG"
}

# Azure Key Vault
resource "azurerm_key_vault" "airlinesvault" {
name                        = "airlinesvault"
location                    = "North Europe"
resource_group_name         = "fligtsdb"
tenant_id                   = "486efef4-96af-4776-aaf2-fea23d7f1820"
sku_name                    = "standard"
purge_protection_enabled    = false
soft_delete_retention_days  = 7
}