# Azure App Service 設定ガイド

## スタートアップコマンドの設定

Azure Portal で、App Service の **構成** → **一般設定** から以下を設定してください：

### スタートアップコマンド

以下のいずれかを使用します：

#### オプション1: Gunicorn を使用（推奨）
```
gunicorn --bind 0.0.0.0:8000 --workers 4 --timeout 120 wsgi:app
```

#### オプション2: シェルスクリプトを使用
```
bash /home/site/wwwroot/startup.sh
```

#### オプション3: Python直接実行
```
python wsgi.py
```

## トラブルシューティング

### ログの確認方法

1. Azure Portal → App Service → **ログストリーム**
2. または Azure CLI:
```bash
az webapp log tail --resource-group news-summarizer-rg --name news-summarizer-app
```

### よくあるエラー

#### エラー: `ModuleNotFoundError: No module named 'flask'`
→ `requirements.txt` が正しくインストールされていない
→ **スタートアップコマンドの実行順序を確認**

#### エラー: `Port is already in use`
→ Azure が自動でポート `8000` を選択しているため問題なし

#### エラー: `Application did not respond`
→ App Service ログを確認し、アプリケーション起動エラーを確認

## 環境変数の確認

Azure Portal → **構成** → **アプリケーション設定** で以下が設定されていることを確認：

- `ENDPOINT`: Azure OpenAI エンドポイント
- `SUBSCRIPTION_KEY`: Azure OpenAI APIキー
- `MODEL_NAME`: デプロイ名（例: `gpt-4`）
- `API_VERSION`: APIバージョン（例: `2024-02-15-preview`）

