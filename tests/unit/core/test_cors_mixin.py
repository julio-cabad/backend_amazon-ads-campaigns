"""
Tests for CorsMixin.
"""
import pytest
from django.http import HttpResponse
from django.views import View
from unittest.mock import Mock

from apps.core.cors_mixin import CorsMixin


class TestCorsMixin:
    
    def test_dispatch_sets_cors_headers(self):
        """Test that CorsMixin sets CORS headers via dispatch."""
        
        # Create a test view that uses CorsMixin
        class TestView(CorsMixin, View):
            def get(self, request, *args, **kwargs):
                return HttpResponse("test content")
        
        # Create an instance of the view
        view = TestView()
        
        # Mock request
        request = Mock()
        request.method = 'GET'
        
        # Call dispatch
        response = view.dispatch(request)
        
        # Verify CORS headers are present
        assert response['Access-Control-Allow-Origin'] == '*'
        assert response['Access-Control-Allow-Methods'] == 'GET, POST, PUT, PATCH, DELETE, OPTIONS'
        assert response['Access-Control-Allow-Headers'] == 'Content-Type, X-CSRFToken, Authorization, Origin, Accept'
    
    def test_dispatch_preserves_response_content(self):
        """Test that CorsMixin preserves the original response content."""
        
        # Create a test view that uses CorsMixin
        class TestView(CorsMixin, View):
            def get(self, request, *args, **kwargs):
                return HttpResponse("original content")
        
        # Create an instance of the view
        view = TestView()
        
        # Mock request
        request = Mock()
        request.method = 'GET'
        
        # Call dispatch
        response = view.dispatch(request)
        
        # Verify response content is preserved
        assert response.content == b"original content"
        # Verify CORS headers are added
        assert response['Access-Control-Allow-Origin'] == '*'
    
    def test_dispatch_sets_cors_headers_for_post(self):
        """Test that CorsMixin sets CORS headers for POST requests."""
        
        # Create a test view that uses CorsMixin
        class TestView(CorsMixin, View):
            def post(self, request, *args, **kwargs):
                return HttpResponse("post response")
        
        # Create an instance of the view
        view = TestView()
        
        # Mock request
        request = Mock()
        request.method = 'POST'
        
        # Call dispatch
        response = view.dispatch(request)
        
        # Verify CORS headers are present
        assert response['Access-Control-Allow-Origin'] == '*'
        assert response['Access-Control-Allow-Methods'] == 'GET, POST, PUT, PATCH, DELETE, OPTIONS'
        assert response['Access-Control-Allow-Headers'] == 'Content-Type, X-CSRFToken, Authorization, Origin, Accept'
    
    def test_dispatch_works_with_multiple_http_methods(self):
        """Test that CorsMixin works with all HTTP methods."""
        
        # Create a test view that uses CorsMixin
        class TestView(CorsMixin, View):
            def get(self, request, *args, **kwargs):
                return HttpResponse("get")
            
            def post(self, request, *args, **kwargs):
                return HttpResponse("post")
            
            def put(self, request, *args, **kwargs):
                return HttpResponse("put")
            
            def patch(self, request, *args, **kwargs):
                return HttpResponse("patch")
            
            def delete(self, request, *args, **kwargs):
                return HttpResponse("delete")
        
        methods = ['GET', 'POST', 'PUT', 'PATCH', 'DELETE']
        
        for method in methods:
            # Create a new instance for each test
            view = TestView()
            
            # Mock request
            request = Mock()
            request.method = method
            
            # Call dispatch
            response = view.dispatch(request)
            
            # Verify CORS headers are present
            assert response['Access-Control-Allow-Origin'] == '*'
            assert response['Access-Control-Allow-Methods'] == 'GET, POST, PUT, PATCH, DELETE, OPTIONS'
            assert response['Access-Control-Allow-Headers'] == 'Content-Type, X-CSRFToken, Authorization, Origin, Accept'
            assert response.content == method.lower().encode()
