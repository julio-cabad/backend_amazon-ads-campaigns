#!/bin/bash
# Don't use 'set -e' so Celery failures don't kill the script

echo "Starting deployment script..."

# Apply database migrations
echo "Applying migrations..."
python manage.py migrate --noinput

# Start Celery Worker in background (optional - may fail if no Redis)
echo "Starting Celery Worker..."
celery -A config worker -l info &

# Start Celery Beat in background (optional - may fail if no Redis)
echo "Starting Celery Beat..."
celery -A config beat -l info &

# Start Gunicorn (Foreground process to keep container alive)
echo "Starting Gunicorn..."
exec gunicorn config.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers 2 --threads 4
