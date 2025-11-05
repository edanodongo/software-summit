import json
import os

from django.apps import AppConfig
from django.contrib.auth import get_user_model
from django.db import OperationalError, ProgrammingError, connection
from django.db.models.signals import post_migrate


def load_config():
    """Load admin credentials from config.json."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config_path = os.path.join(base_dir, "config.json")
    try:
        with open(config_path, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Failed to load config.json: {e}")
        return {}


def table_exists(table_name):
    """Check if a table exists in the database."""
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT EXISTS (
                SELECT FROM information_schema.tables
                WHERE table_name = %s
            )
        """,
            [table_name],
        )
        return cursor.fetchone()[0]


def create_default_admin(sender, **kwargs):
    """Ensure only the admin from config.json exists."""
    config = load_config()
    username = config.get("DJANGO_ADMIN_USERNAME", "summitAdmin")
    email = config.get("DJANGO_ADMIN_EMAIL", "softwaresummit@ict.go.ke")
    password = config.get("DJANGO_ADMIN_PASSWORD", None)

    if not password:
        print("⚠️ DJANGO_ADMIN_PASSWORD missing in config.json. Skipping default admin creation.")
        return

    try:
        if table_exists("auth_user"):
            User = get_user_model()

            # ✅ Delete existing superusers except the one defined in config
            deleted_count, _ = (
                User.objects.filter(is_superuser=True).exclude(username=username).delete()
            )
            if deleted_count:
                print(f"🗑️ Deleted {deleted_count} old admin user(s).")

            # ✅ Create or update the configured admin
            admin, created = User.objects.update_or_create(
                username=username,
                defaults={
                    "email": email,
                    "is_superuser": True,
                    "is_staff": True,
                },
            )
            if created:
                admin.set_password(password)
                admin.save()
                print(f"✅ Default admin created: {username}")
            else:
                # Ensure password stays synced with config
                admin.set_password(password)
                admin.save()
                print(f"🔄 Default admin updated: {username}")

    except (ProgrammingError, OperationalError) as e:
        # Happens if DB isn't ready yet (e.g. first migration)
        print(f"⚠️ Skipping admin creation: {e}")


class SummitpageConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "summitPage"

    def ready(self):
        post_migrate.connect(create_default_admin, sender=self)
