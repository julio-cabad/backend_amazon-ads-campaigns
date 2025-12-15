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
RUN pip install --no-cache-dir -r requirements/production.txt

# Copy project (cache bust with build arg)
ARG CACHEBUST=1
COPY . .

# Collect static files (using production settings)
ENV DJANGO_SETTINGS_MODULE=config.settings.production
RUN python manage.py collectstatic --noinput

# Perform chmod on start script
RUN chmod +x /app/start.sh

# Create a non-root user
RUN addgroup --system app && adduser --system --group app
USER app

# Run the start script
CMD ["/app/start.sh"]
