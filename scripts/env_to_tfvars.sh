#!/bin/bash

# .env ファイルから Terraform 用の .tfvars ファイルを生成するスクリプト
# 使用方法: bash scripts/env_to_tfvars.sh

set -e

ENV_FILE=".env"
TFVARS_FILE="terraform/secret.tfvars"
PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

# .env ファイルの確認
if [ ! -f "$PROJECT_ROOT/$ENV_FILE" ]; then
    echo "❌ エラー: $ENV_FILE ファイルが見つかりません"
    exit 1
fi

echo "📖 $ENV_FILE から値を読み込み中..."

# .env ファイルから値を読み込む
export $(cat "$PROJECT_ROOT/$ENV_FILE" | grep -v '^#' | xargs)

# 空でない値を確認
if [ -z "$ENDPOINT" ] || [ -z "$MODEL_NAME" ] || [ -z "$SUBSCRIPTION_KEY" ]; then
    echo "❌ エラー: 必要な環境変数が .env に見つかりません"
    echo "   必須: ENDPOINT, MODEL_NAME, SUBSCRIPTION_KEY, API_VERSION"
    exit 1
fi

# secret.tfvars を生成
cat > "$PROJECT_ROOT/$TFVARS_FILE" << EOF
# このファイルは scripts/env_to_tfvars.sh で自動生成されました
# 手動編集は避けてください

openai_endpoint = "$ENDPOINT"
openai_model = "$MODEL_NAME"
openai_api_key = "$SUBSCRIPTION_KEY"
api_version = "${API_VERSION:-2024-02-15-preview}"
EOF

echo "✅ 成功: $TFVARS_FILE が生成されました"
echo ""
echo "📋 生成された設定:"
echo "  - Endpoint: $ENDPOINT"
echo "  - Model: $MODEL_NAME"
echo "  - API Version: ${API_VERSION:-2024-02-15-preview}"
echo ""
echo "🚀 次のコマンドでデプロイを実行してください:"
echo "  cd terraform"
echo "  terraform plan -var-file=\"secret.tfvars\""
echo "  terraform apply -var-file=\"secret.tfvars\""
