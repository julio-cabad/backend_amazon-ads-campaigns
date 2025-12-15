"""
Tests for ForceCorsMiddleware.
"""
import pytest
from django.http import HttpResponse
from unittest.mock import Mock

from apps.core.middleware import ForceCorsMiddleware


class TestForceCorsMiddleware:
    
    def test_sets_cors_headers_on_regular_request(self):
        """Test that CORS headers are set on regular responses."""
        # Mock the get_response callable
        get_response = Mock(return_value=HttpResponse())
        middleware = ForceCorsMiddleware(get_response)
        
        # Mock request
        request = Mock()
        request.method = 'GET'
        request.path = '/api/test'
        
        # Call middleware
        response = middleware(request)
        
        # Verify CORS headers are set
        assert response['Access-Control-Allow-Origin'] == '*'
        assert response['Access-Control-Allow-Methods'] == 'GET, POST, PUT, PATCH, DELETE, OPTIONS'
        assert response['Access-Control-Allow-Headers'] == 'Content-Type, X-CSRFToken, Authorization, Origin, Accept'
        assert get_response.called
    
    def test_handles_options_request(self):
        """Test that OPTIONS requests return 200 with empty content."""
        # Mock the get_response callable
        get_response = Mock()
        middleware = ForceCorsMiddleware(get_response)
        
        # Mock OPTIONS request
        request = Mock()
        request.method = 'OPTIONS'
        request.path = '/api/test'
        
        # Call middleware
        response = middleware(request)
        
        # Verify OPTIONS handling
        assert response.status_code == 200
        assert not response.content  # Empty content
        assert response['Access-Control-Allow-Origin'] == '*'
        assert response['Access-Control-Allow-Methods'] == 'GET, POST, PUT, PATCH, DELETE, OPTIONS'
        assert response['Access-Control-Allow-Headers'] == 'Content-Type, X-CSRFToken, Authorization, Origin, Accept'
        
        # Verify get_response was NOT called (short-circuited)
        assert not get_response.called
    
    def test_sets_cors_headers_on_post_request(self):
        """Test that CORS headers are set on POST responses."""
        # Mock the get_response callable
        get_response = Mock(return_value=HttpResponse())
        middleware = ForceCorsMiddleware(get_response)
        
        # Mock POST request
        request = Mock()
        request.method = 'POST'
        request.path = '/api/test'
        
        # Call middleware
        response = middleware(request)
        
        # Verify CORS headers are set
        assert response['Access-Control-Allow-Origin'] == '*'
        assert response['Access-Control-Allow-Methods'] == 'GET, POST, PUT, PATCH, DELETE, OPTIONS'
        assert response['Access-Control-Allow-Headers'] == 'Content-Type, X-CSRFToken, Authorization, Origin, Accept'
        assert get_response.called
    
    def test_sets_cors_headers_on_all_http_methods(self):
        """Test that CORS headers are set for all HTTP methods."""
        methods = ['GET', 'POST', 'PUT', 'PATCH', 'DELETE']
        
        for method in methods:
            # Mock the get_response callable
            get_response = Mock(return_value=HttpResponse())
            middleware = ForceCorsMiddleware(get_response)
            
            # Mock request
            request = Mock()
            request.method = method
            request.path = '/api/test'
            
            # Call middleware
            response = middleware(request)
            
            # Verify CORS headers are set
            assert response['Access-Control-Allow-Origin'] == '*'
            assert response['Access-Control-Allow-Methods'] == 'GET, POST, PUT, PATCH, DELETE, OPTIONS'
            assert response['Access-Control-Allow-Headers'] == 'Content-Type, X-CSRFToken, Authorization, Origin, Accept'
            assert get_response.called
