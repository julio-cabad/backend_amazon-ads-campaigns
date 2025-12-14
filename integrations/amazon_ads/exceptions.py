"""
Amazon Ads API exceptions.

Custom exceptions for handling Amazon Ads API errors.
"""


class AmazonAdsError(Exception):
    """Base exception for Amazon Ads API errors."""

    def __init__(self, message: str, status_code: int = 500, error_code: str = 'UNKNOWN_ERROR'):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        super().__init__(self.message)

    def __str__(self):
        return f'[{self.error_code}] {self.message} (HTTP {self.status_code})'


class AmazonAdsRateLimitError(AmazonAdsError):
    """
    Error raised when Amazon Ads API rate limit is exceeded.

    HTTP Status: 429 Too Many Requests
    """

    def __init__(self, message: str = 'Rate limit exceeded. Please try again later.'):
        super().__init__(
            message=message,
            status_code=429,
            error_code='RATE_LIMIT_EXCEEDED',
        )


class AmazonAdsServerError(AmazonAdsError):
    """
    Error raised when Amazon Ads API returns a server error.

    HTTP Status: 500 Internal Server Error
    """

    def __init__(self, message: str = 'Amazon Ads API server error.'):
        super().__init__(
            message=message,
            status_code=500,
            error_code='AWS_SERVER_ERROR',
        )


class AmazonAdsAuthError(AmazonAdsError):
    """
    Error raised when authentication with Amazon Ads API fails.

    HTTP Status: 401 Unauthorized
    """

    def __init__(self, message: str = 'Authentication failed.'):
        super().__init__(
            message=message,
            status_code=401,
            error_code='AUTH_FAILED',
        )


class AmazonAdsValidationError(AmazonAdsError):
    """
    Error raised when Amazon Ads API returns a validation error.

    HTTP Status: 400 Bad Request
    """

    def __init__(self, message: str = 'Invalid request data.'):
        super().__init__(
            message=message,
            status_code=400,
            error_code='VALIDATION_ERROR',
        )
