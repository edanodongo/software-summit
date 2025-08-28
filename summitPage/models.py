from django.db import models

# Create your models here.
from django.db import models

class Registration(models.Model):
    REG_TYPES = [
        ("student", "Student"),
        ("professional", "Professional"),
        ("corporate", "Corporate"),
    ]
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20)
    reg_type = models.CharField(max_length=20, choices=REG_TYPES)
    organization = models.CharField(max_length=200, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"
