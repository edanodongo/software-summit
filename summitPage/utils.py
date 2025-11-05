import secrets
import string
import time
import traceback
from datetime import datetime
from io import BytesIO

import qrcode
from barcode import Code128
from barcode.writer import ImageWriter
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.utils import timezone

from .models import Category, EmailLog, EmailLogs

from_email = settings.EMAIL_HOST_USER
current_year = datetime.now().year


def sendmailer(subject, message, recipients):
    """
    Send a styled email with logos and message card.
    All recipients are hidden using BCC.
    """
    if isinstance(recipients, str):
        recipients = [recipients]

    try:
        current_year = datetime.now().year

        # --- Logos section ---
        logo_section = """
                <div style="text-align:center; margin-bottom:20px;">
                  <img src="https://Sylvester976.github.io/geoclock/static/images/banner-logo.png"
                       alt="MINISTRY LOGO" style="height:70px;"><br>
                  <img src="https://Sylvester976.github.io/geoclock/static/images/summit_logo.png"
                       alt="Summit Logo" style="height:60px;">
                </div>
                """

        # --- Combine HTML ---
        html_message = f"""
                <html>
                <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                    {logo_section}
                    <div style="margin: 20px auto; max-width: 600px;">
                        {message}
                    </div>
                    <hr style="margin-top: 40px;">
                    <p style="font-size: 13px; color: #777; text-align:center;">
                        This email was sent by the Kenya Software & AI Summit Secretariat.
                    </p>
                    <footer style="text-align:center; font-size:12px; color:#888; margin-top:25px;">
                        <p>&copy; {current_year} The Kenya Software & AI Summit.</p>
                        <p>The Ministry of Information, Communications and The Digital Economy</p>
                        <p>6th Floor, Bruce House, Standard Street</p>
                        <p>Email: softwaresummit@ict.go.ke</p>
                        <p>All rights reserved.</p>
                    </footer>
                </body>
                </html>
                """

        # --- Plain text fallback ---
        plain_message = message

        # --- Compose & send ---
        # Send to yourself in "To" field, hide recipients in BCC
        email_obj = EmailMultiAlternatives(
            subject, plain_message, from_email, [from_email], bcc=recipients
        )
        email_obj.attach_alternative(html_message, "text/html")
        email_obj.mixed_subtype = "related"
        email_obj.send(fail_silently=False)

        print(f" Email sent successfully to {len(recipients)} recipients (hidden).")

    except Exception as e:
        print(" Email sending failed:", str(e))
        traceback.print_exc()


