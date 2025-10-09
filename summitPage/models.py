from django.db import models
import uuid


# ---------------------------
# Initial Registration model
# --------------------------- 

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
        ('', 'Select Organization'),
        ("Government Agency", "Government Agency"),
        ("Private Company", "Private Company"),
        ("Academic Institution", "Academic Institution"),
        ("Sector Association", "Sector Association"),
        ("Industry Advocacy Groups", "Industry Advocacy Groups"),
        ("Development Partners", "Development Partners"),
        ("Student", "Student"),
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

    
    def get_full_name(self):
        return f"{self.title} {self.first_name} {self.second_name}".strip()

    def __str__(self):
        return f"{self.title} {self.first_name} {self.second_name}"






# ---------------------------
# New registration model for applications on IOS & Android
# --------------------------- 

from django.db import models
import uuid


class Registration(models.Model):
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
        ('', 'Select Organization'),
        ("Government Agency", "Government Agency"),
        ("Private Company", "Private Company"),
        ("Academic Institution", "Academic Institution"),
        ("Sector Association", "Sector Association"),
        ("Industry Advocacy Groups", "Industry Advocacy Groups"),
        ("Development Partners", "Development Partners"),
        ("Student", "Student"),
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
            if i == "others" and self.other_interest:
                items.append(self.other_interest)
            else:
                items.append(dict(self.INTEREST_CHOICES).get(i, i))
        return ", ".join(items)

    def get_full_name(self):
        return f"{self.title} {self.first_name} {self.second_name}".strip()

    def __str__(self):
        return self.get_full_name()




# All new models



#---------------------------
# gallery model

from django.db import models
from django.utils import timezone

class SummitGallery(models.Model):
    """Model for managing event gallery images shown in the gallery section."""
    title = models.CharField(max_length=150)
    image = models.ImageField(upload_to='gallery/')
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    uploaded_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', '-uploaded_at']

    def __str__(self):
        return self.title


#--------------------------------


# Partners
from django.db import models
import uuid

class SummitPartner(models.Model):
    """Represents a sponsor or partner displayed on the website."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=150, help_text="Official name of the partner or sponsor")
    logo = models.ImageField(upload_to="partners/logos/", help_text="Upload the partner's logo image")
    website = models.URLField(blank=True, null=True, help_text="Optional: Link to partner website")
    order = models.PositiveIntegerField(default=0, help_text="Order of display on the sponsors section")
    is_active = models.BooleanField(default=True, help_text="Show or hide this partner on the site")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["order", "name"]
        verbose_name = "Partner"
        verbose_name_plural = "Partners"

    def __str__(self):
        return self.name



#------------------------------------------------
# Schedule model 

from django.db import models
from django.utils import timezone

class SummitScheduleDay(models.Model):
    """Represents each summit day (e.g., Day 1, Day 2, Day 3)."""
    title = models.CharField(max_length=100, help_text="e.g. Day 1 - November 10")
    date = models.DateField(help_text="Date of the event day.")
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["date"]
        verbose_name = "Schedule Day"
        verbose_name_plural = "Schedule Days"

    def __str__(self):
        return f"{self.title} ({self.date})"


class SummitTimeSlot(models.Model):
    """Represents a time slot block on a given day."""
    day = models.ForeignKey(SummitScheduleDay, on_delete=models.CASCADE, related_name="timeslots")
    start_time = models.TimeField()
    end_time = models.TimeField(blank=True, null=True)
    label = models.CharField(max_length=100, blank=True, help_text="Optional label like 'All Day' or 'Morning'")
    duration = models.CharField(max_length=50, blank=True, null=True, help_text="e.g. 1 hr 30 min")

    class Meta:
        ordering = ["start_time"]
        verbose_name = "Time Slot"
        verbose_name_plural = "Time Slots"

    def __str__(self):
        return f"{self.day.title} - {self.start_time.strftime('%I:%M %p')}"


class SummitSession(models.Model):
    """Represents each session or event in the schedule."""
    SESSION_TYPES = [
        ("keynote", "Keynote"),
        ("networking", "Networking"),
        ("panel", "Panel Discussion"),
        ("break", "Break"),
        ("workshop", "Workshop"),
        ("hackathon", "Hackathon"),
        ("exhibition", "Exhibition"),
        ("closing", "Closing"),
        ("other", "Other"),
    ]

    timeslot = models.ForeignKey(SummitTimeSlot, on_delete=models.CASCADE, related_name="sessions")
    session_type = models.CharField(max_length=50, choices=SESSION_TYPES, default="other")
    title = models.CharField(max_length=200, help_text="e.g. 'Software Ecosystem Landscape'")
    description = models.TextField(blank=True, null=True)
    venue = models.CharField(max_length=100, blank=True, null=True)
    is_break = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0, help_text="Order of appearance in the slot")

    class Meta:
        ordering = ["timeslot__start_time", "order"]
        verbose_name = "Session"
        verbose_name_plural = "Sessions"

    def __str__(self):
        return f"{self.title} ({self.session_type})"


class SummitPanelist(models.Model):
    """Panelists or presenters associated with a session."""
    session = models.ForeignKey(SummitSession, on_delete=models.CASCADE, related_name="panelists")
    role = models.CharField(max_length=150, help_text="e.g. 'Keynote Address', 'Presentation', 'Moderator'")
    name = models.CharField(max_length=200, blank=True, null=True, help_text="e.g. 'Dr. Jane Doe'")
    organization = models.CharField(max_length=200, blank=True, null=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]
        verbose_name = "Panelist"
        verbose_name_plural = "Panelists"

    def __str__(self):
        return f"{self.role}: {self.name or 'TBA'}"


#--------------------------------
# speaker model
from django.db import models
import uuid

class SummitSpeaker(models.Model):
    """Model for Summit Speakers."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    full_name = models.CharField(max_length=150)
    position = models.CharField(max_length=150)
    organization = models.CharField(max_length=250)
    track = models.CharField(max_length=100, blank=True, help_text="E.g., Keynote Speaker, Panelist, Moderator")
    topic = models.CharField(max_length=255)
    summary = models.TextField(blank=True)
    bio = models.TextField(blank=True)
    photo = models.ImageField(upload_to="speakers/", blank=True, null=True)
    linkedin_url = models.URLField(blank=True, null=True)
    twitter_url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["full_name"]

    def __str__(self):
        return self.full_name

    def photo_url(self):
        """Returns photo URL safely for templates."""
        if self.photo:
            return self.photo.url
        return "/static/images/default-speaker.png"


class ApiAccessLog(models.Model):
    api_key = models.CharField(max_length=100, blank=True, null=True)
    endpoint = models.CharField(max_length=255)
    method = models.CharField(max_length=10)
    ip_address = models.GenericIPAddressField()
    status_code = models.PositiveSmallIntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.method} {self.endpoint} - {self.status_code}"



