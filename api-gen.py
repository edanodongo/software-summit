import secrets


def generate_api_key(length=32):
    # Generates a secure random API key (URL-safe)
    return secrets.token_urlsafe(length)


# Example usage
api_key = generate_api_key()
# Use the API key programmatically, don’t print or log it