# --------------------------------------------
# Registrants
def send_confirmation_email(registrant, retries=3, delay=3):
    subject = "The Kenya Software & AI Summit Registration"
    from_email = "softwaresummit@ict.go.ke"
    to = [registrant.email]
    current_year = datetime.now().year
    error_message = None
    success = False
    attempt_count = 0

    try:
        # === Generate QR Code ===
        qr_data = (
            f"Name: {registrant.get_full_name()}\n"
            f"Email: {registrant.email}\n"
            f"Phone: {registrant.phone}\n"
            f"Organization: {registrant.display_org_type()}\n"
            f"Job Title: {registrant.job_title}"
        )
        qr_img = qrcode.make(qr_data)
        qr_buffer = BytesIO()
        qr_img.save(qr_buffer, format="PNG")

        # === Generate Barcode ===
        barcode_buffer = BytesIO()
        Code128(str(registrant.id), writer=ImageWriter()).write(barcode_buffer)

        # === HTML Body ===
        # === Plaintext Message ===

        plain_message = (
            f"Welcome {registrant.title} {registrant.first_name} {registrant.second_name},\n\n"
            "Thank you for successfully registering for the Kenya Software & AI Summit 2025.\n\n"
            "We are delighted to welcome you to this year’s Kenya Software & AI Summit, taking place from "
            "10th November - 12th November , 2025 at Eldoret Moi University  Annex campus, Eldoret City, Uasin Gishu County, Kenya.\n\n"
            "The theme for this year is: “Connecting Minds, Shaping Software, Driving Growth.”\n\n"
            "Upon your arrival in Eldoret, our team will receive you and confirm your delegate status. "
            "To facilitate this, kindly carry a valid identification document. "
            "You will then be issued with a badge, a delegate’s pack containing your conference guide, "
            "and the full programme to help you easily navigate the conference activities.\n\n"
            "This experience has been thoughtfully tailored to meet your innovative needs and standards.\n\n"
            "Karibu.\n\n"
            "Best regards,\nThe Kenya Software & AI Summit Team"
        )

        # === HTML Email Body ===
        html_message = f"""
        <html>
          <body style="font-family: Arial, sans-serif; background-color:#f4f6f9; padding:20px;">
            <div style="max-width:650px; margin:40px auto; background:#ffffff; border-radius:8px;
                        padding:30px; border:1px solid #e0e0e0;">

              <!-- Ministry Logo -->
              <div style="text-align:center; margin-bottom:20px;">
                <img src="https://Sylvester976.github.io/geoclock/static/images/banner-logo.png" alt="MINISTRY LOGO" style="height:70px;">
              </div>

              <!-- Summit Logo -->
              <div style="text-align:center; margin-bottom:20px;">
                <img src="https://Sylvester976.github.io/geoclock/static/images/summit_logo.png"
                     alt="Summit Logo" style="height:60px;">
              </div>

              <!-- Greeting -->
              <h2 style="color:#2c3e50; text-align:center; margin-bottom:10px;">
                Welcome {registrant.title} {registrant.first_name} {registrant.second_name},
              </h2>

              <!-- Intro -->
              <p style="color:#333; font-size:15px; text-align:center; margin-bottom:25px;">
                Thank you for successfully registering for the <strong>The Kenya Software & AI Summit 2025</strong>.
              </p>

              <p style="color:#333; font-size:14px; margin-bottom:20px;">
                We are delighted to welcome you to this year’s Kenya Software & AI Summit, taking place from 
                10th November -12th November , 2025 at Eldoret Moi University  Annex campus, <strong>Eldoret City, Uasin Gishu County, Kenya</strong>.
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

              <p style="margin-top:30px; text-align:center;">
                Best regards,<br><strong>The Kenya Software & AI Summit Team</strong>
              </p>
            </div>

            <!-- CTA button -->
            <div style="margin:30px 0; text-align:center;">
              <a href="https://softwaresummit.go.ke/" 
                style="background-color:#007bff; color:#fff; padding:12px 25px; border-radius:4px; text-decoration:none; font-weight:bold; font-size:14px;">
                Visit Summit Portal
              </a>
            </div>

            <!-- Footer outside card -->
            <footer style="text-align:center; font-size:12px; color:#888; margin-top:20px;">
              <p>&copy; {current_year} The Kenya Software & AI Summit.</p>
              <p>The Ministry of Information, Communications and The Digital Economy</p>
              <p>6th Floor, Bruce House, Standard Street</p>
              <p>Email: softwaresummit@ict.go.ke</p>
              <p>All rights reserved.</p>
            </footer>
          </body>
        </html>
        """

        # === Compose Email ===
        email = EmailMultiAlternatives(subject, plain_message, from_email, to)
        email.attach_alternative(html_message, "text/html")

        # qr_img_mime = MIMEImage(qr_buffer.getvalue(), _subtype="png")
        # qr_img_mime.add_header("Content-ID", "<qr_code>")
        # qr_img_mime.add_header("Content-Disposition", "inline", filename="qr.png")
        # email.attach(qr_img_mime)
        email.mixed_subtype = "related"

        # === Retry sending ===
        for attempt in range(1, retries + 1):
            attempt_count = attempt
            try:
                email.send(fail_silently=False)
                print(f"✅ Email sent successfully to {registrant.email} (attempt {attempt})")
                success = True
                break
            except Exception as send_error:
                error_message = str(send_error)
                print(f"⚠️ Attempt {attempt} failed: {error_message}")
                traceback.print_exc()
                if attempt < retries:
                    print(f"⏳ Retrying in {delay} seconds...")
                    time.sleep(delay)

    except Exception as e:
        error_message = f"Email preparation failed: {e}"
        traceback.print_exc()

    finally:
        # === Log outcome ===
        EmailLog.objects.create(
            registrant=registrant,
            recipient=registrant.email,
            subject=subject,
            status="success" if success else "failed",
            error_message=error_message,
            attempts=attempt_count,
            sent_at=timezone.now(),
        )


# --------------------------------------------


def get_category_name_from_id(category_id):
    try:
        category = Category.objects.get(id=category_id)
        return category.name
    except Category.DoesNotExist:
        return "Delegate"


