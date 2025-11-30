# Guide: Fixing "Web App Not Showing" on Azure

## 🔧 Summary of Implemented Fixes

To resolve the issue where the Azure App Service failed to render the application, the following files were added or updated.

### 1. **main.py** – Host/Port configuration

```python
# Before
if __name__ == '__main__':
    app.run(debug=True)

# After
if __name__ == '__main__':
    import sys
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug_mode)
```

**Why**
- `host='0.0.0.0'`: Listen on every interface Azure exposes
- `PORT`: Align with the dynamic port assigned by Azure
- `debug_mode`: Keep debug disabled in production

### 2. **wsgi.py** – New file

WSGI entry point for Gunicorn:

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

### 3. **app.py** – New file

Alternative entry point for App Service.

```python
from main import app

if __name__ == '__main__':
    app.run()
```

### 4. **requirements.txt** – Added Flask and Gunicorn

```
Flask==3.1.2
gunicorn==23.0.0
langchain==1.0.8
langchain-openai==1.0.3
```

### 5. **web.config** – New file (Windows/IIS settings)

Ensures static files are served correctly when hosted on Azure App Service for Windows.

### 6. **startup.sh** – New file (startup script)

```bash
#!/bin/bash
pip install --no-cache-dir -r requirements.txt
gunicorn --bind 0.0.0.0:8000 --workers 4 --timeout 120 wsgi:app
```

---

## 🚀 Configure the Azure Portal

### Step 1: Set the startup command

1. **Azure Portal** → **App Service** (`news-summarizer-app`)
2. Left menu → **Configuration**
3. Open the **General settings** tab
4. Enter the startup command:
   ```
   gunicorn --bind 0.0.0.0:8000 --workers 4 --timeout 120 wsgi:app
   ```
5. Click **Save**
6. Restart the App Service

### Step 2: Commit and push changes to GitHub

```bash
# Move into the project directory
cd /Users/nakashimakengo/Desktop/news-summarizer-p

# Activate the virtual environment
source .venv/bin/activate

# Commit the changes
git commit -m "Fix Azure App Service deployment - Add Gunicorn and WSGI support"

# Push to GitHub
git push origin main
```

### Step 3: Confirm the GitHub Actions deployment

1. GitHub repository → **Actions** tab
2. Confirm a new workflow run has started
3. Wait for the ✅ **build** and **deploy** jobs to finish

### Step 4: Access the application

1. Azure Portal → App Service → **Overview**
2. Click the **URL** to verify the app loads

✅ The application should now render correctly.

---

## 🔍 Troubleshooting

### If the app still does not show

#### 1. Inspect logs

```bash
az webapp log tail --resource-group news-summarizer-rg --name news-summarizer-app
```

#### 2. Confirm the startup command

```bash
az webapp config show --resource-group news-summarizer-rg --name news-summarizer-app | grep startup
```

#### 3. Validate required environment variables

```bash
az webapp config appsettings list --resource-group news-summarizer-rg --name news-summarizer-app
```

Ensure the output includes:
- `ENDPOINT`
- `SUBSCRIPTION_KEY`
- `MODEL_NAME`
- `API_VERSION`

#### 4. Restart the App Service

```bash
az webapp restart --resource-group news-summarizer-rg --name news-summarizer-app
```

---

## 📋 Deployment Checklist

Confirm these items once deployment completes:

- [ ] Startup command configured
- [ ] GitHub Actions workflow succeeded (✅ badge)
- [ ] All required environment variables exist
- [ ] `wsgi.py` committed to GitHub
- [ ] `requirements.txt` includes Flask and Gunicorn
- [ ] No errors in the App Service logs
- [ ] Web App URL renders the application

---

## ✅ Signs of Success

1. ✅ The Azure App Service URL loads the app
2. ✅ Clicking **Summarize** after entering news text returns a summary
3. ✅ **Download as Markdown** returns a file
4. ✅ Logs contain only `DEBUG` or `INFO` level entries

---

## 📞 Need more help?

- **Azure CLI Docs**: https://learn.microsoft.com/en-us/cli/azure/
- **Flask Docs**: https://flask.palletsprojects.com/
- **Gunicorn Docs**: https://docs.gunicorn.org/
