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



# from django.db import models
# from django.utils import timezone
# import uuid

# # ---------------------------
# # Core event / venue models
# # ---------------------------

# class Event(models.Model):
#     """Top-level event (a summit). You can host multiple events in the same system."""
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     name = models.CharField(max_length=255)
#     slug = models.SlugField(max_length=255, unique=True)
#     description = models.TextField(blank=True)
#     start_date = models.DateTimeField()
#     end_date = models.DateTimeField()
#     timezone = models.CharField(max_length=64, default="UTC")
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     def __str__(self):
#         return self.name


# class Venue(models.Model):
#     """Venue for an event. Can hold rooms, halls, and floor plans."""
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="venues")
#     name = models.CharField(max_length=255)
#     address = models.TextField(blank=True)
#     latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
#     longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
#     map_embed_url = models.URLField(blank=True, null=True)
#     created_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"{self.name} - {self.event.name}"


# class VenueRoom(models.Model):
#     """Rooms inside a venue (used for session locations)."""
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     venue = models.ForeignKey(Venue, on_delete=models.CASCADE, related_name="rooms")
#     name = models.CharField(max_length=255)
#     capacity = models.PositiveIntegerField(blank=True, null=True)
#     floor = models.CharField(max_length=50, blank=True)
#     layout_image = models.ImageField(upload_to="venue_layouts/", blank=True, null=True)

#     def __str__(self):
#         return f"{self.name} ({self.venue.name})"

# # ---------------------------
# # Tracks, tags and categories
# # ---------------------------

# class Track(models.Model):
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="tracks")
#     name = models.CharField(max_length=150)
#     slug = models.SlugField(max_length=150)
#     description = models.TextField(blank=True)
#     color_hex = models.CharField(max_length=7, blank=True)  # optional UI hint

#     class Meta:
#         unique_together = ("event", "slug")

#     def __str__(self):
#         return self.name


# class Tag(models.Model):
#     """Generic tags (topics, interests) used across sessions and attendees."""
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     name = models.CharField(max_length=100, unique=True)

#     def __str__(self):
#         return self.name

# # ---------------------------
# # Sessions & agenda
# # ---------------------------

# class Session(models.Model):
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="sessions")
#     title = models.CharField(max_length=255)
#     slug = models.SlugField(max_length=255)
#     abstract = models.TextField(blank=True)
#     description = models.TextField(blank=True)
#     start_time = models.DateTimeField()
#     end_time = models.DateTimeField()
#     track = models.ForeignKey(Track, on_delete=models.SET_NULL, null=True, blank=True, related_name="sessions")
#     room = models.ForeignKey(VenueRoom, on_delete=models.SET_NULL, null=True, blank=True, related_name="sessions")
#     capacity = models.PositiveIntegerField(null=True, blank=True)
#     tags = models.ManyToManyField(Tag, blank=True, related_name="sessions")
#     is_keynote = models.BooleanField(default=False)
#     is_panel = models.BooleanField(default=False)
#     created_at = models.DateTimeField(auto_now_add=True)

#     class Meta:
#         ordering = ("start_time",)
#         unique_together = ("event", "slug")

#     def __str__(self):
#         return f"{self.title} ({self.event.name})"


# class SessionSpeakerRole(models.Model):
#     """Role of a speaker on a session (speaker, moderator, panelist)."""
#     ROLE_CHOICES = [("speaker", "Speaker"), ("moderator", "Moderator"), ("panelist", "Panelist")]
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name="speaker_roles")
#     speaker = models.ForeignKey("Speaker", on_delete=models.CASCADE, related_name="session_roles")
#     role = models.CharField(max_length=32, choices=ROLE_CHOICES, default="speaker")

#     class Meta:
#         unique_together = ("session", "speaker", "role")

#     def __str__(self):
#         return f"{self.speaker} as {self.role} for {self.session}"

# # ---------------------------
# # People: Speakers, Exhibitors, Sponsors
# # ---------------------------