# --------------------------------------------
# Exhibitor
def send_confirmation_mail(exhibitor, retries=3, delay=3):
    subject = "The Kenya Software & AI Summit Registration"
    from_email = "softwaresummit@ict.go.ke"
    to = [exhibitor.email]
    current_year = datetime.now().year
    error_message = None
    success = False
    attempt_count = 0

    try:
        # === Generate QR Code ===
        qr_data = (
            f"Name: {exhibitor.get_full_name()}\n"
            f"Email: {exhibitor.email}\n"
            f"Phone: {exhibitor.phone}\n"
            f"Organization: {exhibitor.organization_type}\n"
            f"Job Title: {exhibitor.job_title}"
        )
        qr_img = qrcode.make(qr_data)
        qr_buffer = BytesIO()
        qr_img.save(qr_buffer, format="PNG")

        # === Generate Barcode ===
        barcode_buffer = BytesIO()
        Code128(str(exhibitor.id), writer=ImageWriter()).write(barcode_buffer)

        # === HTML Body ===
        # === Plaintext Message ===

        plain_message = (
            f"Welcome {exhibitor.title} {exhibitor.first_name} {exhibitor.second_name},\n\n"
            "Thank you for booking your exhibitor booth for the Kenya Software & AI Summit 2025.\n\n"
            "We have received your booth reservation request for the upcoming summit, "
            "taking place from 10th November - 12th November, 2025 at Moi University Annex Campus, "
            "Eldoret City, Uasin Gishu County, Kenya.\n\n"
            "Theme: “Connecting Minds, Shaping Software, Driving Growth.”\n\n"
            "Please note that your booth booking is currently pending payment confirmation. "
            "To secure your booth, kindly proceed to make the required payment as outlined "
            "on the Summit Portal (https://softwaresummit.go.ke/). "
            "Once payment has been received, you will receive a confirmation email along with "
            "your booth allocation details.\n\n"
            "For any assistance or clarification regarding payment or booth allocation, "
            "please contact us at softwaresummit@ict.go.ke.\n\n"
            "We look forward to your participation and contribution to this year’s Summit.\n\n"
            "Karibu!\n\n"
            "Best regards,\nThe Kenya Software & AI Summit Team"
        )

        # === HTML Email Body ===
        html_message = f"""
        <html>
          <body style="font-family: Arial, sans-serif; background-color:#f4f6f9; padding:20px;">
            <div style="max-width:650px; margin:40px auto; background:#ffffff; border-radius:8px;
                        padding:30px; border:1px solid #e0e0e0;">

              <!-- Ministry Logo -->
              <div style="text-align:center; margin-bottom:20px;">
                <img src="https://Sylvester976.github.io/geoclock/static/images/banner-logo.png" alt="MINISTRY LOGO" style="height:70px;">
              </div>

              <!-- Summit Logo -->
              <div style="text-align:center; margin-bottom:20px;">
                <img src="https://Sylvester976.github.io/geoclock/static/images/summit_logo.png"
                     alt="Summit Logo" style="height:60px;">
              </div>

              <!-- Greeting -->
              <h2 style="color:#2c3e50; text-align:center; margin-bottom:10px;">
                Welcome {exhibitor.title} {exhibitor.first_name} {exhibitor.second_name},
              </h2>

              <!-- Intro -->
              <p style="color:#333; font-size:15px; text-align:center; margin-bottom:25px;">
                Thank you for booking your exhibitor booth for the <strong>Kenya Software & AI Summit 2025</strong>.
              </p>

              <p style="color:#333; font-size:14px; margin-bottom:20px;">
                We have received your booth reservation request for the upcoming summit, taking place from 
                <strong>10th – 12th November 2025</strong> at Moi University Annex Campus, 
                <strong>Eldoret City, Uasin Gishu County, Kenya</strong>.
              </p>

              <p style="color:#333; font-size:14px; margin-bottom:20px;">
                <em>Theme:</em> <strong>“Connecting Minds, Shaping Software, Driving Growth”</strong>
              </p>

              <p style="color:#333; font-size:14px; margin-bottom:20px;">
                Please note that your booth booking is currently <strong>pending payment confirmation</strong>. 
                To secure your booth, kindly proceed to make the required payment. 
                Once payment has been received, we will send you a confirmation email along with your booth allocation details.
              </p>

              <p style="color:#333; font-size:14px; margin-bottom:20px;">
                For assistance or clarification regarding payment or booth allocation, please contact us at 
                <a href="mailto:softwaresummit@ict.go.ke" style="color:#007bff; text-decoration:none;">softwaresummit@ict.go.ke</a>.
              </p>

              <p style="color:#333; font-size:14px; margin-bottom:20px;">
                We look forward to your participation and contribution to this year’s Summit.
              </p>

              <p style="color:#333; font-size:14px; margin-bottom:20px;">
                <strong>Karibu!</strong>
              </p>

              <p style="margin-top:30px; text-align:center;">
                Best regards,<br><strong>The Kenya Software & AI Summit Team</strong>
              </p>
            </div>

            <!-- CTA button -->
            <div style="margin:30px 0; text-align:center;">
              <a href="https://softwaresummit.go.ke/" 
                style="background-color:#007bff; color:#fff; padding:12px 25px; border-radius:4px; text-decoration:none; font-weight:bold; font-size:14px;">
                Complete Payment Now
              </a>
            </div>

            <!-- Footer outside card -->
            <footer style="text-align:center; font-size:12px; color:#888; margin-top:20px;">
              <p>&copy; {current_year} The Kenya Software & AI Summit.</p>
              <p>The Ministry of Information, Communications and The Digital Economy</p>
              <p>6th Floor, Bruce House, Standard Street</p>
              <p>Email: softwaresummit@ict.go.ke</p>
              <p>All rights reserved.</p>
            </footer>
          </body>
        </html>
        """

        # === Compose Email ===
        email = EmailMultiAlternatives(subject, plain_message, from_email, to)
        email.attach_alternative(html_message, "text/html")

        # qr_img_mime = MIMEImage(qr_buffer.getvalue(), _subtype="png")
        # qr_img_mime.add_header("Content-ID", "<qr_code>")
        # qr_img_mime.add_header("Content-Disposition", "inline", filename="qr.png")
        # email.attach(qr_img_mime)
        email.mixed_subtype = "related"

        # === Retry sending ===
        for attempt in range(1, retries + 1):
            attempt_count = attempt
            try:
                email.send(fail_silently=False)
                print(f"✅ Email sent successfully to {exhibitor.email} (attempt {attempt})")
                success = True
                break
            except Exception as send_error:
                error_message = str(send_error)
                print(f"⚠️ Attempt {attempt} failed: {error_message}")
                traceback.print_exc()
                if attempt < retries:
                    print(f"⏳ Retrying in {delay} seconds...")
                    time.sleep(delay)

    except Exception as e:
        error_message = f"Email preparation failed: {e}"
        traceback.print_exc()

    finally:
        # === Log outcome ===
        EmailLogs.objects.create(
            exhibitor=exhibitor,
            recipient=exhibitor.email,
            subject=subject,
            status="success" if success else "failed",
            error_message=error_message,
            attempts=attempt_count,
            sent_at=timezone.now(),
        )


# --------------------------------------------


