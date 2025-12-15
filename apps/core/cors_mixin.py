class CorsMixin:
    """
    Mixin to manually inject CORS headers into the response,
    bypassing middleware if necessary.
    Uses dispatch to wrap the entire view processing.
    """
    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        
        # Force CORS headers on EVERY response from this view
        response['Access-Control-Allow-Origin'] = '*'
        response['Access-Control-Allow-Methods'] = 'GET, POST, PUT, PATCH, DELETE, OPTIONS'
        response['Access-Control-Allow-Headers'] = 'Content-Type, X-CSRFToken, Authorization, Origin, Accept'
        response['Access-Control-Max-Age'] = '86400'
        
        return response
