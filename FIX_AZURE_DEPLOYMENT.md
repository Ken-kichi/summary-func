# Web App が表示されない問題の解決ガイド

## 🔧 実装した修正内容

Azure App Service でアプリケーションが表示されない問題を解決するため、以下のファイルを追加・修正しました。

### 1. **main.py** - ホスト・ポート設定を修正

**変更内容**:
```python
# 修正前
if __name__ == '__main__':
    app.run(debug=True)

# 修正後
if __name__ == '__main__':
    import sys
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug_mode)
```

**理由**:
- `host='0.0.0.0'` : Azure App Service の全インターフェースをリッスン
- `PORT` 環境変数 : Azure が自動的に割り当てるポート番号に対応
- `debug_mode` : 本番環境ではデバッグモードを無効化

### 2. **wsgi.py** - 新規作成

WSGI アプリケーションサーバー（Gunicorn）用のエントリポイント

```python
import logging
import sys
from main import app

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logger = logging.getLogger(__name__)

if __name__ == '__main__':
    logger.info("Starting Flask application for Azure App Service")
    app.run(host='0.0.0.0', port=8000)
```

### 3. **app.py** - 新規作成

代替エントリポイント

```python
from main import app

if __name__ == '__main__':
    app.run()
```

### 4. **requirements.txt** - Flask と Gunicorn を追加

```
Flask==3.1.2
gunicorn==23.0.0
langchain==1.0.8
langchain-openai==1.0.3
```

### 5. **web.config** - 新規作成（Windows Server IIS 設定）

Azure App Service 上で静的ファイルを正しく提供するための IIS 設定

### 6. **startup.sh** - 新規作成（起動スクリプト）

```bash
#!/bin/bash
pip install --no-cache-dir -r requirements.txt
gunicorn --bind 0.0.0.0:8000 --workers 4 --timeout 120 wsgi:app
```

---

## 🚀 Azure Portal での設定手順

### Step 1: スタートアップコマンドを設定

1. **Azure Portal** → **App Service** （`news-summarizer-app`）を開く
2. 左メニュー → **構成** をクリック
3. **一般設定** タブをクリック
4. **スタートアップコマンド** に以下を入力：

```
gunicorn --bind 0.0.0.0:8000 --workers 4 --timeout 120 wsgi:app
```

5. **保存** をクリック
6. App Service を **再起動**

### Step 2: 変更をコミットして GitHub にプッシュ

```bash
# ディレクトリに移動
cd /Users/nakashimakengo/Desktop/news-summarizer-p

# 仮想環境をアクティベート
source .venv/bin/activate

# 変更をコミット
git commit -m "Fix Azure App Service deployment - Add Gunicorn and WSGI support"

# GitHub にプッシュ
git push origin main
```

### Step 3: GitHub Actions の自動デプロイを確認

1. GitHub リポジトリ → **Actions** タブをクリック
2. 新しいワークフロー実行を確認
3. ✅ **build** と **deploy** ジョブが成功するのを待つ

### Step 4: アプリケーションにアクセス

1. Azure Portal → App Service → **概要**
2. **URL** をクリックしてアプリにアクセス

✅ これでアプリが表示されるはずです！

---

## 🔍 トラブルシューティング

### アプリがまだ表示されない場合

#### 1. ログを確認

```bash
# リアルタイムログ表示
az webapp log tail --resource-group news-summarizer-rg --name news-summarizer-app
```

#### 2. スタートアップコマンドが正しく設定されているか確認

```bash
az webapp config show --resource-group news-summarizer-rg --name news-summarizer-app | grep startup
```

#### 3. 環境変数が全て設定されているか確認

```bash
az webapp config appsettings list --resource-group news-summarizer-rg --name news-summarizer-app
```

出力に以下が含まれているか確認:
- `ENDPOINT`
- `SUBSCRIPTION_KEY`
- `MODEL_NAME`
- `API_VERSION`

#### 4. App Service を再起動

```bash
az webapp restart --resource-group news-summarizer-rg --name news-summarizer-app
```

---

## 📋 チェックリスト

デプロイが完了したら、以下を確認してください：

- [ ] スタートアップコマンドが設定されている
- [ ] GitHub Actions が成功している（✅ マーク）
- [ ] 環境変数が全て設定されている
- [ ] `wsgi.py` ファイルが Githab にアップロードされている
- [ ] `requirements.txt` に Flask と Gunicorn が含まれている
- [ ] App Service ログにエラーがない
- [ ] Web App の URL にアクセスしてアプリが表示されている

---

## ✅ 成功の兆候

以下が確認できたら、完全にセットアップが完了しています：

1. ✅ Azure App Service の URL にアクセスするとアプリが表示される
2. ✅ ニュース本文を入力して「要約する」ボタンをクリックすると要約が生成される
3. ✅ 「Markdownをダウンロード」でファイルがダウンロードされる
4. ✅ ログに `DEBUG` または `INFO` レベルのログのみ表示される

---

## 📞 さらにサポートが必要な場合

- **Azure CLI ドキュメント**: https://learn.microsoft.com/en-us/cli/azure/
- **Flask ドキュメント**: https://flask.palletsprojects.com/
- **Gunicorn ドキュメント**: https://docs.gunicorn.org/
