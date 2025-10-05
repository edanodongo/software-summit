import json
import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = "Create a default admin user using JSON config"

    def handle(self, *args, **options):
        # Adjust path to where your config.json is located
        config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'config.json')

        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
        except Exception as e:
            self.stderr.write(f"❌ Could not load config.json: {e}")
            return

        username = config.get("DJANGO_ADMIN_USERNAME", "admin")
        email = config.get("DJANGO_ADMIN_EMAIL", "admin@example.com")
        password = config.get("DJANGO_ADMIN_PASSWORD", None)

        if not password:
            self.stderr.write("❌ DJANGO_ADMIN_PASSWORD is missing in config.json")
            return

        User = get_user_model()
        if not User.objects.filter(username=username).exists():
            User.objects.create_superuser(
                username=username,
                email=email,
                password=password
            )
            self.stdout.write(self.style.SUCCESS(f"✅ Default admin created: {username} / [hidden password]"))
        else:
            self.stdout.write(f"ℹ️ Admin user '{username}' already exists.")
