from django.core.mail import send_mail
from django.conf import settings
from datetime import datetime


def send_confirmation_email(registrant):
    subject = "Kenya Software Summit Registration"
    plain_message = (
        f"Hello {registrant.first_name},\n\n"
        "Thank you for registering for the 2025 Kenya Software Summit!\n\n"
        "Details:\n"
        f"- Category: {registrant.organization_type()}\n"
        f"- Organization: {registrant.other_organization_type or 'N/A'}\n\n"
        "We’ll keep you updated with more information as the event approaches.\n\n"
        "Best regards,\nThe Summit Team"
    )

    current_year = datetime.now().year  # dynamic year

    html_message = f"""
    <html>
      <body style="font-family: Arial, sans-serif; background-color:#f9f9f9; padding:20px;">
        <div style="max-width:600px; margin:0 auto; background:#ffffff; border-radius:8px; padding:20px; border:1px solid #ddd;">
          <div style="text-align:center; margin-bottom:20px;">
            <img src="https://example.com/static/logo.png" alt="Summit Logo" style="height:60px;">
          </div>
          <h2 style="color:#2c3e50;">Hello {registrant.first_name},</h2>
          <p>Thank you for registering for the <strong>2025 Kenya Software Summit!</strong></p>

          <h3 style="margin-top:20px; color:#2c3e50;">Details:</h3>
          <ul style="line-height:1.6; color:#555;">
            <li><strong>Category:</strong> {registrant.organization_type()}</li>
            <li><strong>Organization:</strong> {registrant.other_organization_type or 'N/A'}</li>
          </ul>

          <p>We’ll keep you updated with more information as the event approaches.</p>

          <p style="margin-top:30px;">Best regards,<br><strong>The Summit Team</strong></p>

          <hr style="margin:30px 0; border:none; border-top:1px solid #eee;">
          <footer style="text-align:center; font-size:12px; color:#888;">
            <p>&copy; {current_year} Kenya Software Summit.<br>
            All rights reserved.</p>
          </footer>
        </div>
      </body>
    </html>
    """

    send_mail(
        subject,
        plain_message,
        settings.DEFAULT_FROM_EMAIL,
        [registrant.email],
        fail_silently=False,
        html_message=html_message,
    )
