from django.core.mail import send_mail
from django.conf import settings
from datetime import datetime


def send_confirmation_email(registrant):
    subject = "Kenya Software Summit Registration"
    plain_message = (
        f"Hello {registrant.first_name} {registrant.second_name},\n\n"
        "Thank you for registering for the 2025 Kenya Software Summit!\n\n"
        "Details:\n"
        f"- Category: {registrant.organization_type}\n"
        f"- Organization: {registrant.other_organization_type or 'N/A'}\n\n"
        "We’ll keep you updated with more information as the event approaches.\n\n"
        "Best regards,\nThe Summit Team"
    )

    current_year = datetime.now().year

    html_message = f"""
    <html>
      <body style="font-family: Arial, sans-serif; background-color:#f4f6f9; padding:20px; margin:0;">
        <div style="max-width:650px; margin:40px auto; background:#ffffff; border-radius:8px; padding:30px; border:1px solid #e0e0e0;">

          <!-- Ministry Logo -->
          <div style="text-align:center; margin-bottom:20px;">
            <img src="https://iili.io/KcnJtXs.md.png" alt="MINISTRY LOGO" style="height:70px;">
          </div>

          <!-- Summit Logo -->
          <div style="text-align:center; margin-bottom:20px;">
            <img src="https://iili.io/KcnJDLG.md.png" alt="Summit Logo" style="height:60px;">
          </div>

          <!-- Greeting -->
          <h2 style="color:#2c3e50; text-align:center; margin-bottom:10px;">Hello {registrant.first_name} {registrant.second_name},</h2>
          <p style="color:#333; font-size:15px; text-align:center; margin-bottom:25px;">
            Thank you for registering for the <strong>2025 Kenya Software Summit!</strong>
          </p>

          <!-- Details in tabular style -->
          <table style="width:100%; border-collapse:collapse; margin-bottom:25px; font-size:14px; color:#333;">
            <tr>
              <td style="border:1px solid #ddd; padding:8px; font-weight:bold; width:35%;">Category</td>
              <td style="border:1px solid #ddd; padding:8px;">{registrant.organization_type}</td>
            </tr>
            <tr>
              <td style="border:1px solid #ddd; padding:8px; font-weight:bold;">Organization</td>
              <td style="border:1px solid #ddd; padding:8px;">{registrant.other_organization_type or 'N/A'}</td>
            </tr>
          </table>

          <!-- CTA button -->
          <div style="margin:30px 0; text-align:center;">
            <a href="https://softwaresummit.go.ke/" 
               style="background-color:#007bff; color:#fff; padding:12px 25px; border-radius:4px; text-decoration:none; font-weight:bold; font-size:14px;">
              Visit Summit Portal
            </a>
          </div>

          <p style="color:#333; font-size:14px;">We’ll keep you updated with more information as the event approaches.</p>

          <p style="margin-top:30px; color:#333; font-size:14px;">Best regards,<br><strong>The Summit Team</strong></p>
        </div>

        <!-- Footer outside card -->
        <footer style="text-align:center; font-size:12px; color:#888; margin-top:20px;">
          <p>&copy; {current_year} Kenya Software Summit.</p>
          <p> The Ministry of Information, Communications and The Digital Economy</p>
          <p> 6th Floor, Bruce House, Standard Street</p>
          <p> Email: softwaresummit@ict.go.ke </p>
          <p>  All rights reserved.</p>
        </footer>
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
