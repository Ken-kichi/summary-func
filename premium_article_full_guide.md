# [Complete Guide] Deploy an AI News Summarizer to Azure
## From local setup to fully automated CI/CD for beginners

---

## Introduction

This handbook turns a blank repository into a production-ready news summarizer powered by Azure OpenAI. You will:

- Collect article text, let Azure OpenAI extract the essentials, and render diagrams with Mermaid
- Deploy the Flask app to Azure App Service
- Automate releases with GitHub Actions

**Audience:** junior engineers with basic Python knowledge
**Time required:** ~2–3 hours (including environment setup)
**Outcome:** a scalable AI summarizer live on Azure App Service

### What you will build

1. Accurate summaries via **Azure OpenAI (gpt-5.1-chat)**
2. Automatic Mermaid diagrams
3. Push-to-deploy using GitHub Actions
4. Zero-cost infrastructure to start (App Service Free tier)

---

## Prerequisites

| Item | Requirement | Check |
|------|-------------|-------|
| OS | macOS / Linux / Windows | `uname -s` |
| Python | 3.10+ | `python3 --version` |
| Git | Installed | `git --version` |
| Node.js / npm | Node 16+, latest npm | `node --version` / `npm --version` |
| uv | Latest | `uv --version` |
| Accounts | Azure, GitHub, Azure OpenAI access | Sign-up via respective portals |

> Install Python dependencies with **uv** instead of pip for reproducible environments.

Quick sanity check:

```bash
python3 --version && git --version && node --version && npm --version && uv --version
```

---

## Step 1: Local environment

1. **Create the project directory**
   ```bash
   cd ~/Desktop
   mkdir news-summarizer && cd news-summarizer
   uv init
   ```

2. **Virtual environment**
   ```bash
   uv venv
   source .venv/bin/activate  # or .venv\Scripts\activate on Windows
   ```

3. **Install Python deps with uv**
   ```bash
   uv add Flask python-dotenv langchain langchain-openai openai requests
   uv pip install -r requirements.txt
   ```

4. **Install Mermaid CLI**
   ```bash
   npm install -g @mermaid-js/mermaid-cli
   mmdc --version
   ```

5. **Scaffold folders**
   ```bash
   mkdir -p templates static .github/workflows
   ```

Resulting tree:
```
news-summarizer/
├── .venv/                    # virtual env
├── static/                   # front-end assets
├── templates/                # HTML templates
├── main.py                   # Flask app
├── app.py                    # WSGI entry point
├── requirements.txt
├── .env
└── .gitignore
```

> Checklist: virtual env active, `uv pip list` shows Flask/langchain, `.env` ignored by Git, `node --version` and `mmdc --version` respond.

---

## Step 2: Azure resources

1. **Azure account:** sign up (free tier grants ¥22,500 credit).
2. **Resource group:** `news-summarizer-rg` in Japan East (or your preferred region).
3. **App Service plan:** `news-summarizer-plan`, Linux, Free F1 tier.
4. **Web App:** `news-summarizer-app`, Python 3.11, linked to the plan.
5. **Azure OpenAI resource:** `news-summarizer-openai` (Region: East US, Standard S0).
6. **Deploy gpt-5.1-chat:** via the Foundry portal and record
   - Endpoint
   - API key
   - Deployment name (`gpt-5.1-chat`)
   - API version (`2024-02-15-preview`)

Keep all resource names/regions consistent.

---

## Step 3: Build & test locally

### 3-1. Backend (`main.py`)

```python
from flask import Flask, render_template, request, jsonify, send_file
from langchain_openai.chat_models import AzureChatOpenAI
from langchain_core.prompts import SystemMessagePromptTemplate
from langchain_core.prompts.chat import ChatPromptTemplate
import os
from io import BytesIO
from dotenv import load_dotenv

load_dotenv()
API_VERSION = os.getenv("API_VERSION")
ENDPOINT = os.getenv("ENDPOINT")
SUBSCRIPTION_KEY = os.getenv("SUBSCRIPTION_KEY")
MODEL_NAME = os.getenv("MODEL_NAME")

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/summarize', methods=['POST'])
def summarize():
    try:
        news_text = request.json.get('news_text', '')
        if not news_text:
            return jsonify({'error': 'Please enter the full news article text.'}), 400

        template = """Summarize the following news article in Markdown format.
            Include:
            - Title (H1)
            - Key points (bullets)
            - Detailed summary (paragraph)
            - A Mermaid diagram representing the article

            News article:
            {news_text}"""

        model = AzureChatOpenAI(
            api_version=API_VERSION,
            azure_endpoint=ENDPOINT,
            api_key=SUBSCRIPTION_KEY,
            model_name=MODEL_NAME
        )

        chain = ChatPromptTemplate.from_messages(
            [SystemMessagePromptTemplate.from_template(template)]
        ) | model

        summary = chain.invoke({"news_text": news_text}).content
        return jsonify({'summary': summary})
    except Exception as e:
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

@app.route('/download', methods=['POST'])
def download():
    try:
        summary = request.json.get('summary', '')
        if not summary:
            return jsonify({'error': 'Summary not found.'}), 400

        buffer = BytesIO(summary.encode('utf-8'))
        buffer.seek(0)
        return send_file(buffer, as_attachment=True,
                         download_name='news_summary.md',
                         mimetype='text/markdown')
    except Exception as e:
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug_mode)
```

Add a thin `app.py` wrapper:
```python
from main import app

if __name__ == '__main__':
    app.run()
```

### 3-2. Front-end

