"""
Core views for system health monitoring.
"""
from django.db import connection
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema


class HealthCheckView(APIView):
    """
    Basic health check endpoint.

    Returns 200 OK if the service is running.
    """

    authentication_classes = []
    permission_classes = []
    throttle_classes = []

    @extend_schema(
        tags=['Health'],
        summary='Basic health check',
        description='Returns 200 OK if the service is running.',
        responses={200: {'type': 'object', 'properties': {'status': {'type': 'string'}}}},
    )
    def get(self, request):
        """Return basic health status."""
        return Response({'status': 'healthy'}, status=status.HTTP_200_OK)


class ReadinessCheckView(APIView):
    """
    Readiness check endpoint.

    Returns 200 OK if the service is ready to accept traffic.
    Checks database connectivity.
    """

    authentication_classes = []
    permission_classes = []
    throttle_classes = []

    @extend_schema(
        tags=['Health'],
        summary='Readiness check',
        description='Returns 200 OK if the service is ready to accept traffic.',
        responses={
            200: {
                'type': 'object',
                'properties': {
                    'status': {'type': 'string'},
                    'database': {'type': 'string'},
                },
            },
            503: {
                'type': 'object',
                'properties': {
                    'status': {'type': 'string'},
                    'error': {'type': 'string'},
                },
            },
        },
    )
    def get(self, request):
        """Check if service is ready to accept traffic."""
        try:
            # Check database connection
            with connection.cursor() as cursor:
                cursor.execute('SELECT 1')

            return Response(
                {
                    'status': 'ready',
                    'database': 'connected',
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {
                    'status': 'not ready',
                    'error': str(e),
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
