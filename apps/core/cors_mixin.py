from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.views import APIView
from rest_framework import status
from django.conf import settings

# --- ULTIMATE CORS PROXY ---
# If middleware fails, we handle CORS manually in a base view or mixin

class CorsMixin:
    """
    Mixin to manually inject CORS headers into the response,
    bypassing middleware if necessary.
    """
    def finalize_response(self, request, response, *args, **kwargs):
        response = super().finalize_response(request, response, *args, **kwargs)
        
        # Force CORS headers
        response['Access-Control-Allow-Origin'] = '*'
        response['Access-Control-Allow-Methods'] = 'GET, POST, PUT, PATCH, DELETE, OPTIONS'
        response['Access-Control-Allow-Headers'] = 'Content-Type, X-CSRFToken, Authorization'
        response['Access-Control-Max-Age'] = '86400'
        
        return response

# We need to monkey-patch or update the viewset to use this mixin.
# But better yet, let's create a custom middleware that sits at the VERY TOP via wsgi.py if possible,
# or just update the CampaignViewSet.