# class Speaker(models.Model):
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     name = models.CharField(max_length=255)
#     bio = models.TextField(blank=True)
#     photo = models.ImageField(upload_to="speakers/", blank=True, null=True)
#     organization = models.CharField(max_length=255, blank=True)
#     title = models.CharField(max_length=255, blank=True)
#     social_links = models.JSONField(default=dict, blank=True)  # e.g. {"linkedin": "...", "twitter": "..."}
#     created_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return self.name


# class Exhibitor(models.Model):
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="exhibitors")
#     name = models.CharField(max_length=255)
#     description = models.TextField(blank=True)
#     logo = models.ImageField(upload_to="exhibitors/", blank=True, null=True)
#     website = models.URLField(blank=True, null=True)
#     booth_number = models.CharField(max_length=64, blank=True, null=True)
#     contact_email = models.EmailField(blank=True, null=True)
#     created_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return self.name


# class Sponsor(models.Model):
#     LEVEL_CHOICES = [("platinum", "Platinum"), ("gold", "Gold"), ("silver", "Silver"), ("bronze", "Bronze")]
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="sponsors")
#     name = models.CharField(max_length=255)
#     level = models.CharField(max_length=32, choices=LEVEL_CHOICES)
#     logo = models.ImageField(upload_to="sponsors/", blank=True, null=True)
#     website = models.URLField(blank=True, null=True)
#     display_order = models.PositiveIntegerField(default=0)

#     def __str__(self):
#         return f"{self.name} ({self.level})"

# # ---------------------------
# # Registration & Attendee
# # ---------------------------
# # Note: You already provided a Registration model in the prompt. We'll refer to it here
# # as a pre-existing model. If you prefer to use Django's AUTH user model, replace
# # references to Registration with settings.AUTH_USER_MODEL.

# class AttendeeProfile(models.Model):
#     """Profile information connected to Registration."""
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     registration = models.OneToOneField("Registration", on_delete=models.CASCADE, related_name="profile")
#     display_name = models.CharField(max_length=255, blank=True)
#     bio = models.TextField(blank=True)
#     photo = models.ImageField(upload_to="attendees/", blank=True, null=True)
#     interests = models.JSONField(default=list, blank=True)  # list of tags or strings
#     social_links = models.JSONField(default=dict, blank=True)
#     company = models.CharField(max_length=255, blank=True)
#     job_title = models.CharField(max_length=255, blank=True)
#     created_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return self.display_name or self.registration.get_full_name()


# class ConnectionRequest(models.Model):
#     STATUS_CHOICES = [("pending", "Pending"), ("accepted", "Accepted"), ("declined", "Declined"), ("blocked", "Blocked")]
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     from_profile = models.ForeignKey(AttendeeProfile, related_name="sent_requests", on_delete=models.CASCADE)
#     to_profile = models.ForeignKey(AttendeeProfile, related_name="received_requests", on_delete=models.CASCADE)
#     status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
#     message = models.TextField(blank=True)
#     created_at = models.DateTimeField(auto_now_add=True)

#     class Meta:
#         unique_together = (("from_profile", "to_profile"),)

#     def __str__(self):
#         return f"{self.from_profile} -> {self.to_profile} ({self.status})"


# class ChatThread(models.Model):
#     """Optional grouping for messages between multiple participants (2+)."""
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="chat_threads")
#     participants = models.ManyToManyField(AttendeeProfile, related_name="chat_threads")
#     created_at = models.DateTimeField(auto_now_add=True)


# class ChatMessage(models.Model):
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     thread = models.ForeignKey(ChatThread, on_delete=models.CASCADE, related_name="messages", null=True, blank=True)
#     sender = models.ForeignKey(AttendeeProfile, on_delete=models.CASCADE, related_name="sent_messages")
#     receiver = models.ForeignKey(AttendeeProfile, on_delete=models.CASCADE, related_name="received_messages", null=True, blank=True)
#     message = models.TextField()
#     attachments = models.JSONField(default=list, blank=True)  # list of file refs
#     created_at = models.DateTimeField(auto_now_add=True)

#     class Meta:
#         ordering = ("created_at",)

# # ---------------------------
# # Tickets, Orders, Payments, Check-ins
# # ---------------------------

