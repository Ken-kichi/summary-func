# Azure App Service Configuration Guide

## Configure the Startup Command

In the Azure Portal, open your App Service and navigate to **Configuration** → **General settings**, then set one of the commands below.

### Startup Command

Use one of these options:

#### Option 1: Gunicorn (recommended)
```
gunicorn --bind 0.0.0.0:8000 --workers 4 --timeout 120 wsgi:app
```

#### Option 2: Shell script
```
bash /home/site/wwwroot/startup.sh
```

#### Option 3: Direct Python execution
```
python wsgi.py
```

## Troubleshooting

### How to check logs

1. Azure Portal → App Service → **Log stream**
2. Or via Azure CLI:
```bash
az webapp log tail --resource-group news-summarizer-rg --name news-summarizer-app
```

### Common errors

#### Error: `ModuleNotFoundError: No module named 'flask'`
→ `requirements.txt` was not installed correctly  
→ Verify the startup command installs dependencies before launching the app

#### Error: `Port is already in use`
→ Safe to ignore; Azure automatically binds the app to port `8000`

#### Error: `Application did not respond`
→ Inspect the App Service logs to locate application startup failures

## Verify environment variables

In Azure Portal → **Configuration** → **Application settings**, make sure the following keys exist:

- `ENDPOINT`: Azure OpenAI endpoint
- `SUBSCRIPTION_KEY`: Azure OpenAI API key
- `MODEL_NAME`: Deployment name (e.g., `gpt-4`)
- `API_VERSION`: API version (e.g., `2024-02-15-preview`)
