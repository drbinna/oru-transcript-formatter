#!/bin/bash
# Start script for Render deployment

echo "Starting Flask application..."
echo "Python version: $(python --version)"
echo "Port: $PORT"
echo "Current directory: $(pwd)"
echo "Files in directory:"
ls -la

# Try to start with gunicorn
exec gunicorn web_app:app --bind 0.0.0.0:$PORT --timeout 120 --workers 1 --log-level debug