# class TicketType(models.Model):
#     """Defines ticket types available for purchase for an event."""
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="ticket_types")
#     name = models.CharField(max_length=100)  # e.g., Standard, VIP, Student
#     slug = models.SlugField(max_length=100)
#     description = models.TextField(blank=True)
#     price = models.DecimalField(max_digits=10, decimal_places=2)
#     quantity = models.PositiveIntegerField(null=True, blank=True)  # null = unlimited
#     active = models.BooleanField(default=True)

#     class Meta:
#         unique_together = (("event", "slug"),)

#     def __str__(self):
#         return f"{self.name} - {self.event.name}"


# class Order(models.Model):
#     """User order which may contain multiple Ticket instances."""
#     STATUS_CHOICES = [("pending", "Pending"), ("paid", "Paid"), ("cancelled", "Cancelled"), ("refunded", "Refunded")]
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     registration = models.ForeignKey("Registration", on_delete=models.CASCADE, related_name="orders")
#     event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="orders")
#     status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
#     total_amount = models.DecimalField(max_digits=12, decimal_places=2)
#     currency = models.CharField(max_length=10, default="USD")
#     payment_reference = models.CharField(max_length=255, blank=True, null=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     def __str__(self):
#         return f"Order {self.id} - {self.registration.email}"


# class Ticket(models.Model):
#     """A concrete ticket issued to a registration (can be multiple per order)."""
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="tickets")
#     ticket_type = models.ForeignKey(TicketType, on_delete=models.PROTECT)
#     holder = models.ForeignKey("Registration", on_delete=models.CASCADE, related_name="tickets")
#     issued_at = models.DateTimeField(auto_now_add=True)
#     qr_code = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)  # token encoded into QR
#     checked_in = models.BooleanField(default=False)
#     checked_in_at = models.DateTimeField(null=True, blank=True)

#     def __str__(self):
#         return f"{self.ticket_type.name} for {self.holder.email}"


# class Payment(models.Model):
#     """Record coming back from the payment gateway."""
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name="payment")
#     gateway = models.CharField(max_length=64)  # e.g., stripe, flutterwave
#     amount = models.DecimalField(max_digits=12, decimal_places=2)
#     currency = models.CharField(max_length=10, default="USD")
#     reference = models.CharField(max_length=255, unique=True)
#     raw_response = models.JSONField(blank=True, null=True)
#     status = models.CharField(max_length=32)  # authorized, captured, failed
#     created_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"Payment {self.reference} ({self.status})"


# class CheckIn(models.Model):
#     """Records ticket check-ins (scanning QR codes)."""
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     ticket = models.OneToOneField(Ticket, on_delete=models.CASCADE, related_name="checkin")
#     scanned_by = models.ForeignKey("Registration", on_delete=models.SET_NULL, null=True, blank=True)  # staff who scanned
#     scanned_at = models.DateTimeField(auto_now_add=True)
#     location = models.CharField(max_length=255, blank=True)

#     def __str__(self):
#         return f"CheckIn {self.ticket} at {self.scanned_at}"

# # ---------------------------
# # Engagement: Polls, Q&A, Live
# # ---------------------------

# class Poll(models.Model):
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="polls")
#     session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name="polls", null=True, blank=True)
#     question = models.CharField(max_length=512)
#     anonymous = models.BooleanField(default=False)
#     created_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return self.question


# class PollOption(models.Model):
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     poll = models.ForeignKey(Poll, on_delete=models.CASCADE, related_name="options")
#     text = models.CharField(max_length=255)
#     order = models.PositiveIntegerField(default=0)

#     def vote_count(self):
#         return self.responses.count()

#     def __str__(self):
#         return self.text


# class PollResponse(models.Model):
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     poll = models.ForeignKey(Poll, on_delete=models.CASCADE, related_name="responses")
#     option = models.ForeignKey(PollOption, on_delete=models.CASCADE, related_name="responses")
#     registration = models.ForeignKey("Registration", on_delete=models.SET_NULL, null=True, blank=True)
#     created_at = models.DateTimeField(auto_now_add=True)