def send_student_email(registrant, retries=3, delay=3):
    subject = "The Kenya Software & AI Summit Registration"
    from_email = "softwaresummit@ict.go.ke"
    to = [registrant.email]
    datetime.now().year
    error_message = None
    success = False
    attempt_count = 0

    try:
        # === Generate QR Code ===
        qr_data = (
            f"Name: {registrant.get_full_name()}\n"
            f"Email: {registrant.email}\n"
            f"Phone: {registrant.phone}\n"
            f"Organization: {registrant.display_org_type()}\n"
            f"Job Title: {registrant.job_title}"
        )
        qr_img = qrcode.make(qr_data)
        qr_buffer = BytesIO()
        qr_img.save(qr_buffer, format="PNG")

        # === Generate Barcode ===
        barcode_buffer = BytesIO()
        Code128(str(registrant.id), writer=ImageWriter()).write(barcode_buffer)

        # === HTML Body ===
        # === Plaintext Message ===

        plain_message = (
            f"Dear {registrant.title} {registrant.first_name} {registrant.second_name},\n\n"
            "Thank you for successfully registering for the Kenya Software & AI Summit 2025.\n\n"
            "Your registration has been received and is currently awaiting verification from your academic institution.\n"
            "Once your institution confirms your details, your participation will be officially approved.\n\n"
            "This year’s Kenya Software & AI Summit will be held from 10th November to 12th November 2025 at Moi University Annex Campus, "
            "Eldoret City, Uasin Gishu County, Kenya.\n\n"
            f"Your academic institution, {registrant.other_organization_type}, will confirm your attendance details.\n\n"
            "Theme: “Connecting Minds, Shaping Software, Driving Growth.”\n\n"
            "We appreciate your patience during this verification process.\n\n"
            "Best regards,\n"
            "The Kenya Software & AI Summit Team\n"
            "Ministry of Information, Communications and The Digital Economy\n"
            "Email: softwaresummit@ict.go.ke\n"
            "Website: https://softwaresummit.go.ke"
        )

        # === HTML Email Body ===
        html_message = f"""
        <html>
          <body style="font-family: Arial, sans-serif; background-color:#f4f6f9; padding:20px;">
            <div style="max-width:650px; margin:40px auto; background:#ffffff; border-radius:8px;
                        padding:30px; border:1px solid #e0e0e0;">

              <!-- Ministry Logo -->
              <div style="text-align:center; margin-bottom:20px;">
                <img src="https://Sylvester976.github.io/geoclock/static/images/banner-logo.png" 
                     alt="MINISTRY LOGO" style="height:70px;">
              </div>

              <!-- Summit Logo -->
              <div style="text-align:center; margin-bottom:20px;">
                <img src="https://Sylvester976.github.io/geoclock/static/images/summit_logo.png"
                     alt="Summit Logo" style="height:60px;">
              </div>

              <!-- Greeting -->
              <h2 style="color:#2c3e50; text-align:center; margin-bottom:10px;">
                Dear {registrant.title} {registrant.first_name} {registrant.second_name},
              </h2>

              <!-- Intro -->
              <p style="color:#333; font-size:14px; margin-bottom:20px;">
                Your registration has been received and is currently <strong>awaiting verification</strong> from your academic institution. 
                Once your details are confirmed, your participation will be officially approved.
              </p>

              <p style="color:#333; font-size:14px; margin-bottom:20px;">
                The summit will take place from <strong>10th – 12th November 2025</strong> at 
                <strong>Moi University Annex Campus</strong>, Eldoret City, 
                <strong>Uasin Gishu County, Kenya</strong>.
              </p>

              <p style="color:#333; font-size:14px; margin-bottom:20px;">
                <em>Theme:</em> <strong>“Connecting Minds, Shaping Software, Driving Growth.”</strong>
              </p>

              <p style="color:#333; font-size:14px; margin-bottom:20px;">
                Your academic institution, <strong>{registrant.other_organization_type}</strong>, will confirm your attendance details.
              </p>

              <p style="color:#333; font-size:14px; margin-bottom:20px;">
                We appreciate your patience as your registration is being verified.
              </p>

              <p style="margin-top:30px; text-align:center;">
                Best regards,<br>
                <strong>The Kenya Software & AI Summit Team</strong><br>
                Ministry of Information, Communications and The Digital Economy
              </p>
            </div>

            <!-- CTA button -->
            <div style="margin:30px 0; text-align:center;">
              <a href="https://softwaresummit.go.ke/" 
                style="background-color:#007bff; color:#fff; padding:12px 25px; border-radius:4px; text-decoration:none; font-weight:bold; font-size:14px;">
                Visit Summit Portal
              </a>
            </div>

            <!-- Footer -->
            <footer style="text-align:center; font-size:12px; color:#888; margin-top:20px;">
              <p>&copy; {datetime.now().year} The Kenya Software & AI Summit Team.</p>
              <p>The Ministry of Information, Communications and The Digital Economy</p>
              <p>6th Floor, Bruce House, Standard Street</p>
              <p>Email: softwaresummit@ict.go.ke</p>
              <p>All rights reserved.</p>
            </footer>
          </body>
        </html>
        """

        # === Compose Email ===
        email = EmailMultiAlternatives(subject, plain_message, from_email, to)
        email.attach_alternative(html_message, "text/html")

        # qr_img_mime = MIMEImage(qr_buffer.getvalue(), _subtype="png")
        # qr_img_mime.add_header("Content-ID", "<qr_code>")
        # qr_img_mime.add_header("Content-Disposition", "inline", filename="qr.png")
        # email.attach(qr_img_mime)
        email.mixed_subtype = "related"

        # === Retry sending ===
        for attempt in range(1, retries + 1):
            attempt_count = attempt
            try:
                email.send(fail_silently=False)
                print(f"✅ Email sent successfully to {registrant.email} (attempt {attempt})")
                success = True
                break
            except Exception as send_error:
                error_message = str(send_error)
                print(f"⚠️ Attempt {attempt} failed: {error_message}")
                traceback.print_exc()
                if attempt < retries:
                    print(f"⏳ Retrying in {delay} seconds...")
                    time.sleep(delay)

    except Exception as e:
        error_message = f"Email preparation failed: {e}"
        traceback.print_exc()

    finally:
        # === Log outcome ===
        EmailLog.objects.create(
            registrant=registrant,
            recipient=registrant.email,
            subject=subject,
            status="success" if success else "failed",
            error_message=error_message,
            attempts=attempt_count,
            sent_at=timezone.now(),
        )


