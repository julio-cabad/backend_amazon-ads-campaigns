"""
Production settings for Amazon Ads Campaigns project.

These settings are used in production environments.
"""
from .base import *  # noqa: F401, F403

# Security settings
DEBUG = False

SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Allow all hosts to avoid 502/400 errors on Railway
ALLOWED_HOSTS = ['*']

# HTTPS settings (enable when using HTTPS)
# SECURE_SSL_REDIRECT = True
# SESSION_COOKIE_SECURE = True
# CSRF_COOKIE_SECURE = True

# Sentry for error tracking (optional)
import os
if os.environ.get('SENTRY_DSN'):
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration
    from sentry_sdk.integrations.celery import CeleryIntegration

    sentry_sdk.init(
        dsn=os.environ['SENTRY_DSN'],
        integrations=[DjangoIntegration(), CeleryIntegration()],
        traces_sample_rate=0.1,
        send_default_pii=False,
    )

# Production database should be configured via DATABASE_URL
# Example: DATABASE_URL=postgres://user:password@host:5432/dbname

# Production Celery should use Redis
# CELERY_BROKER_URL should be set in environment

# MEMORY OPTIMIZATION: Run tasks synchronously (Eager) to avoid OOM in small containers
# This eliminates the need for a separate Worker process
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True


# Ensure proper logging in production
LOGGING['handlers']['console']['level'] = 'DEBUG'
LOGGING['handlers']['console']['formatter'] = 'verbose'  # noqa: F405
LOGGING['loggers']['apps']['level'] = 'DEBUG'
LOGGING['loggers']['apps']['handlers'] = ['console']

# CORS is now properly configured in base.py (corsheaders in THIRD_PARTY_APPS)

# Redefine middleware to ensure CORS is at the top
MIDDLEWARE = [
    'apps.core.middleware.ForceCorsMiddleware', # NUCLEAR OPTION
    'corsheaders.middleware.CorsMiddleware',  # MUST BE FIRST
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_HEADERS = ['*']

# Allow all origins for CSRF too (Nuclear option for demo)
CSRF_TRUSTED_ORIGINS = ['https://frontendamazon-ads-campaigns-otm4gdxvq-julio-cabads-projects.vercel.app']
# CSRF_COOKIE_SECURE = True  # Commented out to avoid issues if HTTPS headers are stripping

# FINAL SAFETY CHECK: Deduplicate INSTALLED_APPS one last time
# This is "Nuclear Option" to fix "Application labels aren't unique" error
INSTALLED_APPS = [app for app in INSTALLED_APPS if app != 'corsheaders']
INSTALLED_APPS.append('corsheaders')
 


# DEBUG: Print final apps list
import sys
sys.stderr.write(f"DEBUG: INSTALLED_APPS={INSTALLED_APPS}\n")

