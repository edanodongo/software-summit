from django.core.mail import send_mail
from django.conf import settings
from datetime import datetime


def send_confirmation_email(registrant):
    subject = "Kenya Software Summit Registration"

    plain_message = (
        f"Welcome {registrant.title} {registrant.first_name} {registrant.second_name},\n\n"
        "Thank you for successfully registering for the Software Summit 2025.\n\n"
        "We are delighted to welcome you to this year’s Software Summit, taking place from "
        "10th November - 12th November , 2025 at Eldoret Moi University  Annex campus, Eldoret City, Uasin Gishu County, Kenya.\n\n"
        "The theme for this year is: “Connecting Minds, Shaping Software, Driving Growth.”\n\n"
        "Upon your arrival in Eldoret, our team will receive you and confirm your delegate status. "
        "To facilitate this, kindly carry a valid identification document. "
        "You will then be issued with a badge, a delegate’s pack containing your conference guide, "
        "and the full programme to help you easily navigate the conference activities.\n\n"
        "This experience has been thoughtfully tailored to meet your innovative needs and standards.\n\n"
        "Karibu.\n\n"
        "Best regards,\nThe Software Summit Team"
    )

    current_year = datetime.now().year

    html_message = f"""
    <html>
      <body style="font-family: Arial, sans-serif; background-color:#f4f6f9; padding:20px; margin:0;">
        <div style="max-width:650px; margin:40px auto; background:#ffffff; border-radius:8px; padding:30px; border:1px solid #e0e0e0;">
          <!-- Ministry Logo -->
          <div style="text-align:center; margin-bottom:20px;">
            <img src="https://Sylvester976.github.io/geoclock/static/images/banner-logo.png" alt="MINISTRY LOGO" style="height:70px;">
          </div>

          <!-- Summit Logo -->
          <div style="text-align:center; margin-bottom:20px;">
            <img src="https://Sylvester976.github.io/geoclock/static/images/summit_logo.png" alt="Summit Logo" style="height:60px;">
          </div>

          <!-- Greeting -->
          <h2 style="color:#2c3e50; text-align:center; margin-bottom:10px;">
            Welcome {registrant.title} {registrant.first_name} {registrant.second_name},
          </h2>

          <!-- Intro -->
          <p style="color:#333; font-size:15px; text-align:center; margin-bottom:25px;">
            Thank you for successfully registering for the <strong>Software Summit 2025</strong>.
          </p>

          <p style="color:#333; font-size:14px; margin-bottom:20px;">
            We are delighted to welcome you to this year’s Software Summit, taking place from 
            10th November -12th November , 2025 at  Eldoret Moi University  Annex campus, <strong>Eldoret City, Uasin Gishu County, Kenya</strong>.
          </p>

          <p style="color:#333; font-size:14px; margin-bottom:20px;">
            <em>Theme:</em> <strong>“Connecting Minds, Shaping Software, Driving Growth”</strong>
          </p>

          <p style="color:#333; font-size:14px; margin-bottom:20px;">
            Upon your arrival in Eldoret, our team will receive you and confirm your delegate status. 
            To facilitate this, kindly carry a valid identification document. You will then receive 
            a badge, a delegate’s pack containing your conference guide, and the programme for 
            easier navigation of the conference activities.
          </p>

          <p style="color:#333; font-size:14px; margin-bottom:20px;">
            This experience has been thoughtfully tailored to meet your innovative needs and standards.
          </p>

          <p style="color:#333; font-size:14px; margin-bottom:20px;">
            <strong>Karibu!</strong>
          </p>

          <!-- CTA button -->
          <div style="margin:30px 0; text-align:center;">
            <a href="https://softwaresummit.go.ke/" 
               style="background-color:#007bff; color:#fff; padding:12px 25px; border-radius:4px; text-decoration:none; font-weight:bold; font-size:14px;">
              Visit Summit Portal
            </a>
          </div>

          <p style="margin-top:30px; color:#333; font-size:14px;">
            Best regards,<br><strong>The Software Summit Team</strong>
          </p>
        </div>

        <!-- Footer outside card -->
        <footer style="text-align:center; font-size:12px; color:#888; margin-top:20px;">
          <p>&copy; {current_year} Kenya Software Summit.</p>
          <p>The Ministry of Information, Communications and The Digital Economy</p>
          <p>6th Floor, Bruce House, Standard Street</p>
          <p>Email: softwaresummit@ict.go.ke</p>
          <p>All rights reserved.</p>
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

