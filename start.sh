#!/bin/bash
set -e

echo "Starting deployment script..."

# Apply database migrations
echo "Applying migrations..."
python manage.py migrate --noinput

# Start Celery Worker in background
echo "Starting Celery Worker..."
celery -A config worker -l info --detach

# Start Celery Beat in background
echo "Starting Celery Beat..."
celery -A config beat -l info --detach

# Start Gunicorn (Foreground process to keep container alive)
echo "Starting Gunicorn..."
gunicorn config.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers 2 --threads 4
