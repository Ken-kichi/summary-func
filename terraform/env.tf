# .env ファイルから環境変数を読み込み、Terraform 変数に反映

# 注記：このファイルは .env ファイルの値を Terraform 変数にマッピングします
# .env ファイルが更新されると、以下のコマンドで変数を更新できます：
# source scripts/env_to_tfvars.sh

# environment 変数を取得（.env から読み込まれる）
variable "env_endpoint" {
  type        = string
  description = "OpenAI endpoint from .env"
  default     = ""
}

variable "env_model_name" {
  type        = string
  description = "Model name from .env"
  default     = ""
}

variable "env_subscription_key" {
  type        = string
  description = "Subscription key from .env"
  sensitive   = true
  default     = ""
}

variable "env_api_version" {
  type        = string
  description = "API version from .env"
  default     = ""
}

# .env から読み込まれた値を優先的に使用
locals {
  # .env から値を読み込む場合、env_* 変数が優先
  openai_endpoint = var.env_endpoint != "" ? var.env_endpoint : var.openai_endpoint
  openai_model    = var.env_model_name != "" ? var.env_model_name : var.openai_model
  subscription_key = var.env_subscription_key != "" ? var.env_subscription_key : var.openai_api_key
  api_version     = var.env_api_version != "" ? var.env_api_version : var.api_version
}

# ローカル変数をアプリケーション設定に使用
# main.tf の azurerm_linux_web_app 内で以下を使用:
# "AZURE_OPENAI_ENDPOINT"               = local.openai_endpoint
# "AZURE_OPENAI_DEPLOYMENT_NAME"        = local.openai_model
# "API_VERSION"                         = local.api_version
