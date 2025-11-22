provider "azurerm" {
  features {}

  subscription_id = var.subscription_id
}

# Resource Group
resource "azurerm_resource_group" "rg" {
  name     = var.rg_name
  location = var.rg_location
}

# Storage Account（ログとコンテナイメージの保存）
resource "azurerm_storage_account" "storage" {
  name                     = var.storage_account_name
  resource_group_name      = azurerm_resource_group.rg.name
  location                 = azurerm_resource_group.rg.location
  account_tier             = "Standard"
  account_replication_type = "LRS"

  tags = {
    environment = "production"
  }
}

# Azure Container Registry - Basic プラン（低価格）
resource "azurerm_container_registry" "acr" {
  name                = var.container_registry_name
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  sku                 = "Basic"
  admin_enabled       = true

  tags = {
    environment = "production"
  }
}

# Key Vault - Standard（低価格）
resource "azurerm_key_vault" "kv" {
  name                        = var.key_vault_name
  location                    = azurerm_resource_group.rg.location
  resource_group_name         = azurerm_resource_group.rg.name
  enabled_for_disk_encryption = false
  tenant_id                   = data.azurerm_client_config.current.tenant_id
  sku_name                    = "standard"

  access_policy {
    tenant_id = data.azurerm_client_config.current.tenant_id
    object_id = data.azurerm_client_config.current.object_id

    key_permissions = [
      "Get",
    ]

    secret_permissions = [
      "Get",
      "List",
      "Set",
      "Delete",
    ]

    storage_permissions = [
      "Get",
    ]
  }

  tags = {
    environment = "production"
  }
}

# Key Vault Secrets - ローカル変数を使用
resource "azurerm_key_vault_secret" "openai_api_key" {
  name         = "openai-api-key"
  value        = local.subscription_key
  key_vault_id = azurerm_key_vault.kv.id
}

resource "azurerm_key_vault_secret" "openai_endpoint" {
  name         = "openai-endpoint"
  value        = local.openai_endpoint
  key_vault_id = azurerm_key_vault.kv.id
}

resource "azurerm_key_vault_secret" "openai_model" {
  name         = "openai-model"
  value        = local.openai_model
  key_vault_id = azurerm_key_vault.kv.id
}

# App Service Plan - 低価格プラン（Free/Shared）
resource "azurerm_service_plan" "asp" {
  name                = var.app_service_plan_name
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  os_type             = "Linux"
  sku_name            = var.app_service_sku # "F1"（Free）または "D1"（Shared）

  tags = {
    environment = "production"
  }
}

# App Service - Python Flask App
resource "azurerm_linux_web_app" "app" {
  name                = var.app_name
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  service_plan_id     = azurerm_service_plan.asp.id

  site_config {
    always_on         = false # 低価格プランでは不要
    minimum_tls_version = "1.2"

    application_stack {
      python_version = "3.11"
    }
  }

  app_settings = {
    "WEBSITES_ENABLE_APP_SERVICE_STORAGE" = "false"
    "AZURE_OPENAI_API_KEY"                = "@Microsoft.KeyVault(SecretUri=${azurerm_key_vault_secret.openai_api_key.id})"
    "AZURE_OPENAI_ENDPOINT"               = "@Microsoft.KeyVault(SecretUri=${azurerm_key_vault_secret.openai_endpoint.id})"
    "AZURE_OPENAI_DEPLOYMENT_NAME"        = "@Microsoft.KeyVault(SecretUri=${azurerm_key_vault_secret.openai_model.id})"
    "API_VERSION"                         = local.api_version
    "DEVELOPMENT"                         = "false"
  }

  identity {
    type = "SystemAssigned"
  }

  tags = {
    environment = "production"
  }
}

# App Service - Key Vault アクセス権限
resource "azurerm_key_vault_access_policy" "app_access" {
  key_vault_id       = azurerm_key_vault.kv.id
  tenant_id          = data.azurerm_client_config.current.tenant_id
  object_id          = azurerm_linux_web_app.app.identity[0].principal_id

  secret_permissions = [
    "Get",
    "List",
  ]
}

# Data source: Current Azure context
data "azurerm_client_config" "current" {}
