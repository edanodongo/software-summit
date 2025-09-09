from django.core.mail import send_mail
from django.conf import settings

def send_confirmation_email(registrant):
    subject = "Kenya Software Summit Registration"
    message = (
        f"Hello {registrant.full_name},\n\n"
        "Thank you for registering for the 2025 Kenya Software Summit! \n\n"
        "Details:\n"
        f"- Category: {registrant.get_category_display()}\n"
        f"- Organization: {registrant.organization or 'N/A'}\n\n"
        "We’ll keep you updated with more information as the event approaches.\n\n"
        "Best regards,\nThe Summit Team"
    )

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [registrant.email],
        fail_silently=False,
    )
