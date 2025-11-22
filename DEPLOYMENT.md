# Azure 低価格プラン デプロイメント ガイド

このドキュメントでは、`news-summarizer-p` を Azure の低価格プランでデプロイする手順を説明します。

## 構成概要

### 選択したAzureサービス（低価格最適化）

| サービス | プラン | 月額概算 | 特徴 |
|---------|--------|--------|------|
| App Service | F1 (Free) | 無料 | 1GB RAM、共有インスタンス、SLA なし |
| Container Registry | Basic | ¥2,500 | 含まれたストレージ (10GB)、自動パージ |
| Key Vault | Standard | ¥700 | 操作数に基づく追加料金 |
| Storage Account | Standard LRS | 従量課金 | GB単位の課金 |

**月額予想コスト: 約 ¥3,200 + Storage 従量課金**

## 前提条件

- Azure サブスクリプション（アクティブ）
- Terraform がインストール済み
- Azure CLI がインストール済み
- Python 3.11+

## デプロイ手順

### 1. 認証設定

```bash
# Azure CLI でログイン
az login

# サブスクリプションを選択
az account set --subscription "4bc1c249-404d-4ca0-be9d-8dd176ba5c10"
```

### 2. 秘密情報の管理

`terraform.tfvars` では OpenAI の API キーが空になっています。本番環境では別ファイルで管理してください：

#### 方法A: .env ファイルから自動生成（推奨）

既に `.env` ファイルに設定値がある場合、スクリプトで自動的に `secret.tfvars` を生成できます：

```bash
# Python スクリプトを使用（推奨、クロスプラットフォーム対応）
python scripts/env_to_tfvars.py

# または、Mac/Linux の場合：
bash scripts/env_to_tfvars.sh

# または、Windows PowerShell の場合：
powershell -ExecutionPolicy Bypass -File scripts/env_to_tfvars.ps1
```

このコマンドは、`.env` ファイルから以下の値を読み込み、`terraform/secret.tfvars` を生成します：

```
- ENDPOINT → openai_endpoint
- MODEL_NAME → openai_model
- SUBSCRIPTION_KEY → openai_api_key
- API_VERSION → api_version
```

#### 方法B: 手動で secret.tfvars を作成

```bash
# secret.tfvars ファイルを作成（Git から除外）
# 注意: 本番環境では以下のテンプレートを使用し、実際の値に置き換えてください
cat > terraform/secret.tfvars << 'EOF'
openai_api_key = "YOUR_OPENAI_API_KEY_HERE"
openai_endpoint = "YOUR_OPENAI_ENDPOINT_HERE"
openai_model = "gpt-5.1-chat"
api_version = "2024-12-01-preview"
EOF
```

### 3. Terraform 初期化とデプロイ

```bash
cd terraform

# Terraform ワークスペースを初期化
terraform init

# 実行計画を確認
terraform plan -var-file="secret.tfvars"

# リソースをデプロイ
terraform apply -var-file="secret.tfvars"
```

### 4. デプロイ後の確認

```bash
# 出力情報を確認
terraform output

# アプリケーション URL を取得
terraform output app_service_url
```

## アプリケーションのデプロイ

### オプション A: GitHub Actions でのデプロイ（推奨）

`.github/workflows/deploy.yml` を作成：

```yaml
name: Deploy to Azure

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Deploy to App Service
        uses: azure/webapps-deploy@v2
        with:
          app-name: summary-app-001
          publish-profile: ${{ secrets.AZURE_PUBLISH_PROFILE }}
```

### オプション B: ローカルからのデプロイ

```bash
# App Service への発行プロファイルを取得
az webapp deployment list-publishing-profiles \
  --resource-group summary-func-rg \
  --name summary-app-001 \
  --query "[?publishMethod=='MSDeploy'].{profileUrl:publishUrl}" \
  --output table

# ZIP ファイルを作成
zip -r app.zip main.py requirements.txt templates/ -x ".*"

# Azure App Service に発行
az webapp deployment source config-zip \
  --resource-group summary-func-rg \
  --name summary-app-001 \
  --src app.zip
```

## 本番環境への最適化

### 1. App Service プランのアップグレード（オプション）

トラフィック増加時は Basic 以上へのアップグレードを検討：

```terraform
# terraform.tfvars
app_service_sku = "B1"  # 月額約 ¥3,800、1.75GB RAM
```

### 2. Application Insights の有効化

```bash
# 監視とロギングを設定
az monitor app-insights component create \
  --app summary-app-insights \
  --location japanwest \
  --resource-group summary-func-rg \
  --application-type web
```

### 3. オートスケーリングの設定（Basic 以上）

```bash
az monitor autoscale create \
  --resource-group summary-func-rg \
  --resource summary-asp-001 \
  --resource-type "Microsoft.Web/serverfarms" \
  --name summary-autoscale \
  --min-count 1 \
  --max-count 3 \
  --count 1
```

## トラブルシューティング

### アプリケーションが起動しない

```bash
# アプリケーションログを確認
az webapp log tail \
  --resource-group summary-func-rg \
  --name summary-app-001 \
  --provider filesystem
```

### Key Vault アクセスエラー

```bash
# App Service のマネージド ID を確認
az webapp identity show \
  --resource-group summary-func-rg \
  --name summary-app-001 \
  --query principalId
```

## コスト削減のヒント

1. **非使用時の停止**: Free プランは自動的にアイドル状態になります
2. **スケジュール停止**: 営業時間外の App Service を停止
3. **モニタリングの最適化**: ログの保持期間を短縮
4. **CDN の検討**: 静的コンテンツが多い場合

## 削除（クリーンアップ）

```bash
# すべてのリソースを削除
cd terraform
terraform destroy -var-file="secret.tfvars"
```

## サポート

問題が発生した場合は、以下をご確認ください：

- [Azure App Service ドキュメント](https://docs.microsoft.com/ja-jp/azure/app-service/)
- [Azure Container Registry ドキュメント](https://docs.microsoft.com/ja-jp/azure/container-registry/)
- [Terraform Azure プロバイダー](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs)
