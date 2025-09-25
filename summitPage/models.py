from django.db import models
import uuid


class Registrant(models.Model):
    TITLE_CHOICES = [
        ('', 'Select Title'),
        ("Prof", "Prof."),
        ("Dr", "Dr."),
        ("Eng", "Eng."),
        ("Mr", "Mr."),
        ("Mrs", "Mrs."),
        ("Ms", "Ms"),
    ]

    ORG_TYPE_CHOICES = [
        ('', 'Select Organization Type'),
        ("Government Agency", "Government Agency"),
        ("Private Company", "Private Company"),
        ("Academic Institution", "Academic Institution"),
        ("Sector Association", "Sector Association"),
        ("Industry Advocacy Groups", "Industry Advocacy Groups"),
        ("Development Partners", "Development Partners"),
        ("other", "Others"),
    ]

    INTEREST_CHOICES = [
        ("knowledge", "Knowledge and skill development"),
        ("networking", "Networking and Community building"),
        ("business", "Business and Career Growth"),
        ("others", "Others"),
    ]

    # ==== Fields ====
    title = models.CharField(max_length=10, choices=TITLE_CHOICES, blank=True)
    first_name = models.CharField(max_length=100)
    second_name = models.CharField(max_length=100)

    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=50)

    organization_type = models.CharField(max_length=100, choices=ORG_TYPE_CHOICES)
    other_organization_type = models.CharField(max_length=255, blank=True, null=True)

    job_title = models.CharField(max_length=255, blank=True)

    interests = models.JSONField(default=list, blank=True)
    other_interest = models.CharField(max_length=255, blank=True, null=True)

    accessibility_needs = models.TextField(blank=True, null=True)
    updates_opt_in = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    unsubscribe_token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    # ==== Display helpers ====
    def display_org_type(self):
        """
        Always merge dropdown + textbox if textbox is filled.
        Example: 'Private Company - Safaricom'
        """
        base_label = self.get_organization_type_display()
        if self.other_organization_type:
            return f"{base_label} - {self.other_organization_type}"
        return base_label

    def display_interests(self):
        """Return interests as labels, merging 'Others' with custom text if provided."""
        items = []
        for i in self.interests:
            if i in ["other", "others"] and self.other_interest:
                items.append(self.other_interest)
            else:
                items.append(dict(self.INTEREST_CHOICES).get(i, i))
        return ", ".join(items)

    def __str__(self):
        return f"{self.title} {self.first_name} {self.second_name}"