def send_student_email_verify(registrant, retries=3, delay=3):
    subject = "Kenya Software & AI Summit Registration Successful"
    from_email = "softwaresummit@ict.go.ke"
    to = [registrant.email]
    datetime.now().year
    error_message = None
    success = False
    attempt_count = 0

    try:
        # === Generate QR Code ===
        qr_data = (
            f"Name: {registrant.get_full_name()}\n"
            f"Email: {registrant.email}\n"
            f"Phone: {registrant.phone}\n"
            f"Organization: {registrant.display_org_type()}\n"
            f"Job Title: {registrant.job_title}"
        )
        qr_img = qrcode.make(qr_data)
        qr_buffer = BytesIO()
        qr_img.save(qr_buffer, format="PNG")

        # === Generate Barcode ===
        barcode_buffer = BytesIO()
        Code128(str(registrant.id), writer=ImageWriter()).write(barcode_buffer)

        # === HTML Body ===
        # === Plaintext Message ===

        plain_message = (
            f"Dear {registrant.title} {registrant.first_name} {registrant.second_name},\n\n"
            "Congratulations! Your registration for the Kenya Software & AI Summit has been successfully received and approved.\n\n"
            "We are delighted to welcome you to this year’s Kenya Software & AI Summit, taking place from "
            "10th November to 12th November 2025 at Moi University Annex Campus, Eldoret City, "
            "Uasin Gishu County, Kenya.\n\n"
            "Theme: “Connecting Minds, Shaping Software, Driving Growth.”\n\n"
            "This year’s summit promises to be an inspiring and transformative experience for all participants.\n\n"
            "Karibu sana!\n\n"
            "Best regards,\n"
            "The Kenya Software & AI Summit Team\n"
            "Ministry of Information, Communications and The Digital Economy\n"
            "Email: softwaresummit@ict.go.ke\n"
            "Website: https://softwaresummit.go.ke"
        )

        # === HTML Email Body ===
        html_message = f"""
        <html>
          <body style="font-family: Arial, sans-serif; background-color:#f4f6f9; padding:20px;">
            <div style="max-width:650px; margin:40px auto; background:#ffffff; border-radius:8px;
                        padding:30px; border:1px solid #e0e0e0;">

              <!-- Ministry Logo -->
              <div style="text-align:center; margin-bottom:20px;">
                <img src="https://Sylvester976.github.io/geoclock/static/images/banner-logo.png" 
                     alt="MINISTRY LOGO" style="height:70px;">
              </div>

              <!-- Summit Logo -->
              <div style="text-align:center; margin-bottom:20px;">
                <img src="https://Sylvester976.github.io/geoclock/static/images/summit_logo.png"
                     alt="Summit Logo" style="height:60px;">
              </div>

              <!-- Greeting -->
              <h2 style="color:#2c3e50; text-align:center; margin-bottom:10px;">
                Dear {registrant.title} {registrant.first_name} {registrant.second_name},
              </h2>

              <!-- Intro -->
              <p style="color:#333; font-size:15px; text-align:center; margin-bottom:25px;">
                Congratulations! Your registration for the <strong>The Kenya Software & AI Summit 2025</strong> has been approved.
              </p>

              <p style="color:#333; font-size:14px; margin-bottom:20px;">
                We are thrilled to welcome you to this year’s Kenya Software & AI Summit, taking place from 
                <strong>10th – 12th November 2025</strong> at <strong>Moi University Annex Campus</strong>, 
                Eldoret City, <strong>Uasin Gishu County, Kenya</strong>.
              </p>

              <p style="color:#333; font-size:14px; margin-bottom:20px;">
                <em>Theme:</em> <strong>“Connecting Minds, Shaping Software, Driving Growth.”</strong>
              </p>

              <p style="color:#333; font-size:14px; margin-bottom:20px;">
                This year’s summit is tailored to spark collaboration, creativity, and technological innovation.
              </p>

              <p style="color:#333; font-size:14px; margin-bottom:20px;">
                <strong>Karibu sana!</strong>
              </p>

              <p style="margin-top:30px; text-align:center;">
                Best regards,<br>
                <strong>The Kenya Software & AI Summit Team</strong><br>
                Ministry of Information, Communications and The Digital Economy
              </p>
            </div>

            <!-- CTA button -->
            <div style="margin:30px 0; text-align:center;">
              <a href="https://softwaresummit.go.ke/" 
                style="background-color:#007bff; color:#fff; padding:12px 25px; border-radius:4px; text-decoration:none; font-weight:bold; font-size:14px;">
                Visit Summit Portal
              </a>
            </div>

            <!-- Footer -->
            <footer style="text-align:center; font-size:12px; color:#888; margin-top:20px;">
              <p>&copy; {datetime.now().year} Kenya Software & AI Summit.</p>
              <p>The Ministry of Information, Communications and The Digital Economy</p>
              <p>6th Floor, Bruce House, Standard Street</p>
              <p>Email: softwaresummit@ict.go.ke</p>
              <p>All rights reserved.</p>
            </footer>
          </body>
        </html>
        """

        # === Compose Email ===
        email = EmailMultiAlternatives(subject, plain_message, from_email, to)
        email.attach_alternative(html_message, "text/html")

        # qr_img_mime = MIMEImage(qr_buffer.getvalue(), _subtype="png")
        # qr_img_mime.add_header("Content-ID", "<qr_code>")
        # qr_img_mime.add_header("Content-Disposition", "inline", filename="qr.png")
        # email.attach(qr_img_mime)
        email.mixed_subtype = "related"

        # === Retry sending ===
        for attempt in range(1, retries + 1):
            attempt_count = attempt
            try:
                email.send(fail_silently=False)
                print(f"✅ Email sent successfully to {registrant.email} (attempt {attempt})")
                success = True
                break
            except Exception as send_error:
                error_message = str(send_error)
                print(f"⚠️ Attempt {attempt} failed: {error_message}")
                traceback.print_exc()
                if attempt < retries:
                    print(f"⏳ Retrying in {delay} seconds...")
                    time.sleep(delay)

    except Exception as e:
        error_message = f"Email preparation failed: {e}"
        traceback.print_exc()

    finally:
        # === Log outcome ===
        EmailLog.objects.create(
            registrant=registrant,
            recipient=registrant.email,
            subject=subject,
            status="success" if success else "failed",
            error_message=error_message,
            attempts=attempt_count,
            sent_at=timezone.now(),
        )


