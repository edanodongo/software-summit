# registrations/models.py
from django.db import models
import uuid

class Registrant(models.Model):
    CATEGORY_CHOICES = [
        ('govt', 'Government'),
        ('private', 'Private Sector'),
        ('startup', 'Startup'),
        ('academia', 'Academia'),
        ('student', 'Student'),
        ('investor', 'Investor'),
        ('other', 'Other'),
    ]

    INTEREST_CHOICES = [
        ('ai', 'AI'),
        ('cybersecurity', 'Cybersecurity'),
        ('cloud', 'Cloud'),
        ('data_science', 'Data Science'),
        ('mobile_apps', 'Mobile Apps'),
        ('policy', 'Policy & Governance'),
        ('other', 'Other'),
    ]

    full_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=50)
    organization = models.CharField(max_length=255, blank=True)
    job_title = models.CharField(max_length=255, blank=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    interests = models.JSONField(default=list, blank=True)  # stores checkbox selections
    accessibility_needs = models.TextField(blank=True, null=True)
    updates_opt_in = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
        
    updates_opt_in = models.BooleanField(default=False)
    unsubscribe_token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    def get_unsubscribe_url(self):
        from django.urls import reverse
        return reverse("unsubscribe", args=[str(self.unsubscribe_token)])

    def __str__(self):
        return self.full_name


