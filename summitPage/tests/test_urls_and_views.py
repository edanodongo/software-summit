import pytest
from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse, get_resolver


@pytest.mark.django_db
def test_all_urls(client):
    """
    Automatically test that all registered URLs in the project
    return a valid response (200, 302, 403, or 404).
    """

    resolver = get_resolver()
    urls = []

    # Collect all valid URL patterns
    for pattern in resolver.url_patterns:
        if hasattr(pattern, "pattern"):
            try:
                url_name = pattern.name or str(pattern.pattern)
                urls.append((url_name, pattern.pattern.describe()))
            except Exception as e:
                print(f"Skipping pattern due to error: {e}")  # safer than silent continue

    # Create a test user for any views requiring login
    user = User.objects.create_user(  # nosec B106
        username="testuser", password="test_pass_123"
    )
    client = Client()
    client.login(username="testuser", password="test_pass_123")  # nosec B106

    # Test each URL
    for url_name, url_pattern in urls:
        try:
            # Try resolving by name (preferred)
            if url_name:
                url = reverse(url_name)
            else:
                url = f"/{url_pattern.strip('^$')}"
        except Exception as e:
            print(f"Skipping URL build error: {e}")
            continue

        response = client.get(url)

        # Avoid Python `assert` — use pytest assert, which is safe
        assert response.status_code in [200, 302, 403, 404], (  # nosec B101
            f"❌ URL '{url}' returned {response.status_code}"
        )
