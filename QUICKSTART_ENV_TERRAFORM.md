# クイックスタート: .env から Terraform へ

## 🚀 30秒での実行手順

### ステップ 1: secret.tfvars を生成

```bash
# プロジェクトルートで実行
uv run scripts/env_to_tfvars.py
```

**出力例:**
```
✅ 成功: terraform/secret.tfvars が生成されました

📋 生成された設定:
  - Endpoint: https://poti1-mi8uf9zs-eastus2.cognitiveservices.azure.com/
  - Model: gpt-5.1-chat
  - API Version: 2024-12-01-preview
```

### ステップ 2: Azure にデプロイ

```bash
cd terraform
terraform init
terraform plan -var-file="secret.tfvars"
terraform apply -var-file="secret.tfvars"
```

## 📋 利用可能なスクリプト

| スクリプト | 対応OS | コマンド |
|----------|--------|---------|
| Python（推奨） | 全て | `uv run scripts/env_to_tfvars.py` または `python3 scripts/env_to_tfvars.py` |
| Bash | Mac/Linux | `bash scripts/env_to_tfvars.sh` |
| PowerShell | Windows | `powershell -ExecutionPolicy Bypass -File scripts/env_to_tfvars.ps1` |

## 🔄 フロー図

```
.env ファイル（ローカル開発用）
    │
    ├─→ env_to_tfvars.py（自動変換）
    │
    ├─→ secret.tfvars（Terraform用）
    │
    ├─→ Terraform → Azure
    │
    ├─→ Key Vault（秘密情報保存）
    │
    └─→ App Service（環境変数参照）
```

## ✨ 主な特徴

✅ **ワンコマンド生成** - スクリプトを実行するだけ
✅ **セキュア** - API キーは Key Vault で管理
✅ **自動同期** - .env 更新後は再実行するだけ
✅ **マルチプラットフォーム** - Windows/Mac/Linux 対応
✅ **エラーハンドリング** - 問題があれば明確なメッセージを表示

## 🛠️ トラブルシューティング

### 問題: "python-dotenv" が見つからない

```bash
# パッケージをインストール
pip install python-dotenv

# または uv の場合
uv pip install python-dotenv
```

### 問題: `.env` ファイルが見つからない

```bash
# .env ファイルが存在するか確認
ls -la .env

# 必要な変数を確認
cat .env | grep -E "ENDPOINT|MODEL_NAME|SUBSCRIPTION_KEY"
```

### 問題: secret.tfvars が生成されない

```bash
# ファイルの権限を確認
ls -la scripts/env_to_tfvars.py

# スクリプトを実行可能にする（必要に応じて）
chmod +x scripts/env_to_tfvars.py
```

## 📚 詳細なドキュメント

さらに詳しい情報は以下を参照してください：

- **統合ガイド**: `ENV_TO_TERRAFORM.md`
- **デプロイメント**: `DEPLOYMENT.md`
- **ソースコード**: `terraform/env.tf`、`scripts/env_to_tfvars.py`

## 🔐 セキュリティ注意事項

⚠️ **重要:**
- `secret.tfvars` は Git にコミット **しない**（`.gitignore` で除外）
- `.env` も Git にコミット **しない**（機密情報が含まれる）
- API キーは環境変数または CI/CD の秘密として管理
- Git にコミット前に必ず確認

## 💡 Tips

**複数環境での使用:**
```bash
# 本番環境用
python3 scripts/env_to_tfvars.py --env-file .env.prod --output terraform/secret.prod.tfvars

# ステージング環境用
python3 scripts/env_to_tfvars.py --env-file .env.staging --output terraform/secret.staging.tfvars
```

**CI/CD での自動化:**
GitHub Actions などで環境変数を設定すれば、パイプラインで自動的に `secret.tfvars` を生成できます。

---

質問がある場合は、`ENV_TO_TERRAFORM.md` の FAQ セクションを参照してください。
