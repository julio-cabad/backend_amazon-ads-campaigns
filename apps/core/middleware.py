class ForceCorsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        print(f"ForceCorsMiddleware hit: {request.method} {request.path}")
        
        # Short-circuit OPTIONS requests (Preflight)
        if request.method == 'OPTIONS':
            from django.http import HttpResponse
            response = HttpResponse()
            response.status_code = 200
        else:
            response = self.get_response(request)

        # Force these headers on EVERY response
        response['Access-Control-Allow-Origin'] = '*'
        response['Access-Control-Allow-Methods'] = 'GET, POST, PUT, PATCH, DELETE, OPTIONS'
        response['Access-Control-Allow-Headers'] = 'Content-Type, X-CSRFToken, Authorization, Origin, Accept'
        response['Access-Control-Max-Age'] = '86400'
            
        return response
