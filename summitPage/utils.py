# registrations/utils.py
from django.core.mail import send_mail
from django.conf import settings

def send_confirmation_email(registrant):
    subject = "Summit Registration Confirmation"
    message = (
        f"Hello {registrant.full_name},\n\n"
        "Thank you for registering for the Summit!\n\n"
        "📅 Date: 11th – 13th November 2025\n"
        "📍 Venue: Nairobi International Conference Center\n\n"
        "We’re excited to have you join us. You’ll receive more updates "
        "closer to the event.\n\n"
        "Best regards,\n"
        "The Summit Organizing Team"
    )

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [registrant.email],
        fail_silently=False,
    )
