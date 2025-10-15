# models.py
import os
from django.conf import settings
from django.db import models
from django.utils import timezone
from django_countries.fields import CountryField
import uuid


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

def get_category_choices():
    choices = [('', 'Select Category')]
    choices += [(c.id, c.name) for c in Category.objects.all()]
    return choices

# --------------------------------------------
# def get_category_id():
#
#     choices = [('', 'Select Category')]  # Placeholder
#     choices += [(str(c.id), str(c.id)) for c in Category.objects.all()]  # 👈 id as both value & label
#     return choices

# --------------------------------------------

def get_category_id():
    """Safely return category choices, even when the DB isn't ready."""
    try:
        return [('', 'Select Category')] + [
            (str(c.id), str(c.id)) for c in Category.objects.all()
        ]
    except Exception:
        # Happens before migrations or when DB is unavailable
        return [('', 'Select Category')]


# --------------------------------------------

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


    title = models.CharField(max_length=10, choices=TITLE_CHOICES, blank=True)
    first_name = models.CharField(max_length=100)
    second_name = models.CharField(max_length=100)

    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=50)

    organization_type = models.CharField(max_length=100, choices=ORG_TYPE_CHOICES)
    other_organization_type = models.CharField(max_length=255, blank=True, null=True)

    job_title = models.CharField(max_length=255, blank=True)

    interests = models.JSONField(default=list, blank=True)
    other_interest = models.TextField(blank=True, null=True)

    category = models.CharField(max_length=50, choices=get_category_id, blank=False, verbose_name="Registration Category")
    privacy_agreed = models.BooleanField(default=False, verbose_name="Agreed to Privacy Policy")

    accessibility_needs = models.TextField(blank=True, null=True)
    updates_opt_in = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    unsubscribe_token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    national_id_number = models.CharField(max_length=20, unique=True, blank=True, null=True, verbose_name="National ID Number")

    national_id_scan = models.FileField(upload_to="uploads/id_scans/", blank=True, null=True, verbose_name="Scanned National ID (JPG/PDF)")

    passport_photo = models.FileField(upload_to="uploads/passport_photos/", blank=True, null=True, verbose_name="Passport Photo (JPG/PDF)")

    def display_org_type(self):
        base_label = self.get_organization_type_display()
        if self.other_organization_type:
            return f"{base_label} - {self.other_organization_type}"
        return base_label

    def display_interests(self):
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

    # ✅ Automatically ensure upload folders exist
    def save(self, *args, **kwargs):
        upload_dirs = [
            os.path.join(settings.MEDIA_ROOT, "uploads/id_scans"),
            os.path.join(settings.MEDIA_ROOT, "uploads/passport_photos"),
            os.path.join(settings.MEDIA_ROOT, "uploads/exhibitors/id_scans/"),
            os.path.join(settings.MEDIA_ROOT, "uploads/exhibitors/photos/"),
            os.path.join(settings.MEDIA_ROOT, "uploads/partners/logos/"),
        ]
        for path in upload_dirs:
            os.makedirs(path, exist_ok=True)
        super().save(*args, **kwargs)



# ---------------------------
# New registration model for applications on IOS & Android
# ---------------------------

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





# --------------------------------------------
# gallery model
# --------------------------------------------

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


# --------------------------------------------


