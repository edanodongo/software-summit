from django.apps import AppConfig
from django.contrib.auth import get_user_model
from django.db.models.signals import post_migrate

def create_default_admin(sender, **kwargs):
    User = get_user_model()
    if not User.objects.filter(username="admin").exists():
        User.objects.create_superuser(
            username="admin",
            email="admin@summit.com",
            password="admin123"
        )
        # print("Default admin created: admin / admin123")

        
class SummitpageConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'summitPage'

    def ready(self):
        post_migrate.connect(create_default_admin, sender=self)