# --------------------------------------------
# Registrants
def send_protocol_confirmation_email(registrant, retries=3, delay=3):
    subject = "The Kenya Software & AI Summit Registration"
    from_email = "softwaresummit@ict.go.ke"
    to = [registrant.email]
    current_year = datetime.now().year
    error_message = None
    success = False
    attempt_count = 0

    try:
        # === Generate QR Code ===
        qr_data = (
            f"Name: {registrant.get_full_name()}\n"
            f"Email: {registrant.email}\n"
            f"Phone: {registrant.phone}\n"
            f"Organization: {registrant.display_org_type()}\n"
            f"Job Title: {registrant.job_title}"
        )
        qr_img = qrcode.make(qr_data)
        qr_buffer = BytesIO()
        qr_img.save(qr_buffer, format="PNG")

        # === Generate Barcode ===
        barcode_buffer = BytesIO()
        Code128(str(registrant.id), writer=ImageWriter()).write(barcode_buffer)

        # === HTML Body ===
        # === Plaintext Message ===

        plain_message = (
            f"Welcome {registrant.title} {registrant.first_name} {registrant.second_name},\n\n"
            "Thank you for successfully registering for the Kenya Software & AI Summit 2025.\n\n"
            "We are delighted to welcome you to this year’s Kenya Software & AI Summit, taking place from "
            "10th November - 12th November , 2025 at Eldoret Moi University  Annex campus, Eldoret City, Uasin Gishu County, Kenya.\n\n"
            "The theme for this year is: “Connecting Minds, Shaping Software, Driving Growth.”\n\n"
            f"Upon your arrival in Eldoret, our team will receive you and confirm your <strong> {registrant.get_category_display()} </strong> status. "
            "To facilitate this, kindly carry a valid identification document. "
            f"You will then be issued with a badge, the <strong> {registrant.get_category_display()} </strong> pack containing your conference guide, "
            "and the full programme to help you easily navigate the conference activities.\n\n"
            "This experience has been thoughtfully tailored to meet your innovative needs and standards.\n\n"
            "Karibu.\n\n"
            "Best regards,\nThe Kenya Software & AI Summit Team"
        )

        # === HTML Email Body ===
        html_message = f"""
        <html>
          <body style="font-family: Arial, sans-serif; background-color:#f4f6f9; padding:20px;">
            <div style="max-width:650px; margin:40px auto; background:#ffffff; border-radius:8px;
                        padding:30px; border:1px solid #e0e0e0;">

              <!-- Ministry Logo -->
              <div style="text-align:center; margin-bottom:20px;">
                <img src="https://Sylvester976.github.io/geoclock/static/images/banner-logo.png" alt="MINISTRY LOGO" style="height:70px;">
              </div>

              <!-- Summit Logo -->
              <div style="text-align:center; margin-bottom:20px;">
                <img src="https://Sylvester976.github.io/geoclock/static/images/summit_logo.png"
                     alt="Summit Logo" style="height:60px;">
              </div>

              <!-- Greeting -->
              <h2 style="color:#2c3e50; text-align:center; margin-bottom:10px;">
                Welcome {registrant.title} {registrant.first_name} {registrant.second_name},
              </h2>

              <!-- Intro -->
              <p style="color:#333; font-size:15px; text-align:center; margin-bottom:25px;">
                Thank you for successfully registering for the <strong>The Kenya Software & AI Summit 2025</strong>.
              </p>

              <p style="color:#333; font-size:14px; margin-bottom:20px;">
                We are delighted to welcome you to this year’s Kenya Software & AI Summit, taking place from 
                10th November -12th November , 2025 at Eldoret Moi University  Annex campus, <strong>Eldoret City, Uasin Gishu County, Kenya</strong>.
              </p>

              <p style="color:#333; font-size:14px; margin-bottom:20px;">
                <em>Theme:</em> <strong>“Connecting Minds, Shaping Software, Driving Growth”</strong>
              </p>

              <p style="color:#333; font-size:14px; margin-bottom:20px;">
                Upon your arrival in Eldoret, our team will receive you and confirm your <strong> {registrant.get_category_display()} </strong> status. 
                To facilitate this, kindly carry a valid identification document. You will then receive 
                a badge, the <strong> {registrant.get_category_display()} </strong> pack containing your conference guide, and the programme for 
                easier navigation of the conference activities.
              </p>

              <p style="color:#333; font-size:14px; margin-bottom:20px;">
                This experience has been thoughtfully tailored to meet your innovative needs and standards.
              </p>

              <p style="color:#333; font-size:14px; margin-bottom:20px;">
                <strong>Karibu!</strong>
              </p>

              <p style="margin-top:30px; text-align:center;">
                Best regards,<br><strong>The Kenya Software & AI Summit Team</strong>
              </p>
            </div>

            <!-- CTA button -->
            <div style="margin:30px 0; text-align:center;">
              <a href="https://softwaresummit.go.ke/" 
                style="background-color:#007bff; color:#fff; padding:12px 25px; border-radius:4px; text-decoration:none; font-weight:bold; font-size:14px;">
                Visit Summit Portal
              </a>
            </div>

            <!-- Footer outside card -->
            <footer style="text-align:center; font-size:12px; color:#888; margin-top:20px;">
              <p>&copy; {current_year} The Kenya Software & AI Summit.</p>
              <p>The Ministry of Information, Communications and The Digital Economy</p>
              <p>6th Floor, Bruce House, Standard Street</p>
              <p>Email: softwaresummit@ict.go.ke</p>
              <p>All rights reserved.</p>
            </footer>
          </body>
        </html>
        """

        # === Compose Email ===
        email = EmailMultiAlternatives(subject, plain_message, from_email, to)
        email.attach_alternative(html_message, "text/html")

        # qr_img_mime = MIMEImage(qr_buffer.getvalue(), _subtype="png")
        # qr_img_mime.add_header("Content-ID", "<qr_code>")
        # qr_img_mime.add_header("Content-Disposition", "inline", filename="qr.png")
        # email.attach(qr_img_mime)
        email.mixed_subtype = "related"

        # === Retry sending ===
        for attempt in range(1, retries + 1):
            attempt_count = attempt
            try:
                email.send(fail_silently=False)
                print(f"✅ Email sent successfully to {registrant.email} (attempt {attempt})")
                success = True
                break
            except Exception as send_error:
                error_message = str(send_error)
                print(f"⚠️ Attempt {attempt} failed: {error_message}")
                traceback.print_exc()
                if attempt < retries:
                    print(f"⏳ Retrying in {delay} seconds...")
                    time.sleep(delay)

    except Exception as e:
        error_message = f"Email preparation failed: {e}"
        traceback.print_exc()

    finally:
        # === Log outcome ===
        EmailLog.objects.create(
            registrant=registrant,
            recipient=registrant.email,
            subject=subject,
            status="success" if success else "failed",
            error_message=error_message,
            attempts=attempt_count,
            sent_at=timezone.now(),
        )


