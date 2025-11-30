#!/bin/bash
set -e

# Create the log directory
mkdir -p /tmp/app_logs

# Install Python package dependencies
echo "Installing dependencies..."
pip install --no-cache-dir -r requirements.txt

# Start the Flask app (using Gunicorn)
echo "Starting Flask application with Gunicorn..."
gunicorn --bind 0.0.0.0:8000 --workers 4 --timeout 120 --access-logfile - --error-logfile - wsgi:app
