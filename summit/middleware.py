from django.conf import settings
from django.contrib import messages
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.utils import timezone


class AutoLogoutMiddleware:
    """
    Logs out users after a period of inactivity.
    Redirects directly to login with an inactivity message.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.timeout = getattr(settings, "AUTO_LOGOUT_TIMEOUT", 60 * 15)

    def __call__(self, request):
        if request.user.is_authenticated:
            now = timezone.now()
            last_activity_str = request.session.get("last_activity")

            if last_activity_str:
                try:
                    last_activity = timezone.datetime.fromisoformat(last_activity_str)
                    if timezone.is_naive(last_activity):
                        last_activity = timezone.make_aware(last_activity)
                    elapsed = (now - last_activity).total_seconds()

                    if elapsed > self.timeout:
                        logout(request)
                        request.session.flush()
                        messages.warning(request, "You were logged out due to inactivity.")
                        return redirect("custom_login")  # ✅ redirect straight to login
                except Exception:
                    request.session.pop("last_activity", None)

            request.session["last_activity"] = now.isoformat()

        return self.get_response(request)