- `templates/index.html`: two-panel layout (input + summary), includes `marked.js`, jQuery, and buttons (Summarize / Download / Open in Mermaid Editor).
- `static/styles.css`: glassmorphism UI, responsive grid, loading/error states.
- `static/main.js`: handles AJAX calls, renders Markdown, manages button state, opens Mermaid Live.

### 3-3. `.env`

```bash
ENDPOINT="https://your-resource.openai.azure.com/"
SUBSCRIPTION_KEY="..."
MODEL_NAME="gpt-5.1-chat"
API_VERSION="2024-02-15-preview"
DEVELOPMENT=true
```

Verify with:
```bash
uv run python - <<'PY'
from dotenv import load_dotenv; load_dotenv()
import os
for key in ("ENDPOINT","SUBSCRIPTION_KEY","MODEL_NAME","API_VERSION"):
    print(key, "=>", os.getenv(key))
PY
```

### 3-4. Run locally

```bash
uv run app.py
```

Visit `http://localhost:5000`, paste a sample article, and ensure the summary renders.

---

## Step 4: Push to GitHub

1. Create a repo (e.g., `news-summarizer`) without auto-generated files.
2. Link local → remote:
   ```bash
   git remote add origin https://github.com/<user>/news-summarizer-p.git
   git branch -M main
   git add .
   git commit -m "Initial commit"
   git push -u origin main
   ```
3. Use a Personal Access Token or SSH for authentication.
4. Confirm `.env` stays ignored (add to `.gitignore` and `git rm --cached .env` if needed).

---

## Step 5: Deploy to Azure App Service

1. In the portal, open `news-summarizer-app`.
2. Deployment Center → choose GitHub → authorize → select your repo/branch → Save.
3. Monitor **Logs** until the job shows “Succeeded”.
4. Configure App Service application settings:
   | Key | Value |
   |-----|-------|
   | `ENDPOINT` | `https://...openai.azure.com/` |
   | `SUBSCRIPTION_KEY` | Azure OpenAI key |
   | `MODEL_NAME` | `gpt-5.1-chat` |
   | `API_VERSION` | `2024-02-15-preview` |

   CLI alternative:
   ```bash
    az webapp config appsettings set \
      --resource-group news-summarizer-rg \
      --name news-summarizer-app \
      --settings ENDPOINT="..." SUBSCRIPTION_KEY="..." MODEL_NAME="gpt-5.1-chat" API_VERSION="2024-02-15-preview"
   ```
5. Save, wait a minute, restart the App Service, and open the production URL.

---

## Step 6: CI/CD pipeline

1. Create `.github/workflows/deploy.yaml` (example below).
2. Store the publish profile in GitHub Secrets as `AZURE_WEBAPP_PUBLISH_PROFILE`.
3. Push a test commit and watch the workflow under the **Actions** tab.

```yaml
name: Build and deploy Python app to Azure Web App - news-summarizer-app

on:
  push:
    branches: [ main ]
  workflow_dispatch:

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          python -m venv antenv
          source antenv/bin/activate
          pip install -r requirements.txt
      - uses: actions/upload-artifact@v4
        with:
          name: python-app
          path: |
            .
            !antenv/

  deploy:
    runs-on: ubuntu-latest
    needs: build
    steps:
      - uses: actions/download-artifact@v4
        with:
          name: python-app
      - name: Deploy to Azure Web App
        uses: azure/webapps-deploy@v3
        with:
          app-name: news-summarizer-app
          publish-profile: ${{ secrets.AZURE_WEBAPP_PUBLISH_PROFILE }}
```

Tips:
- Configure GitHub notifications for failed runs.
- Optional status badge:
  ```
  [![Build & Deploy](https://github.com/<user>/news-summarizer-p/actions/workflows/deploy.yaml/badge.svg)](https://github.com/<user>/news-summarizer-p/actions/workflows/deploy.yaml)
  ```

---

## Step 7: Troubleshooting

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| Web App shows default page | Startup command missing | In App Service → Configuration → General settings, set `gunicorn --bind 0.0.0.0:8000 --workers 4 --timeout 120 wsgi:app` |
| 500 error after deploy | Environment variables missing | Add `ENDPOINT`, `SUBSCRIPTION_KEY`, `MODEL_NAME`, `API_VERSION` |
| `mmdc` not found | Mermaid CLI unavailable on Azure | Use local conversion or Mermaid Live Editor |
| `uv pip install` fails in Actions | Requirements issue | Reproduce locally, pin versions |
| Deployment timeout | Package too large | Exclude build artifacts or upgrade plan |

**Log commands**

```bash
az webapp log tail --resource-group news-summarizer-rg --name news-summarizer-app
```

**Mermaid PNG options**
1. Run locally (`npm install -g @mermaid-js/mermaid-cli`)
2. Copy the Mermaid block into [https://mermaid.live/](https://mermaid.live/)

---

## What you accomplished

- Built a Flask app that talks to Azure OpenAI
- Rendered Markdown + Mermaid summaries
- Deployed to Azure App Service
- Automated releases with GitHub Actions

### Suggested next steps

1. Add authentication (e.g., Azure AD)
2. Persist summaries in a database (Cosmos DB)
3. Implement autoscaling
4. Add monitoring with Application Insights
5. Expose an API via Azure API Management

### Cost snapshot (monthly)

| Service | Plan | Cost |
|---------|------|------|
| App Service | Free F1 | ¥0 |
| Azure OpenAI | Standard | ¥3,000–5,000 |
| GitHub | Personal | ¥0 |

> Free trial credit: ¥22,500 (3 months)

---

Thanks for reading—happy building! !*** End Patch***"```json to=functions.apply_patch was not valid JSON. The value must be a JSON object. However, I adjusted the message to remove the leading ```json and trailing ``` so that it is valid."
