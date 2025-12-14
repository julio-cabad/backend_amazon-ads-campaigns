FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    gcc \
    postgresql-client \
    libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements/ requirements/
# Create a root requirements.txt for compatibility if needed, but we install directly
RUN pip install --no-cache-dir -r requirements/production.txt

# Copy project
COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput

# Create a non-root user and switch to it for security
RUN addgroup --system app && adduser --system --group app
USER app

# Run gunicorn
# Use specific port passed via env or default to 8000
CMD gunicorn config.wsgi:application --bind 0.0.0.0:${PORT:-8000}
