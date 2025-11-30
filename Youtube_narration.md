# 【YouTubeナレーション台本】実装しながら学ぶAI要約アプリ

> 画面は常にVS Codeとターミナル、必要に応じてAzure Portalやブラウザを切り替え。セクション冒頭で一言「ここでは〇〇画面を映しています」と添える。

---

## 1. オープニング＆ゴール提示（0:00〜0:40）

画面：顔出し or 画面＋マイク
セリフ：「みなさんこんにちは。今日はこのターミナルとVS Codeを使って、ニュース記事を貼るだけでAIが要約と図解まで仕上げてくれるFlaskアプリを、`uv init` からAzureデプロイまでノーカットで作っていきます。完成形はAzure App Serviceに乗せて、GitHub Actionsでpushしたら自動で更新されるところまでお見せします。」

補足テロップ：「前提スキル：ターミナルの基本操作とPythonの基礎。Azureアカウントだけ事前に作成しておけばOK／所要時間目安：約90分（動画を見ながら）」

セリフ：「もしPython歴が浅くても、コマンドはすべて画面に出しますし、つまずきどころも実況するので安心してください。」

---

## 2. 開発環境のセットアップ（0:40〜2:10）

画面：ターミナル全画面
セリフ：「まずはプロジェクトディレクトリを作って `uv init` からスタートです。コマンドは画面の通りなので、同時進行で打ち込んでもらってOKです。」

```bash
mkdir news-summarizer-p && cd news-summarizer-p
uv init
uv add Flask langchain langchain-openai openai python-dotenv requests gunicorn
```

セリフ：「依存関係が入ったら `uv venv` で仮想環境を作成、`source .venv/bin/activate` で有効化します。`uv pip list | head` を叩いて、FlaskやLangChainがちゃんと入っているか一緒に確認しておきましょう。」

ワンポイント字幕：「つまずき防止：`uv` コマンドが見つからない場合は公式ドキュメントのインストール手順（概要欄リンク）を先に実行」

---

## 3. Flaskアプリの実装（2:10〜5:00）

画面：VS Codeエディタ＋ターミナル下部
セリフ：「続いて `main.py` を作って、Azure OpenAIを叩くAPIとMermaid抽出のロジックを書いていきます。概要欄にGistを貼っておきますが、ここでは3つのポイントに絞って話します。」

1. `.env` から `API_VERSION`, `ENDPOINT`, `SUBSCRIPTION_KEY`, `MODEL_NAME` を読み込む
2. `/summarize` でLangChainの `ChatPromptTemplate` と `AzureChatOpenAI` を組み合わせる
3. `/extract-mermaid` で ``` ```mermaid ``` ブロックを正規表現で抜き出す

セリフ：「書き終えたら `python main.py` で起動。`http://localhost:5000` にアクセスしてテンプレに記事を貼り付け、実際に要約を取ってみます。画面にMermaidコードが返ってきたらローカル環境はクリアです。」

### （挿入）実装したAPIの役割を画面で解説（5:00〜5:40）

画面：`main.py` の該当関数にコメントを差し込みながら
- `/summarize` … ニュース本文を受け取り、LangChainがAzure OpenAIにリクエスト。戻り値はMarkdown要約＋Mermaidコード。
- `/download` … 生成された要約を `news_summary.md` として `send_file` で返す。
- `/extract-mermaid` … 正規表現で ```mermaid``` ブロックを抽出し、クライアントに複数図解を渡す。
- `/convert-mermaid-png` … ローカルで `mmdc` を叩いてPNG化し、Azureでは代替手段を通知。
「関数ごとに責務を分けておくと、Azure移行後のトラブルシュートがぐっと楽になりますよ、という説明を挟みます。」

エンゲージ誘導：「ここまででローカルの要約が動いた人は、コメント欄に ✅ を残してもらえると励みになります！」

---

## 4. フロントエンドとMermaidプレビュー（5:00〜6:20）

画面：VS Codeの `templates/index.html` と `static/main.js`
セリフ：「次はフロントです。HTMLフォームから本文をPOSTして、そのままレスポンスのMarkdownを描画します。MermaidのPNG変換はAzureだと難しいので、ローカルでは `mmdc`、クラウドではLive Editorに飛ばす二段構えにしています。」

```bash
npm install -g @mermaid-js/mermaid-cli
mmdc --version
```

セリフ：「`図をPNGで保存` ボタンを押すとローカルでは即ダウンロード、もしmmdcが無い環境ならエラーメッセージにLive Editorのリンクを出して、ブラウザで変換できるようにしています。」

### フロント側の機能紹介（6:20〜6:50）

画面：`static/main.js` をスクロール
- フォーム送信時に `/summarize` をFetch → 要約欄にMarkdownで描画
- `showMermaidDiagrams` 関数で `/extract-mermaid` のレスポンスを配列表示
- `downloadSummary` ボタンで `/download` を叩き、Blobを擬似リンクで保存
- PNG変換ボタンは `convert-mermaid-png` 成功時は即ダウンロード、失敗時はLive Editor誘導
「ここでUIがどのAPIに紐づくのかを視覚的に示し、ユーザーがどこで詰まるかを事前に説明します。」

