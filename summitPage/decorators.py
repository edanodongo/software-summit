from django.conf import settings
from django.http import JsonResponse
from django.core.cache import cache
import time
import traceback
from .models import ApiAccessLog

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0]
    return request.META.get('REMOTE_ADDR')

def log_api_access(request, status_code, token=None):
    try:
        ApiAccessLog.objects.create(
            api_key=token,
            endpoint=request.path,
            method=request.method,
            ip_address=get_client_ip(request),
            status_code=status_code
        )
    except Exception as e:
        print("Failed to log API access:", e)
        traceback.print_exc()

def require_api_key(view_func):
    """
    Decorator to check for a valid API key, apply per-endpoint rate limiting,
    and log all API accesses (success and error responses).
    """
    def wrapper(request, *args, **kwargs):
        auth_header = request.headers.get("Authorization")
        token = None
        status_code = 500  # default in case of unexpected errors

        try:
            if not auth_header or not auth_header.startswith("Bearer "):
                status_code = 401
                return JsonResponse({"detail": "Authorization header missing or invalid."}, status=status_code)

            token = auth_header.split("Bearer ")[1].strip()

            if token != settings.REG_SERVICE_API_KEY:
                status_code = 403
                return JsonResponse({"detail": "Invalid API key."}, status=status_code)

            # --- Rate limiting ---
            RATE_LIMIT_REQUESTS = getattr(settings, "RATE_LIMIT_REQUESTS", 60)
            RATE_LIMIT_PERIOD = getattr(settings, "RATE_LIMIT_PERIOD", 60)

            endpoint_key = f"rl:{token}:{request.path}:{request.method}"
            record = cache.get(endpoint_key)
            current_time = int(time.time())

            if record:
                count, start_time = record
                if current_time - start_time < RATE_LIMIT_PERIOD:
                    if count >= RATE_LIMIT_REQUESTS:
                        status_code = 429
                        retry_after = RATE_LIMIT_PERIOD - (current_time - start_time)
                        return JsonResponse(
                            {
                                "detail": "Rate limit exceeded. Try again later.",
                                "retry_after_seconds": retry_after,
                                "limit": RATE_LIMIT_REQUESTS,
                                "period": RATE_LIMIT_PERIOD,
                            },
                            status=status_code
                        )
                    else:
                        cache.set(endpoint_key, (count + 1, start_time), RATE_LIMIT_PERIOD)
                else:
                    cache.set(endpoint_key, (1, current_time), RATE_LIMIT_PERIOD)
            else:
                cache.set(endpoint_key, (1, current_time), RATE_LIMIT_PERIOD)

            # --- Call the actual view ---
            response = view_func(request, *args, **kwargs)
            status_code = getattr(response, "status_code", 200)
            return response

        finally:
            # --- Log the access regardless of outcome ---
            log_api_access(request, status_code=status_code, token=token)

    return wrapper