def generate_strong_password(length=8):
    """
    Generates a strong 8-character random password with uppercase,
    lowercase, digits, and special characters.
    """
    if length < 8:
        raise ValueError("Password length should be at least 8 characters.")

    # Character sets
    letters = string.ascii_letters  # A-Z + a-z
    digits = string.digits  # 0-9
    symbols = "!@#$%^&*()-_=+[]{};:,.<>?"

    # Ensure at least one of each
    all_chars = letters + digits + symbols
    password = [
        secrets.choice(string.ascii_uppercase),
        secrets.choice(string.ascii_lowercase),
        secrets.choice(digits),
        secrets.choice(symbols),
    ]

    # Fill the rest randomly
    password += [secrets.choice(all_chars) for _ in range(length - 4)]

    # Shuffle to mix
    secrets.SystemRandom().shuffle(password)

    return "".join(password)


# Exhibitor
def send_confirmation_booth_confirmation_mail(exhibitor, retries=3, delay=3):
    subject = "The Kenya Software & AI Summit Registration"
    from_email = "softwaresummit@ict.go.ke"
    to = [exhibitor.email]
    current_year = datetime.now().year
    error_message = None
    success = False
    attempt_count = 0

    try:
        # === Generate QR Code ===
        qr_data = (
            f"Name: {exhibitor.get_full_name()}\n"
            f"Email: {exhibitor.email}\n"
            f"Phone: {exhibitor.phone}\n"
            f"Organization: {exhibitor.organization_type}\n"
            f"Job Title: {exhibitor.job_title}"
        )
        qr_img = qrcode.make(qr_data)
        qr_buffer = BytesIO()
        qr_img.save(qr_buffer, format="PNG")

        # === Generate Barcode ===
        barcode_buffer = BytesIO()
        Code128(str(exhibitor.id), writer=ImageWriter()).write(barcode_buffer)

        # === HTML Body ===
        # === Plaintext Message ===
        plain_message = (
            f"Congratulations {exhibitor.title} {exhibitor.first_name} {exhibitor.second_name},\n\n"
            "We are pleased to confirm that your payment has been received successfully and your exhibitor booth booking is now complete.\n\n"
            f"You have been officially allocated {exhibitor.total_count} booth(s) for the Kenya Software & AI Summit 2025, "
            "taking place from 10th November - 12th November, 2025 at Moi University Annex Campus, Eldoret City, "
            "Uasin Gishu County, Kenya.\n\n"
            "Theme: “Connecting Minds, Shaping Software, Driving Growth.”\n\n"
            "You will receive your exhibitor badge, booth access credentials, and an exhibitor’s pack containing your conference guide "
            "and full event programme.\n\n"
            "Thank you for being part of this transformative summit. We look forward to showcasing your innovations and contributions "
            "to Kenya’s growing digital and software ecosystem.\n\n"
            "Karibu sana!\n\n"
            "Best regards,\nThe Kenya Software & AI Summit Team"
        )

        # === HTML Email Body ===
        html_message = f"""
        <html>
          <body style="font-family: Arial, sans-serif; background-color:#f4f6f9; padding:20px;">
            <div style="max-width:650px; margin:40px auto; background:#ffffff; border-radius:8px;
                        padding:30px; border:1px solid #e0e0e0;">

              <!-- Ministry Logo -->
              <div style="text-align:center; margin-bottom:20px;">
                <img src="https://Sylvester976.github.io/geoclock/static/images/banner-logo.png" alt="MINISTRY LOGO" style="height:70px;">
              </div>

              <!-- Summit Logo -->
              <div style="text-align:center; margin-bottom:20px;">
                <img src="https://Sylvester976.github.io/geoclock/static/images/summit_logo.png"
                     alt="Summit Logo" style="height:60px;">
              </div>

              <!-- Greeting -->
              <h2 style="color:#2c3e50; text-align:center; margin-bottom:10px;">
                Congratulations {exhibitor.title} {exhibitor.first_name} {exhibitor.second_name},
              </h2>

              <!-- Intro -->
              <p style="color:#333; font-size:15px; text-align:center; margin-bottom:25px;">
                We are pleased to confirm that your payment has been received successfully and your exhibitor booth booking is now complete!
              </p>

              <p style="color:#333; font-size:14px; margin-bottom:20px;">
                You have been officially allocated <strong>{exhibitor.total_count}</strong> booth(s) for the upcoming 
                <strong>Kenya Software & AI Summit 2025</strong>, taking place from 
                <strong>10th – 12th November 2025</strong> at 
                <strong>Moi University Annex Campus, Eldoret City, Uasin Gishu County, Kenya</strong>.
              </p>

              <p style="color:#333; font-size:14px; margin-bottom:20px;">
                <em>Theme:</em> <strong>“Connecting Minds, Shaping Software, Driving Growth”</strong>
              </p>

              <p style="color:#333; font-size:14px; margin-bottom:20px;">You will receive your exhibitor badge, booth access credentials, and an exhibitor’s pack containing 
                your conference guide and full event programme.
              </p>

              <p style="color:#333; font-size:14px; margin-bottom:20px;">
                Thank you for being part of this transformative summit. We look forward to showcasing your innovations 
                and contributions to Kenya’s growing digital and software ecosystem.
              </p>

              <p style="color:#333; font-size:14px; margin-bottom:20px;">
                <strong>Karibu sana!</strong>
              </p>

              <p style="margin-top:30px; text-align:center;">
                Best regards,<br><strong>The Kenya Software & AI Summit Team</strong>
              </p>
            </div>

            <!-- CTA button -->
            <div style="margin:30px 0; text-align:center;">
              <a href="https://softwaresummit.go.ke/" 
                style="background-color:#007bff; color:#fff; padding:12px 25px; border-radius:4px; text-decoration:none; font-weight:bold; font-size:14px;">
                Visit Summit Portal
              </a>
            </div>

            <!-- Footer outside card -->
            <footer style="text-align:center; font-size:12px; color:#888; margin-top:20px;">
              <p>&copy; {current_year} The Kenya Software & AI Summit.</p>
              <p>The Ministry of Information, Communications and The Digital Economy</p>
              <p>6th Floor, Bruce House, Standard Street</p>
              <p>Email: softwaresummit@ict.go.ke</p>
              <p>All rights reserved.</p>
            </footer>
          </body>
        </html>
        """

        # === Compose Email ===
        email = EmailMultiAlternatives(subject, plain_message, from_email, to)
        email.attach_alternative(html_message, "text/html")

        # qr_img_mime = MIMEImage(qr_buffer.getvalue(), _subtype="png")
        # qr_img_mime.add_header("Content-ID", "<qr_code>")
        # qr_img_mime.add_header("Content-Disposition", "inline", filename="qr.png")
        # email.attach(qr_img_mime)
        email.mixed_subtype = "related"

        # === Retry sending ===
        for attempt in range(1, retries + 1):
            attempt_count = attempt
            try:
                email.send(fail_silently=False)
                print(f"✅ Email sent successfully to {exhibitor.email} (attempt {attempt})")
                success = True
                break
            except Exception as send_error:
                error_message = str(send_error)
                print(f"⚠️ Attempt {attempt} failed: {error_message}")
                traceback.print_exc()
                if attempt < retries:
                    print(f"⏳ Retrying in {delay} seconds...")
                    time.sleep(delay)

    except Exception as e:
        error_message = f"Email preparation failed: {e}"
        traceback.print_exc()

    finally:
        # === Log outcome ===
        EmailLogs.objects.create(
            exhibitor=exhibitor,
            recipient=exhibitor.email,
            subject=subject,
            status="success" if success else "failed",
            error_message=error_message,
            attempts=attempt_count,
            sent_at=timezone.now(),
        )
