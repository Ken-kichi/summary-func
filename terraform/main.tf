provider "azurerm" {
  features {}

  subscription_id = var.subscription_id
}

# Resource Group
resource "azurerm_resource_group" "rg" {
  name     = var.rg_name
  location = var.rg_location
}

# Storage Account (Function App に必須)
resource "azurerm_storage_account" "storage" {
  name                     = replace("${var.rg_name}storage", "-", "")
  resource_group_name      = azurerm_resource_group.rg.name
  location                 = azurerm_resource_group.rg.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
}

# Service Plan (Linux で Python ランタイム実行)
resource "azurerm_service_plan" "service_plan" {
  name                = "${var.rg_name}-func-plan"
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  os_type             = "Linux"
  sku_name            = "B1"
}

# Application Insights (監視・ログ)
resource "azurerm_application_insights" "appinsights" {
  name                = "${var.rg_name}-appinsights"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  application_type    = "web"
}

# Linux Function App (Python 3.11 対応)
resource "azurerm_linux_function_app" "function_app" {
  name                = "${var.rg_name}-func-app"
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location

  storage_account_name       = azurerm_storage_account.storage.name
  storage_account_access_key = azurerm_storage_account.storage.primary_access_key
  service_plan_id            = azurerm_service_plan.service_plan.id

  site_config {
    application_stack {
      python_version = "3.11"
    }
  }

  app_settings = {
    "APPINSIGHTS_INSTRUMENTATION_KEY"             = azurerm_application_insights.appinsights.instrumentation_key
    "ApplicationInsightsAgent_EXTENSION_VERSION"  = "~3"
    "XDT_MicrosoftApplicationInsights_Mode"       = "recommended"
    "AzureWebJobsStorage"                         = azurerm_storage_account.storage.primary_connection_string
  }

  depends_on = [
    azurerm_storage_account.storage,
    azurerm_service_plan.service_plan,
    azurerm_application_insights.appinsights
  ]
}

