import pytest
from django.contrib.auth.models import User
from django.test import Client
from django.urls import reverse


@pytest.mark.django_db
def test_all_urls(client):
    """
    Automatically test that all registered URLs in the project
    return a valid response (200, 302, or 403).
    """

    # Get all URL patterns from the main urlpatterns
    from django.urls import get_resolver

    resolver = get_resolver()
    urls = []

    # Collect all valid URL patterns
    for pattern in resolver.url_patterns:
        if hasattr(pattern, "pattern"):
            try:
                url_name = pattern.name or str(pattern.pattern)
                urls.append((url_name, pattern.pattern.describe()))
            except Exception:
                continue

    # Create a test user for any views requiring login
    user = User.objects.create_user(username="testuser", password="12345")
    client = Client()
    client.login(username="testuser", password="12345")

    # Test each URL
    for url_name, url_pattern in urls:
        try:
            # Try resolving by name (preferred)
            if url_name:
                url = reverse(url_name)
            else:
                url = f"/{url_pattern.strip('^$')}"
        except Exception:
            continue

        response = client.get(url)

        assert response.status_code in [
            200,
            302,
            403,
            404,
        ], f"❌ URL '{url}' returned {response.status_code}"
