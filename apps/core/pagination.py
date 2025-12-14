"""
Custom pagination classes for the API.
"""
from rest_framework.pagination import PageNumberPagination


class StandardResultsSetPagination(PageNumberPagination):
    """
    Standard pagination for API results.

    Provides consistent pagination across all endpoints with
    configurable page size via query parameters.
    """

    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100

    def get_paginated_response(self, data):
        """
        Return a paginated response with additional metadata.
        """
        response = super().get_paginated_response(data)
        response.data['page'] = self.page.number
        response.data['total_pages'] = self.page.paginator.num_pages
        return response


class LargeResultsSetPagination(PageNumberPagination):
    """
    Pagination for endpoints that may return large datasets.
    """

    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 500