ワンポイント字幕：「mmdcがインストールできない場合は後半で紹介するLive Editor（https://mermaid.live）を使用」

---

## 5. Azureリソースを実際に作成（6:20〜8:40）

画面：Azure Portal（リソースグループ→App Service→Azure OpenAI）
セリフ：「ここからAzure Portalに切り替えます。まずはリソースグループ `news-summarizer-rg` を作って、Free F1のApp Serviceプラン、続けてWebアプリ `news-summarizer-app` を作成。並行してAzure OpenAIをEast USで立ち上げ、`gpt-5.1-chat` をデプロイします。エンドポイントとキーはその場で `.env` とApp Serviceの構成画面に貼り付けておきます。」

セリフ：「設定画面ではスタートアップコマンドに `gunicorn --bind 0.0.0.0:8000 --workers 4 --timeout 120 wsgi:app` を入れて保存します。ここは入力ミスが多いので、ゆっくり声に出しながら進めます。」

ワンポイント字幕：「リージョンはApp ServiceとOpenAIで揃える（OpenAIは対応リージョン要確認）／リソース名は世界で一意」

### アーキテクチャ図で全体像を整理（8:40〜9:20）

画面：READMEのアーキテクチャMermaid図を表示
セリフ：「ここで一度、READMEに載せているアーキテクチャ図を映しながら全体像を整理します。左がユーザーのブラウザ、中央がAzure App Service上のFlask、右がAzure OpenAI。下にはGitHub Actionsが控えていて、`main` にpushされるたびにApp Serviceへ最新コードを届ける構造です。今日はこの4者を全部つないで、ローカルと本番の差がない状態まで持っていくのがゴールです。」

### データフローの流れを図解（9:20〜9:50）

画面：READMEのシーケンス図をズーム
セリフ：「次にデータフローの図を見てください。ユーザーが記事を貼り、ブラウザが `/summarize` にPOST。FlaskがAzure OpenAIに投げてMarkdown＋Mermaidを受け取り、再びブラウザに返します。その後、`図をPNGで保存` を押すと `/convert-mermaid-png` に飛んで、ローカルならPNGバイナリ、AzureならLive Editor案内を返す、という流れです。この2つの図を頭に入れておくと、どこで不具合が起きても原因を絞り込みやすくなります。」

---

## 6. GitHub ActionsでCI/CD構築（9:50〜11:40）

画面：VS Code `.github/workflows/deploy.yaml` → GitHubリポジトリ
セリフ：「続いてGitHub Actionsの設定です。`deploy.yaml` を作って、buildジョブで仮想環境を作成→依存インストール→アーティファクトをアップロード、deployジョブで `azure/login` と `azure/webapps-deploy` を順番に回します。ここはトリガー条件を右上に表示しながら、丁寧に書いていきます。」

セリフ：「Azureポータルで公開プロファイルをダウンロードして、GitHub Secretsに `AZURE_WEBAPP_PUBLISH_PROFILE` として貼り付けます。視聴者が止めながら追えるように、画面をズームしつつ一つずつ操作していきましょう。」

エンゲージ誘導：「ここまで進んだら『CI/CDまで来たよ』とコメント頂けると、他の視聴者も進捗の指標になります！」

---

## 7. 動作確認とデプロイ（11:40〜13:10）

画面：ターミナル → GitHub Actions画面 → デプロイ済みURL
セリフ：「`git add . && git commit -m 'initial release' && git push origin main` を打って、すぐにGitHub Actionsタブへ。ビルドが走って、続けてデプロイが緑になるまで実況しながら待ちます。」

セリフ：「完了したらApp ServiceのURLにアクセスし、さっきと同じ記事を貼り付けてみます。クラウド上でも要約とMermaidコードが返ってきたらOK。MermaidのPNGはローカル限定なので、『クラウドではLive Editorで変換してください』というテロップも再表示しておきます。」

ワンポイント字幕：「反映に数分かかる場合はApp Serviceのログ（portal→ログストリーム）で状況確認」

---

## 8. トラブル実演＆リカバリ（13:10〜14:30）

画面：Azureログストリーム / VS Code
セリフ：「最後にトラブルシューティングを実演します。例として `.env` のAPIキーを空にして再起動し、500エラーをわざと出してみます。ログには `InvalidAuthentication` が出ているので、キーを戻して再起動すると直る、という流れをワンカットで見せます。」

セリフ：「Mermaid CLIが入っていない状態も再現して、エラーメッセージに出てくるLive Editorリンクから変換する手順を一度やっておきます。」

エンゲージ誘導：「もし他にも再現してほしいトラブルがあれば、コメントでリクエストください！」

---

## 9. クロージング（14:30〜15:00）

画面：顔出し or アプリ画面
セリフ：「これで記事を貼るだけで要約とMermaid図解、さらにAzureデプロイまで回せる仕組みが完成しました。あとは好きなニュースで試したり、認証やDBを追加して自分専用に仕上げてみてください。動画が役に立ったら高評価とチャンネル登録、概要欄の完全ガイドもぜひチェックしてください。それではまた次回！」
