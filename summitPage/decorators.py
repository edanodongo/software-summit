from django.conf import settings
from django.http import JsonResponse

def require_api_key(view_func):
    """
    Decorator to check for a valid API key in the request header.
    Usage:
        @require_api_key
        def my_view(request):
            ...
    """
    def wrapper(request, *args, **kwargs):
        auth_header = request.headers.get("Authorization")

        if not auth_header or not auth_header.startswith("Bearer "):
            return JsonResponse(
                {"detail": "Authorization header missing or invalid."},
                status=401
            )

        token = auth_header.split("Bearer ")[1].strip()

        if token != settings.REG_SERVICE_API_KEY:
            return JsonResponse(
                {"detail": "Invalid API key."},
                status=403
            )

        return view_func(request, *args, **kwargs)

    return wrapper
