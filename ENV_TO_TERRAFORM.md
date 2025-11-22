# .env から Terraform への設定値統合ガイド

このドキュメントでは、`.env` ファイルの設定値を Terraform に自動的に反映させる方法を説明します。

## 概要

ローカル開発で使用している `.env` ファイルの設定値を、Azure デプロイメント用の Terraform 変数ファイル（`secret.tfvars`）に自動変換できます。

## 利用可能な方法

### 方法1: Python スクリプト（推奨、クロスプラットフォーム対応）

**利点:**
- Windows、Mac、Linux で動作
- 最も汎用的
- エラーハンドリングが充実

**使用方法:**

```bash
# スクリプトを実行
python scripts/env_to_tfvars.py

# または、カスタムパスを指定
python scripts/env_to_tfvars.py \
  --env-file .env \
  --output terraform/secret.tfvars \
  --project-root .
```

**前提条件:**
```bash
# python-dotenv パッケージが必要
pip install python-dotenv
```

### 方法2: Bash スクリプト（Mac/Linux）

**利点:**
- 追加インストール不要
- シンプルで高速

**使用方法:**

```bash
bash scripts/env_to_tfvars.sh
```

### 方法3: PowerShell スクリプト（Windows）

**利点:**
- Windows ネイティブ
- 特別な設定不要

**使用方法:**

```powershell
powershell -ExecutionPolicy Bypass -File scripts/env_to_tfvars.ps1
```

### 方法4: Terraform ローカル変数を直接使用

`terraform/env.tf` ファイルで、環境変数と Terraform 変数のマッピングを定義しています。

## マッピング対応表

| .env 変数 | Terraform 変数 | 説明 |
|----------|---------------|------|
| ENDPOINT | openai_endpoint | OpenAI エンドポイント URL |
| MODEL_NAME | openai_model | モデル名（デプロイ名） |
| SUBSCRIPTION_KEY | openai_api_key | API キー |
| API_VERSION | api_version | OpenAI API バージョン |

## 実行フロー

```
1. .env ファイルを確認
        ↓
2. スクリプトで secret.tfvars を生成
        ↓
3. Terraform で secret.tfvars を使用
        ↓
4. Key Vault にシークレットを保存
        ↓
5. App Service で環境変数を参照
```

## 詳細な使用例

### ステップ 1: .env ファイルを確認

```bash
cat .env
# 出力例:
# ENDPOINT=https://poti1-mi8uf9zs-eastus2.cognitiveservices.azure.com/
# MODEL_NAME=gpt-5.1-chat
# SUBSCRIPTION_KEY=7DgN2tQz...
# API_VERSION=2024-12-01-preview
```

### ステップ 2: secret.tfvars を生成

```bash
# Python スクリプトで生成
python scripts/env_to_tfvars.py

# 出力:
# 📖 .env から値を読み込み中...
# ✅ 成功: terraform/secret.tfvars が生成されました
#
# 📋 生成された設定:
#   - Endpoint: https://poti1-mi8uf9zs-eastus2.cognitiveservices.azure.com/
#   - Model: gpt-5.1-chat
#   - API Version: 2024-12-01-preview
```

### ステップ 3: 生成されたファイルを確認

```bash
cat terraform/secret.tfvars

# 出力例:
# # このファイルは scripts/env_to_tfvars.py で自動生成されました
# # 手動編集は避けてください
#
# openai_endpoint = "https://poti1-mi8uf9zs-eastus2.cognitiveservices.azure.com/"
# openai_model = "gpt-5.1-chat"
# openai_api_key = "7DgN2tQz..."
# api_version = "2024-12-01-preview"
```

### ステップ 4: Terraform でデプロイ

```bash
cd terraform

# 実行計画を確認
terraform plan -var-file="secret.tfvars"

# デプロイ実行
terraform apply -var-file="secret.tfvars"
```

## トラブルシューティング

### エラー: ".env ファイルが見つかりません"

```bash
# .env ファイルが存在するか確認
ls -la .env

# .env ファイルを作成（まだない場合）
cp .env.example .env
```

### エラー: "必要な環境変数が見つかりません"

`.env` ファイルに以下の変数が含まれていることを確認してください：

```bash
grep -E "ENDPOINT|MODEL_NAME|SUBSCRIPTION_KEY|API_VERSION" .env
```

### 生成された secret.tfvars が反映されない

Terraform キャッシュをクリアしてから再度実行：

```bash
cd terraform
rm -rf .terraform/ .terraform.lock.hcl
terraform init
terraform apply -var-file="secret.tfvars"
```

## セキュリティのベストプラクティス

1. **secret.tfvars を Git にコミットしない**
   ```bash
   # .gitignore で除外（既に設定済み）
   echo "terraform/secret.tfvars" >> .gitignore
   ```

2. **.env ファイルも Git にコミットしない**
   ```bash
   echo ".env" >> .gitignore
   ```

3. **CI/CD で使用する場合は環境変数で管理**
   ```bash
   # GitHub Actions などで秘密を設定
   OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
   ```

## 自動化（CI/CD 統合）

### GitHub Actions でのデプロイ自動化

`.github/workflows/deploy.yml` の例：

```yaml
name: Deploy to Azure with Terraform

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Generate secret.tfvars from .env
        run: |
          pip install python-dotenv
          python scripts/env_to_tfvars.py
        env:
          ENDPOINT: ${{ secrets.OPENAI_ENDPOINT }}
          MODEL_NAME: ${{ secrets.OPENAI_MODEL_NAME }}
          SUBSCRIPTION_KEY: ${{ secrets.OPENAI_SUBSCRIPTION_KEY }}
          API_VERSION: ${{ secrets.OPENAI_API_VERSION }}

      - name: Terraform Deploy
        run: |
          cd terraform
          terraform init
          terraform apply -var-file="secret.tfvars" -auto-approve
```

## FAQ

**Q: .env ファイルを更新したら、Terraform にも反映されますか？**

A: いいえ。`.env` を更新した場合は、スクリプトを再度実行して `secret.tfvars` を再生成してください。

**Q: secret.tfvars を手動で編集できますか？**

A: 可能ですが、推奨されません。`.env` を更新してスクリプトで再生成することを推奨します。

**Q: 複数の環境（本番、ステージング）に対応できますか？**

A: 可能です。`.env.prod`、`.env.staging` などを作成し、スクリプトで指定します：

```bash
python scripts/env_to_tfvars.py --env-file .env.prod --output terraform/secret.prod.tfvars
terraform apply -var-file="secret.prod.tfvars"
```

## サポート

問題が発生した場合は、以下をご確認ください：

- スクリプトのヘルプを表示: `python scripts/env_to_tfvars.py --help`
- .env ファイルの形式を確認: `KEY=VALUE` の形式を使用
- Terraform ログを確認: `terraform apply -var-file="secret.tfvars" -no-color`
