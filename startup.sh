#!/bin/bash
set -e

# ログディレクトリの作成
mkdir -p /tmp/app_logs

# Pythonパッケージの依存関係をインストール
echo "Installing dependencies..."
pip install --no-cache-dir -r requirements.txt

# Flaskアプリを起動（Gunicornを使用）
echo "Starting Flask application with Gunicorn..."
gunicorn --bind 0.0.0.0:8000 --workers 4 --timeout 120 --access-logfile - --error-logfile - wsgi:app
