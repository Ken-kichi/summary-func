output "resource_group_id" {
  value       = azurerm_resource_group.rg.id
  description = "The ID of the created Resource Group"
}

output "app_service_url" {
  value       = azurerm_linux_web_app.app.default_hostname
  description = "The default hostname of the App Service"
}

output "app_service_id" {
  value       = azurerm_linux_web_app.app.id
  description = "The ID of the App Service"
}

output "container_registry_login_server" {
  value       = azurerm_container_registry.acr.login_server
  description = "The login server of the Container Registry"
}

output "container_registry_admin_username" {
  value       = azurerm_container_registry.acr.admin_username
  description = "The admin username of the Container Registry"
}

output "key_vault_id" {
  value       = azurerm_key_vault.kv.id
  description = "The ID of the Key Vault"
}

output "storage_account_name" {
  value       = azurerm_storage_account.storage.name
  description = "The name of the Storage Account"
}

output "deployment_notes" {
  value = "デプロイ完了！ アプリケーション URL: https://${azurerm_linux_web_app.app.default_hostname} 低価格プラン構成: App Service: Free プラン(F1) - 月額無料、Container Registry: Basic - 月額約 2,500円、Key Vault: Standard - 月額約 700円"
}