#     class Meta:
#         unique_together = (("poll", "registration"),)  # one vote per user


# class Question(models.Model):
#     """Live Q&A question posted by an attendee for a session."""
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name="questions")
#     registration = models.ForeignKey("Registration", on_delete=models.SET_NULL, null=True, blank=True)
#     text = models.TextField()
#     upvotes = models.PositiveIntegerField(default=0)
#     answered = models.BooleanField(default=False)
#     created_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"Q: {self.text[:80]}"


# class QuestionAnswer(models.Model):
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="answers")
#     responder = models.ForeignKey(Speaker, on_delete=models.SET_NULL, null=True, blank=True)
#     text = models.TextField()
#     created_at = models.DateTimeField(auto_now_add=True)

# # ---------------------------
# # Feedback & Surveys
# # ---------------------------

# class Feedback(models.Model):
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="feedback")
#     registration = models.ForeignKey("Registration", on_delete=models.SET_NULL, null=True, blank=True)
#     session = models.ForeignKey(Session, on_delete=models.SET_NULL, null=True, blank=True)
#     rating = models.PositiveSmallIntegerField(null=True, blank=True)  # 1-5
#     comment = models.TextField(blank=True)
#     created_at = models.DateTimeField(auto_now_add=True)


# # ---------------------------
# # Notifications & push
# # ---------------------------

# class Notification(models.Model):
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="notifications")
#     title = models.CharField(max_length=255)
#     body = models.TextField()
#     data = models.JSONField(blank=True, null=True)  # arbitrary payload for the app
#     send_at = models.DateTimeField(null=True, blank=True)  # scheduled
#     created_at = models.DateTimeField(auto_now_add=True)
#     sent = models.BooleanField(default=False)
#     target_registrations = models.ManyToManyField("Registration", blank=True)

#     def __str__(self):
#         return self.title


# class PushSubscription(models.Model):
#     """Holds a user's device subscription info for web push / mobile tokens."""
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     registration = models.ForeignKey("Registration", on_delete=models.CASCADE, related_name="push_subscriptions")
#     device_id = models.CharField(max_length=255, blank=True)
#     platform = models.CharField(max_length=50, blank=True)  # android, ios, web
#     token = models.TextField()  # FCM token or push subscription JSON
#     created_at = models.DateTimeField(auto_now_add=True)

# # ---------------------------
# # Media & misc
# # ---------------------------

# class MediaAsset(models.Model):
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="media_assets")
#     file = models.FileField(upload_to="media/")
#     caption = models.CharField(max_length=255, blank=True)
#     uploaded_at = models.DateTimeField(auto_now_add=True)


# class FloorPlan(models.Model):
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     venue = models.ForeignKey(Venue, on_delete=models.CASCADE, related_name="floor_plans")
#     image = models.ImageField(upload_to="floorplans/")
#     description = models.TextField(blank=True)


# class Booth(models.Model):
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     exhibitor = models.ForeignKey(Exhibitor, on_delete=models.CASCADE, related_name="booths")
#     floor_plan = models.ForeignKey(FloorPlan, on_delete=models.SET_NULL, null=True, blank=True)
#     x = models.FloatField(null=True, blank=True)  # normalized coordinates
#     y = models.FloatField(null=True, blank=True)
#     width = models.FloatField(null=True, blank=True)
#     height = models.FloatField(null=True, blank=True)
#     label = models.CharField(max_length=255, blank=True)

# # ---------------------------
# # Admin, logs & utilities
# # ---------------------------

# class AdminActionLog(models.Model):
#     """Simple audit log for admin dashboard actions."""
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     user = models.ForeignKey("Registration", on_delete=models.SET_NULL, null=True, blank=True)
#     event = models.ForeignKey(Event, on_delete=models.SET_NULL, null=True, blank=True)
#     action = models.CharField(max_length=255)
#     details = models.JSONField(blank=True, null=True)
#     created_at = models.DateTimeField(auto_now_add=True)

# # ---------------------------
# # Helpers / Managers to be added below (e.g. availability checks, seat allocation, etc.)
# # ---------------------------




