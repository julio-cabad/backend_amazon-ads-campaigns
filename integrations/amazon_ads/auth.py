"""
Simulated AWS4 Authentication for Amazon Ads API.

This module provides a mock implementation of AWS Signature Version 4
authentication headers. In a real implementation, this would create
proper HMAC-SHA256 signatures.

Reference: https://docs.aws.amazon.com/general/latest/gr/signature-version-4.html
"""
import hashlib
import hmac
import time
from datetime import datetime
from typing import Optional

import structlog

logger = structlog.get_logger(__name__)


class AWS4Auth:
    """
    Mock AWS Signature Version 4 authentication.

    This class simulates the AWS4 authentication process used by Amazon APIs.
    In production, this would create proper cryptographic signatures.
    """

    def __init__(
        self,
        access_key: str,
        secret_key: str,
        region: str = 'us-east-1',
        service: str = 'execute-api',
    ):
        """
        Initialize AWS4Auth with credentials.

        Args:
            access_key: AWS access key ID
            secret_key: AWS secret access key
            region: AWS region (default: us-east-1)
            service: AWS service name (default: execute-api)
        """
        self.access_key = access_key
        self.secret_key = secret_key
        self.region = region
        self.service = service

    def get_auth_headers(
        self,
        method: str,
        url: str,
        payload: Optional[str] = None,
    ) -> dict:
        """
        Generate authentication headers for a request.

        This is a simplified mock that generates realistic-looking headers
        without actually performing cryptographic operations.

        Args:
            method: HTTP method (GET, POST, etc.)
            url: Request URL
            payload: Request body (optional)

        Returns:
            Dictionary of authentication headers
        """
        timestamp = datetime.utcnow()
        amz_date = timestamp.strftime('%Y%m%dT%H%M%SZ')
        date_stamp = timestamp.strftime('%Y%m%d')

        # Simulated payload hash (would be SHA256 in real implementation)
        payload_hash = self._hash_payload(payload or '')

        # Simulated signature
        signature = self._generate_mock_signature(method, url, amz_date)

        # Credential scope
        credential_scope = f'{date_stamp}/{self.region}/{self.service}/aws4_request'

        # Authorization header
        authorization = (
            f'AWS4-HMAC-SHA256 '
            f'Credential={self.access_key}/{credential_scope}, '
            f'SignedHeaders=host;x-amz-date, '
            f'Signature={signature}'
        )

        headers = {
            'X-Amz-Date': amz_date,
            'X-Amz-Content-Sha256': payload_hash,
            'Authorization': authorization,
        }

        logger.debug(
            'aws4_auth_headers_generated',
            method=method,
            amz_date=amz_date,
        )

        return headers

    def _hash_payload(self, payload: str) -> str:
        """Generate SHA256 hash of payload."""
        return hashlib.sha256(payload.encode('utf-8')).hexdigest()

    def _generate_mock_signature(self, method: str, url: str, amz_date: str) -> str:
        """
        Generate a mock signature.

        In a real implementation, this would:
        1. Create a canonical request
        2. Create a string to sign
        3. Calculate the signature using HMAC-SHA256

        Here we generate a realistic-looking hex string.
        """
        # Create a deterministic but fake signature
        data = f'{method}:{url}:{amz_date}:{self.secret_key}'
        mock_sig = hashlib.sha256(data.encode()).hexdigest()
        return mock_sig


def create_amazon_ads_auth(
    client_id: str,
    client_secret: str,
    refresh_token: str,
    region: str = 'NA',
) -> dict:
    """
    Create authentication headers for Amazon Ads API.

    This simulates the OAuth + AWS4 auth flow used by Amazon Ads.

    Args:
        client_id: Amazon Ads client ID
        client_secret: Amazon Ads client secret
        refresh_token: OAuth refresh token
        region: Amazon Ads region (NA, EU, FE)

    Returns:
        Dictionary of headers to include in requests
    """
    # Simulate getting an access token (would be OAuth in production)
    mock_access_token = hashlib.sha256(
        f'{client_id}:{refresh_token}:{time.time()}'.encode()
    ).hexdigest()[:64]

    headers = {
        'Amazon-Advertising-API-ClientId': client_id,
        'Authorization': f'Bearer {mock_access_token}',
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    }

    # Add AWS4 signature for extra authenticity
    aws4 = AWS4Auth(
        access_key=client_id[:20] if len(client_id) > 20 else client_id,
        secret_key=client_secret,
        region='us-east-1',
        service='advertising-api',
    )
    auth_headers = aws4.get_auth_headers('POST', 'https://advertising-api.amazon.com')
    headers.update(auth_headers)

    logger.debug(
        'amazon_ads_auth_created',
        has_token=bool(mock_access_token),
    )

    return headers