class SummitPartner(models.Model):
    """Represents a sponsor or partner displayed on the website."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=150, help_text="Official name of the partner or sponsor")
    logo = models.ImageField(upload_to="uploads/partners/logos/", help_text="Upload the partner's logo image")
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



# --------------------------------------------
# Schedule model
# --------------------------------------------

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


# --------------------------------------------

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


# --------------------------------------------

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


# --------------------------------------------

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


# --------------------------------------------
# speaker model
# --------------------------------------------

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
    photo = models.ImageField(upload_to="uploads/speakers/", blank=True, null=True)
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
        return "static/images/speakers/placeholder.webp"


# --------------------------------------------

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


# --------------------------------------------

class EmailLog(models.Model):
    STATUS_CHOICES = [
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('pending', 'Pending'),
    ]

    registrant = models.ForeignKey('Registrant', on_delete=models.CASCADE, related_name='emaillog')
    recipient = models.EmailField()
    subject = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    sent_at = models.DateTimeField(null=False, blank=False)
    attempts = models.IntegerField(default=0)
    error_message = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        # ✅ Automatically set sent_at if not provided
        if not self.sent_at:
            self.sent_at = timezone.now()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.recipient} - {self.status} ({self.sent_at.strftime('%Y-%m-%d %H:%M')})"





# --------------------------------------------


class EmailLogs(models.Model):
    STATUS_CHOICES = [
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('pending', 'Pending'),
    ]

    exhibitor = models.ForeignKey('Exhibitor', on_delete=models.CASCADE, related_name='emaillog')
    recipient = models.EmailField()
    subject = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    sent_at = models.DateTimeField(null=False, blank=False)
    attempts = models.IntegerField(default=0)
    error_message = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        # ✅ Automatically set sent_at if not provided
        if not self.sent_at:
            self.sent_at = timezone.now()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.recipient} - {self.status} ({self.sent_at.strftime('%Y-%m-%d %H:%M')})"




# --------------------------------------------
# EXHIBITION SECTION
# --------------------------------------------
class ExhibitionSection(models.Model):
    """Sections within the exhibition hall (e.g., Innovation, Corporate, Startups)."""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

    @property
    def available_booths(self):
        """Return only unbooked booths."""
        return self.booths.filter(is_booked=False)


# --------------------------------------------
# BOOTH
# --------------------------------------------
class Booth(models.Model):
    BOOTH_TYPE_CHOICES = [
        ('standard', 'Standard Booth'),
        ('premium', 'Premium Booth'),
        ('custom', 'Custom Booth'),
    ]

    section = models.ForeignKey(
        ExhibitionSection, on_delete=models.CASCADE, related_name="booths"
    )
    booth_number = models.CharField(max_length=20, unique=True)
    booth_type = models.CharField(
        max_length=20, choices=BOOTH_TYPE_CHOICES, default='standard'
    )
    size = models.CharField(max_length=50, help_text="e.g., 3m x 3m")
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_booked = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.booth_number} - {self.get_booth_type_display()}"

    def mark_booked(self):
        self.is_booked = True
        self.save(update_fields=['is_booked'])

    def mark_available(self):
        self.is_booked = False
        self.save(update_fields=['is_booked'])


# --------------------------------------------
# BOOTH BOOKING
# --------------------------------------------
class BoothBooking(models.Model):
    exhibitor = models.ForeignKey(
        "Exhibitor", on_delete=models.CASCADE, related_name="bookings"
    )
    booth = models.OneToOneField(
        Booth, on_delete=models.CASCADE, related_name="booking"
    )
    booked_at = models.DateTimeField(default=timezone.now)
    approved = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.exhibitor.organization_name} → {self.booth.booth_number}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Auto mark the booth as booked
        self.booth.mark_booked()

    def delete(self, *args, **kwargs):
        # Free up booth on deletion
        self.booth.mark_available()
        super().delete(*args, **kwargs)


# --------------------------------------------
# EXHIBITOR
# --------------------------------------------

class Exhibitor(models.Model):
    """Main exhibitor registration details (local & international)."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # --- Personal Info ---
    title = models.CharField(
        max_length=10,
        choices=[
            ('', 'Select Title'),
            ("Prof", "Prof."),
            ("Dr", "Dr."),
            ("Mr", "Mr."),
            ("Mrs", "Mrs."),
            ("Ms", "Ms."),
        ],
    )
    first_name = models.CharField(max_length=100)
    second_name = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20)

    # --- Organization Info ---
    organization_type = models.CharField(max_length=200)
    job_title = models.CharField(max_length=200)
    category = models.CharField(
        max_length=50,
        choices=[
            ('', 'Select Category'),
            ('startup', 'Startup'),
            ('corporate', 'Corporate'),
            ('government', 'Government Agency'),
            ('academic', 'Academic Institution'),
            ('ngo', 'NGO'),
            ('other', 'Other'),
        ],
    )
    product_description = models.TextField(blank=True, null=True)

    # --- Booth & Section ---
    booth = models.ForeignKey("Booth", on_delete=models.SET_NULL, null=True, blank=True)
    section = models.ForeignKey("ExhibitionSection", on_delete=models.SET_NULL, null=True, blank=True)

    # --- Identity Verification ---
    national_id_number = models.CharField(max_length=50)
    national_id_scan = models.FileField(upload_to="uploads/exhibitors/id_scans/")
    passport_photo = models.ImageField(upload_to="uploads/exhibitors/photos/")

    # --- Business Type Toggle ---
    BUSINESS_TYPE_CHOICES = [
        ('local', 'Local (Kenyan)'),
        ('international', 'International'),
    ]
    business_type = models.CharField(
        max_length=20,
        choices=BUSINESS_TYPE_CHOICES,
        default='local',
        help_text="Select whether this is a local or international business",
    )

    # --- Business Documents ---
    kra_pin = models.CharField(max_length=20, blank=True, null=True)
    business_registration_doc = models.FileField(upload_to="uploads/exhibitors/business_docs/", blank=True, null=True)
    international_business_doc = models.FileField(upload_to="uploads/exhibitors/international_docs/", blank=True, null=True)

    # --- Country (django-countries) ---
    country_of_registration = CountryField(blank=True, null=True)

    # --- Beneficial Ownership ---
    beneficial_owner_details = models.TextField(blank=True, null=True)
    beneficial_owner_doc = models.FileField(upload_to="uploads/exhibitors/owners_docs/", blank=True, null=True)

    # --- Legal & Timestamps ---
    privacy_agreed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def get_full_name(self):
        return f"{self.title} {self.first_name} {self.second_name or ''}".strip()

    def __str__(self):
        return f"{self.get_full_name()} - {self.organization_type}"

# --------------------------------------------

class BeneficialOwner(models.Model):
    exhibitor = models.ForeignKey(
        Exhibitor, on_delete=models.CASCADE, related_name="owners"
    )
    full_name = models.CharField(max_length=255)
    nationality = models.CharField(max_length=500)
    identification_type = models.CharField(
        max_length=20,
        choices=[('national_id', 'National ID'), ('passport', 'Passport')]
    )
    id_number = models.CharField(max_length=50)
    ownership_percentage = models.DecimalField(
        max_digits=5, decimal_places=2, blank=True, null=True
    )
    supporting_document = models.FileField(
        upload_to="uploads/exhibitors/ownership_docs/", blank=True, null=True
    )

    def __str__(self):
        return f"{self.full_name} ({self.ownership_percentage or 0}%)"
