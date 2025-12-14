"""
URL configuration for core app.

Includes health check endpoints for system monitoring.
"""
from django.urls import path

from .views import HealthCheckView, ReadinessCheckView

urlpatterns = [
    path('health/', HealthCheckView.as_view(), name='health-check'),
    path('health/ready/', ReadinessCheckView.as_view(), name='readiness-check'),
]
