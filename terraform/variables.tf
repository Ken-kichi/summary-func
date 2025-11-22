variable "subscription_id" {
  type        = string
  description = "subscription_id"
}

variable "rg_location" {
  type        = string
  description = "resource location"
}

variable "rg_name" {
  type        = string
  description = "resource name"
}

variable "storage_account_name" {
  type        = string
  description = "Storage Account name"
}

variable "container_registry_name" {
  type        = string
  description = "Azure Container Registry name"
}

variable "key_vault_name" {
  type        = string
  description = "Key Vault name"
}

variable "app_service_plan_name" {
  type        = string
  description = "App Service Plan name"
}

variable "app_service_sku" {
  type        = string
  description = "App Service SKU（F1=Free, D1=Shared, B1=Basic）"
  default     = "F1"
}

variable "app_name" {
  type        = string
  description = "App Service name"
}

variable "openai_api_key" {
  type        = string
  description = "OpenAI API Key"
  sensitive   = true
}

variable "openai_endpoint" {
  type        = string
  description = "OpenAI Endpoint URL"
}

variable "openai_model" {
  type        = string
  description = "OpenAI Model name"
}

variable "api_version" {
  type        = string
  description = "OpenAI API version"
  default     = "2024-02-15-preview"
}
