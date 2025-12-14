"""
Custom exception handlers for Django REST Framework.

Provides consistent error response format across the API.
"""
import structlog
from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework.views import exception_handler

logger = structlog.get_logger(__name__)


class ServiceUnavailableError(APIException):
    """Exception for external service unavailability."""

    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    default_detail = 'Service temporarily unavailable. Please try again later.'
    default_code = 'service_unavailable'


class ExternalAPIError(APIException):
    """Exception for external API errors."""

    status_code = status.HTTP_502_BAD_GATEWAY
    default_detail = 'External API error occurred.'
    default_code = 'external_api_error'


class RateLimitExceededError(APIException):
    """Exception for rate limit exceeded."""

    status_code = status.HTTP_429_TOO_MANY_REQUESTS
    default_detail = 'Rate limit exceeded. Please try again later.'
    default_code = 'rate_limit_exceeded'


def custom_exception_handler(exc, context):
    """
    Custom exception handler that provides consistent error responses.

    Returns error responses in the format:
    {
        "error": {
            "code": "error_code",
            "message": "Human readable message",
            "details": {...}  # Optional additional details
        }
    }
    """
    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)

    if response is not None:
        # Get view information for logging
        view = context.get('view', None)
        view_name = view.__class__.__name__ if view else 'Unknown'

        # Log the exception
        logger.warning(
            'api_exception',
            exception_type=exc.__class__.__name__,
            view=view_name,
            status_code=response.status_code,
            detail=str(exc.detail) if hasattr(exc, 'detail') else str(exc),
        )

        # Format the response
        error_code = getattr(exc, 'default_code', 'error')
        if hasattr(exc, 'get_codes'):
            codes = exc.get_codes()
            if isinstance(codes, str):
                error_code = codes
            elif isinstance(codes, dict) and codes:
                # Get first error code from dict
                first_key = next(iter(codes))
                first_value = codes[first_key]
                if isinstance(first_value, list) and first_value:
                    error_code = first_value[0]
                else:
                    error_code = first_value

        # Build error response
        error_response = {
            'error': {
                'code': error_code,
                'message': _get_error_message(exc),
            }
        }

        # Add field-specific errors for validation errors
        if hasattr(exc, 'detail') and isinstance(exc.detail, dict):
            error_response['error']['details'] = exc.detail

        response.data = error_response

    return response


def _get_error_message(exc):
    """Extract a human-readable message from an exception."""
    if hasattr(exc, 'detail'):
        detail = exc.detail
        if isinstance(detail, str):
            return detail
        elif isinstance(detail, list):
            return detail[0] if detail else str(exc)
        elif isinstance(detail, dict):
            # Get first error message from dict
            for key, value in detail.items():
                if isinstance(value, list) and value:
                    return f"{key}: {value[0]}"
                elif isinstance(value, str):
                    return f"{key}: {value}"
            return str(exc)
    return str(exc)
