import os

from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.contrib.auth.views import LogoutView
from django.contrib.staticfiles import finders
from django.core.paginator import Paginator
from django.db.models import Count
from django.db.models.functions import TruncDate
from django.forms import inlineformset_factory
from django.http import FileResponse, Http404
from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.templatetags.static import static
from django.utils.timezone import now
from django.views.decorators.http import require_POST
from openpyxl import Workbook
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.pagesizes import landscape, A7
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas
from reportlab.platypus import (
    PageBreak
)
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph,
    Image, Spacer
)
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .decorators import require_api_key
from .forms import GalleryForm, QuickRegistrationForm, RegistrantForm, ScheduleDayForm, TimeSlotForm, SessionForm, \
    PanelistForm, SpeakerForm
from .models import *
from .serializers_new import serialize_registrant
from .utils import *

PanelistFormSet = inlineformset_factory(
    SummitSession, SummitPanelist, form=PanelistForm, extra=1, can_delete=True
)



from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import messages
from .models import Registrant, SummitGallery, SummitPartner, SummitScheduleDay
from .forms import QuickRegistrationForm
from .utils import send_confirmation_email  # assuming this is your helper

def home(request):

    if request.method == 'POST':
        form = QuickRegistrationForm(request.POST, request.FILES)

        if form.is_valid():
            registrant = form.save(commit=False)

            # ✅ Explicitly assign file fields
            if request.FILES.get("passport_photo"):
                registrant.passport_photo = request.FILES["passport_photo"]
            if request.FILES.get("national_id_scan"):
                registrant.national_id_scan = request.FILES["national_id_scan"]

            # Interests handling
            interests = form.cleaned_data.get("interests", [])
            other_interest = form.cleaned_data.get("other_interest")
            if "others" in interests and other_interest:
                registrant.other_interest = other_interest
            registrant.interests = interests

            registrant.save()

            # Send confirmation email
            try:
                send_confirmation_email(registrant)
            except Exception as e:
                print("Email Send error:", e)
                if request.headers.get("x-requested-with") == "XMLHttpRequest":
                    return JsonResponse(
                        {"success": True, "message": "Registration saved, but email failed."},
                        status=200
                    )
                messages.warning(request, "Registered, but confirmation email failed.")

            if request.headers.get("x-requested-with") == "XMLHttpRequest":
                return JsonResponse({"success": True, "message": "Registration successful!"})

            messages.success(request, "Registration successful!")
            return redirect('home')

        else:
            if request.headers.get("x-requested-with") == "XMLHttpRequest":
                return JsonResponse({"success": False, "errors": form.errors}, status=400)

            messages.error(request, "There was a problem with your registration.")

    else:
        form = QuickRegistrationForm()

    days = SummitScheduleDay.objects.prefetch_related(
        "timeslots__sessions__panelists"
    ).order_by("date")

    gallery_items = SummitGallery.objects.filter(is_active=True).order_by('order')
    partners = SummitPartner.objects.filter(is_active=True).order_by("order")

    return render(request, "summit/home.html", {
        'form': form,
        'gallery_items': gallery_items,
        'partners': partners,
        'days': days,
        'interest_choices': Registrant.INTEREST_CHOICES,
    })


def reg(request):
    if request.method == 'POST':
        form = QuickRegistrationForm(request.POST, request.FILES)

        if form.is_valid():
            registrant = form.save(commit=False)

            # ✅ Explicitly assign file fields
            if request.FILES.get("passport_photo"):
                registrant.passport_photo = request.FILES["passport_photo"]
            if request.FILES.get("national_id_scan"):
                registrant.national_id_scan = request.FILES["national_id_scan"]

            # Interests handling
            interests = form.cleaned_data.get("interests", [])
            other_interest = form.cleaned_data.get("other_interest")
            if "others" in interests and other_interest:
                registrant.other_interest = other_interest
            registrant.interests = interests

            registrant.save()

            # Send confirmation email
            try:
                send_confirmation_email(registrant)
            except Exception as e:
                print("Email Send error:", e)
                if request.headers.get("x-requested-with") == "XMLHttpRequest":
                    return JsonResponse(
                        {"success": True, "message": "Registration saved, but email failed."},
                        status=200
                    )
                messages.warning(request, "Registered, but confirmation email failed.")

            if request.headers.get("x-requested-with") == "XMLHttpRequest":
                return JsonResponse({"success": True, "message": "Registration successful!"})

            messages.success(request, "Registration successful!")
            return redirect('home')

        else:
            if request.headers.get("x-requested-with") == "XMLHttpRequest":
                return JsonResponse({"success": False, "errors": form.errors}, status=400)

            messages.error(request, "There was a problem with your registration.")

    else:
        form = QuickRegistrationForm()

    days = SummitScheduleDay.objects.prefetch_related("timeslots__sessions__panelists").order_by("date")
    gallery_items = SummitGallery.objects.filter(is_active=True).order_by('order')
    partners = SummitPartner.objects.filter(is_active=True).order_by("order")

    return render(request, "summit/reg.html", {
        'form': form,
        'gallery_items': gallery_items,
        'partners': partners,
        'days': days,
        'interest_choices': Registrant.INTEREST_CHOICES,
    })


import qrcode
from io import BytesIO
from django.http import FileResponse, Http404
from django.contrib.admin.views.decorators import staff_member_required
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A7, portrait
from reportlab.lib.utils import ImageReader
from reportlab.lib import colors
from django.conf import settings
from .models import Registrant
import os


def _fit_text(c, text, max_width, start_font_size=9, font_name="Helvetica-Bold"):
    """Dynamically adjust font size so text fits within the given width."""
    font_size = start_font_size
    while c.stringWidth(text, font_name, font_size) > max_width and font_size > 5:
        font_size -= 0.5
    return font_size


@staff_member_required
def generate_badge(request, registrant_id):
    try:
        registrant = Registrant.objects.get(pk=registrant_id)
    except Registrant.DoesNotExist:
        raise Http404("Registrant not found")

    # --- Data ---
    full_name = registrant.get_full_name() or ""
    org_type = registrant.display_org_type() or ""
    job_title = registrant.job_title or ""
    interests = registrant.display_interests() or ""

    # --- Generate QR Code ---
    qr_data = (
        f"Name: {full_name}\n"
        f"Organization: {org_type}\n"
        f"Job Title: {job_title}\n"
        f"Interests: {interests}"
    )
    qr_img = qrcode.make(qr_data)
    qr_buffer = BytesIO()
    qr_img.save(qr_buffer, format="PNG")
    qr_buffer.seek(0)

    # --- PDF Setup ---
    pdf_buffer = BytesIO()
    c = canvas.Canvas(pdf_buffer, pagesize=portrait(A7))
    width, height = portrait(A7)

    # --- Colors ---
    accent_color = colors.HexColor("#004aad")  # deep blue accent
    light_accent = colors.HexColor("#e6ecf7")  # soft blue-grey

    # --- Background ---
    c.setFillColor(light_accent)
    c.rect(0, 0, width, height, fill=1, stroke=0)
    c.setFillColor(colors.white)
    c.roundRect(6, 6, width - 12, height - 12, 10, fill=1, stroke=0)

    # --- Header ---
    header_h = 32
    header_y = height - header_h - 6
    c.setFillColor(colors.white)
    c.roundRect(6, header_y, width - 12, header_h, 8, fill=1, stroke=0)

    # --- Logo with white background ---
    logo_path = os.path.join(settings.BASE_DIR, "static", "images", "summit_logo_dark.webp")
    if os.path.exists(logo_path):
        logo = ImageReader(logo_path)
        logo_w, logo_h = 80, 34  # increased size
        logo_x = (width - logo_w) / 2
        logo_y = header_y + (header_h - logo_h) / 2 - 3

        # white background box for logo
        # c.setFillColor(colors.white)
        # c.roundRect(logo_x - 4, logo_y - 2, logo_w + 8, logo_h + 4, 4, fill=1, stroke=0)

        c.drawImage(
            logo,
            logo_x,
            logo_y,
            width=logo_w,
            height=logo_h,
            preserveAspectRatio=True,
            mask="auto",
        )

    # --- Summit Title ---
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 8.5)
    c.drawCentredString(width / 2, header_y - 9, "Kenya Software Summit 2025")

    # --- Passport Photo ---
    photo_w, photo_h = 60, 60
    photo_x = (width - photo_w) / 2
    photo_y = header_y - photo_h - 20

    c.setFillColor(light_accent)
    c.roundRect(photo_x - 3, photo_y - 3, photo_w + 6, photo_h + 6, 8, fill=1, stroke=0)

    def draw_placeholder():
        c.setFillColor(colors.lightgrey)
        c.roundRect(photo_x, photo_y, photo_w, photo_h, 6, fill=1, stroke=0)
        c.setFillColor(colors.darkgrey)
        c.setFont("Helvetica", 7)
        c.drawCentredString(width / 2, photo_y + photo_h / 2 - 3, "No Photo")

    if registrant.passport_photo:
        photo_path = os.path.join(settings.MEDIA_ROOT, registrant.passport_photo.name)
        if os.path.exists(photo_path):
            c.drawImage(
                photo_path,
                photo_x,
                photo_y,
                width=photo_w,
                height=photo_h,
                preserveAspectRatio=True,
                mask="auto",
            )
        else:
            draw_placeholder()
    else:
        draw_placeholder()

    # --- Registrant Info ---
    info_y = photo_y - 12
    c.setFillColor(colors.black)

    # Full Name
    name_font_size = _fit_text(c, full_name, width - 20, 10)
    c.setFont("Helvetica-Bold", name_font_size)
    c.drawCentredString(width / 2, info_y, full_name[:40])

    # Job Title
    c.setFillColor(colors.darkgray)
    c.setFont("Helvetica", 8)
    c.drawCentredString(width / 2, info_y - 11, job_title[:45])

    # Organization
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 8)
    c.drawCentredString(width / 2, info_y - 21, org_type[:45])

    # Interests
    if interests:
        c.setFont("Helvetica-Oblique", 7)
        c.setFillColor(colors.gray)
        c.drawCentredString(
            width / 2,
            info_y - 31,
            interests[:55] + ("..." if len(interests) > 55 else ""),
        )

    # --- QR Code ---
    qr_size = 52
    qr_x = (width - qr_size) / 2
    qr_y = info_y - 33 - qr_size + 1  # adjusted upward (removed bottom gap)
    qr_img_reader = ImageReader(qr_buffer)
    c.drawImage(qr_img_reader, qr_x, qr_y, width=qr_size, height=qr_size, mask="auto")

    # --- Footer ---
    c.setStrokeColor(accent_color)
    c.setLineWidth(0.8)
    c.line(12, qr_y - 3, width - 12, qr_y - 3)

    c.setFillColor(colors.grey)
    c.setFont("Helvetica-Oblique", 6.3)
    c.drawCentredString(width / 2, qr_y - 10, "Scan QR for Summit Check-in")

    # --- Finalize ---
    c.showPage()
    c.save()
    pdf_buffer.seek(0)

    filename = f"{registrant.first_name}_{registrant.second_name}_Badge.pdf"
    return FileResponse(pdf_buffer, as_attachment=True, filename=filename)



@staff_member_required
def unsubscribe_view(request, token):
    try:
        registrant = Registrant.objects.get(unsubscribe_token=token)
        registrant.updates_opt_in = False
        registrant.save()
        return render(request, "summit/unsubscribe.html")
    except Registrant.DoesNotExist:
        return HttpResponse("<h2>Invalid unsubscribe link.</h2>", status=400)


@staff_member_required
@api_view(['GET'])
def dashboard_stats(request):
    total = Registrant.objects.count()

    # Participation categories (pie chart)
    categories = Registrant.objects.values('category').annotate(count=Count('id'))

    # Interests breakdown (bar chart)
    # Flatten interests since they’re stored in JSON list
    interest_counts = {}
    for r in Registrant.objects.exclude(interests=[]):
        for i in r.interests:
            interest_counts[i] = interest_counts.get(i, 0) + 1

    # Registrations over time (line chart)
    daily = (
        Registrant.objects.annotate(date=TruncDate('created_at'))
        .values('date')
        .annotate(count=Count('id'))
        .order_by('date')
    )

    # Opt-in % for updates
    updates_opt_in = Registrant.objects.filter(updates_opt_in=True).count()
    updates_percent = (updates_opt_in / total * 100) if total else 0

    return Response({
        "total": total,
        "categories": list(categories),
        "interests": interest_counts,
        "registrations_over_time": list(daily),
        "updates_percent": updates_percent,
    })


# === Excel Export ===
@staff_member_required
def export_registrants_excel(request):
    wb = Workbook()
    ws = wb.active
    ws.title = "Registrants"

    # Header row
    headers = [
        "Full Name", "Email", "Phone", "Organization",
        "Job Title", "Category", "Interests", "Subscribed", "Registered On"
    ]
    ws.append(headers)

    for r in Registrant.objects.all():
        ws.append([
            r.full_name,
            r.email,
            r.phone,
            r.organization or "—",
            r.job_title or "—",
            r.get_category_display(),
            ", ".join(r.interests) if r.interests else "—",
            "Yes" if r.updates_opt_in else "No",
            r.created_at.strftime("%Y-%m-%d %H:%M"),
        ])

    response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response["Content-Disposition"] = 'attachment; filename="registrants.xlsx"'
    wb.save(response)
    return response


# === PDF Export in Landscape ===
# === PDF Export in Landscape with Logo, Header & Footer ===

@staff_member_required
def export_registrants_pdf(request):
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="registrants.pdf"'

    # Landscape A4
    doc = SimpleDocTemplate(
        response,
        pagesize=landscape(A4),
        rightMargin=20,
        leftMargin=20,
        topMargin=20,
        bottomMargin=40,  # leave room for footer
    )
    elements = []
    styles = getSampleStyleSheet()
    normal_style = styles["Normal"]

    # === Logo ===
    logo_path = os.path.join(settings.BASE_DIR, "static", "img", "logo.png")
    if os.path.exists(logo_path):
        logo = Image(logo_path, width=80, height=80)
        elements.append(logo)

    elements.append(Spacer(1, 10))

    # === Header ===
    elements.append(Paragraph("<b>Kenya Software Summit</b>", styles["Title"]))
    elements.append(Paragraph("Summit Registrants Report", styles["Heading2"]))
    elements.append(Spacer(1, 20))

    # === Table headers ===
    data = [[
        "No.", "Full Name", "Email", "Phone", "Organization",
        "Job Title", "Category", "Interests"
    ]]

    # === Table rows ===
    for idx, r in enumerate(Registrant.objects.all(), start=1):
        data.append([
            idx,
            Paragraph(r.full_name, normal_style),
            Paragraph(r.email, normal_style),
            Paragraph(r.phone, normal_style),
            Paragraph(r.organization or "—", normal_style),
            Paragraph(r.job_title or "—", normal_style),
            Paragraph(r.get_category_display(), normal_style),
            Paragraph(", ".join(r.interests) if r.interests else "—", normal_style),
        ])

    # === Column widths (landscape) ===
    col_widths = [30, 120, 130, 80, 120, 100, 90, 160]

    # === Table ===
    table = Table(data, colWidths=col_widths, repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#01873F")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("WORDWRAP", (0, 0), (-1, -1), "CJK"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
    ]))
    elements.append(table)

    # === Footer function ===
    def add_footer(canvas, doc):
        canvas.saveState()
        footer_text = f"Generated on {now().strftime('%b %d, %Y %H:%M')} | Kenya Software Summit © 2025"
        canvas.setFont("Helvetica", 8)
        canvas.drawCentredString(landscape(A4)[0] / 2, 20, footer_text)
        canvas.restoreState()

    # === Build PDF with footer on every page ===
    doc.build(elements, onFirstPage=add_footer, onLaterPages=add_footer)

    return response


@staff_member_required
def print_registrants(request):
    registrants = Registrant.objects.all().order_by("created_at")

    # Build merged org_type counts manually (instead of raw DB field)
    org_type_counts = {}
    for reg in registrants:
        label = reg.display_org_type()
        org_type_counts[label] = org_type_counts.get(label, 0) + 1

    return render(request, "summit/print_registrants.html", {
        "registrants": registrants,
        "org_type_counts": org_type_counts.items(),
    })

from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from django.db.models import Count, Max

@staff_member_required
def dashboard_view(request):
    total_users = Registrant.objects.count()
    updates_count = Registrant.objects.filter(updates_opt_in=True).count()

    # Annotate registrants with email log info
    registrants = Registrant.objects.all().order_by('-created_at').annotate(
        email_attempts=Count('emaillog'),
        email_status=Max('emaillog__status'),
        email_last_sent=Max('emaillog__sent_at')
    )

    context = {
        "total_users": total_users,
        "updates_count": updates_count,
        "registrants": registrants,
        "org_type_choices": Registrant.ORG_TYPE_CHOICES,  # send choices to template
    }
    return render(request, "summit/dashboard.html", context)


# Endpoint for charts (AJAX/React)
@staff_member_required
def dashboard_data(request):
    data = {
        "categories": list(
            Registrant.objects.values("category").annotate(count=Count("id")).order_by("category")
        ),
        "registrations_over_time": list(
            Registrant.objects.extra({"date": "date(created_at)"})
            .values("date")
            .annotate(count=Count("id"))
            .order_by("date")
        ),
        "updates_count": Registrant.objects.filter(updates_opt_in=True).count(),
    }
    return JsonResponse(data)


class SummitLoginView(LoginView):
    template_name = "summit/login.html"


class SummitLogoutView(LogoutView):
    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)


@staff_member_required
def about(request):
    return render(request, 'summit/samples/about.html')


def index(request):
    return render(request, 'summit/index.html')


@staff_member_required
@require_POST
def delete_registrant(request, pk):
    print(f"Method: {request.method}, PK: {pk}")  # ← Debug log
    try:
        registrant = Registrant.objects.get(pk=pk)
        registrant.delete()
        return JsonResponse({"success": True})
    except Registrant.DoesNotExist:
        return JsonResponse({"success": False, "error": "Registrant not found"}, status=404)
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=400)


def privacy(request):
    return render(request, "summit/privacy.html")


def not_found(request):
    return render(request, "summit/404.html")


def mailme_view(request):
    emails = Registrant.objects.values_list('email', flat=True)
    return render(request, "summit/mailme.html", {"emails": emails})


def speakers(request):
    speakers = SummitSpeaker.objects.all()
    return render(request, "summit/speakers.html", {"speakers": speakers})


def media(request):
    return render(request, "summit/gallery.html")


# ---------------------------

def register(request):
    if request.method == "POST":
        form = RegistrantForm(request.POST)

        # 🔹 AJAX request → return JSON
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            if form.is_valid():
                form.save()
                return JsonResponse({
                    "success": True,
                    "message": "Registration successful! Thank you for registering."
                })
            else:
                # Build errors dict: { field: [errors] }
                errors = {
                    field: [str(err) for err in errs]
                    for field, errs in form.errors.items()
                }
                return JsonResponse({
                    "success": False,
                    "errors": errors
                })

        # 🔹 Non-AJAX fallback
        if form.is_valid():
            form.save()
            messages.success(request, " Registration successful! Thank you for registering.")
            return redirect("register")
        else:
            messages.error(request, "⚠️ Please correct the errors below and try again.")
    else:
        form = RegistrantForm()

    return render(request, "summit/buy-tickets.html", {"form": form})


def sendMail(request):
    if request.method == "POST":
        subject = request.POST.get("subject")
        message = request.POST.get("message")
        emails = request.POST.getlist("recipient_emails")

        # Case 1: If getlist() found nothing (maybe input is a text field)
        if not emails:
            emails = request.POST.get("recipient_emails")

        # Case 2: Handle "all"
        if emails == "all" or (isinstance(emails, list) and "all" in emails):
            emails = list(Registrant.objects.values_list('email', flat=True))

        # Case 3: If it's a string, split it into a list (comma-separated)
        elif isinstance(emails, str):
            emails = [e.strip() for e in emails.split(",") if e.strip()]

        # Case 4: Clean up any list input
        else:
            emails = [e.strip() for e in emails if e.strip()]

        try:
            # Send to all recipients in one go
            sendmailer(subject, message, emails)

            return JsonResponse({
                'status': 'success',
                'message': f'Email(s) sent successfully to {len(emails)} recipient(s).'
            })
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'Failed to send email: {str(e)}'
            })

    # Invalid request method
    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'})


def gallery_dashboard(request):
    """Display all gallery images and allow adding new ones."""
    gallery_items = SummitGallery.objects.all()
    form = GalleryForm()

    if request.method == 'POST':
        form = GalleryForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Gallery image added successfully!")
            return redirect('gallery_dashboard')
        else:
            messages.error(request, "Error adding gallery image. Please check the form.")

    return render(request, 'gallery/gallery_dashboard.html', {
        'gallery_items': gallery_items,
        'form': form,
    })


def gallery_edit(request, pk):
    """Edit a specific gallery image."""
    item = get_object_or_404(SummitGallery, pk=pk)
    if request.method == 'POST':
        form = GalleryForm(request.POST, request.FILES, instance=item)
        if form.is_valid():
            form.save()
            messages.success(request, "Gallery image updated successfully!")
            return redirect('gallery_dashboard')
        else:
            messages.error(request, "Error updating gallery image.")
    else:
        form = GalleryForm(instance=item)

    return render(request, 'gallery/gallery_edit.html', {'form': form, 'item': item})


@require_POST
def gallery_delete(request, pk):
    """Delete a gallery item."""
    item = get_object_or_404(SummitGallery, pk=pk)
    item.delete()
    messages.success(request, "Gallery image deleted successfully!")
    return redirect('gallery_dashboard')


def speaker_dashboard(request):
    """Speaker management dashboard."""
    speakers = SummitSpeaker.objects.all().order_by('full_name')
    form = SpeakerForm()

    # ✅ Handle new speaker creation
    if request.method == "POST":
        form = SpeakerForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "✅ Speaker added successfully!")
            return redirect("speaker_dashboard")
        else:
            messages.error(request, "⚠️ Please correct the errors below.")

    context = {
        "speakers": speakers,
        "form": form
    }
    return render(request, "speaker/speaker_dashboard.html", context)


def speaker_create(request):
    if request.method == "POST":
        form = SpeakerForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Speaker added successfully!")
            return redirect("speaker_dashboard")
    else:
        form = SpeakerForm()
    return render(request, "speaker/speaker_form.html", {"form": form, "title": "Add Speaker"})


def update_speaker(request, pk):
    speaker = get_object_or_404(SummitSpeaker, pk=pk)
    if request.method == "POST":
        form = SpeakerForm(request.POST, request.FILES, instance=speaker)
        if form.is_valid():
            form.save()
            messages.success(request, "Speaker details updated successfully!")
            return redirect("speaker_dashboard")
    else:
        form = SpeakerForm(instance=speaker)
    return render(request, "speaker/speaker_form.html", {"form": form, "title": "Update Speaker"})


def delete_speaker(request, pk):
    speaker = get_object_or_404(SummitSpeaker, pk=pk)
    if request.method == "POST":
        speaker.delete()
        messages.success(request, "Speaker deleted successfully!")
        return redirect("speaker_dashboard")
    return render(request, "speaker/confirm_delete.html", {"speaker": speaker})


# Partner


def partner_dashboard(request):
    partners = SummitPartner.objects.all().order_by("order")
    return render(request, "partner/partner_dashboard.html", {"partners": partners})


def save_partner(request):
    if request.method == "POST":
        partner_id = request.POST.get("partner_id")
        name = request.POST.get("name")
        website = request.POST.get("website")
        order = request.POST.get("order", 0)
        is_active = request.POST.get("is_active") == "on"
        logo = request.FILES.get("logo")

        if partner_id:
            partner = get_object_or_404(SummitPartner, pk=partner_id)
            partner.name = name
            partner.website = website
            partner.order = order
            partner.is_active = is_active
            if logo:
                partner.logo = logo
            partner.save()
            messages.success(request, "✅ Partner updated successfully!")
        else:
            if not logo:
                messages.error(request, "Please upload a logo before saving.")
                return redirect("partner_dashboard")

            SummitPartner.objects.create(
                name=name,
                logo=logo,
                website=website,
                order=order,
                is_active=is_active,
            )
            messages.success(request, "✅ Partner added successfully!")

        return redirect("partner_dashboard")


def delete_partner(request, partner_id):
    if request.method == "POST":
        partner = get_object_or_404(SummitPartner, pk=partner_id)
        partner.delete()
        messages.success(request, "🗑️ Partner deleted successfully!")
        return redirect("partner_dashboard")


# Agenda view

# --------------------------------------------


@login_required
def dashboard_home(request):
    days = SummitScheduleDay.objects.all()
    return render(request, "schedule/dashboard_home.html", {"days": days})


# ---------------- DAY CRUD ----------------
@login_required
def add_day(request):
    if request.method == "POST":
        form = ScheduleDayForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "✅ Day added successfully.")
            return redirect("dashboard_home")
    else:
        form = ScheduleDayForm()
    return render(request, "schedule/day_form.html", {"form": form})


@login_required
def edit_day(request, pk):
    day = get_object_or_404(SummitScheduleDay, id=pk)
    if request.method == "POST":
        form = ScheduleDayForm(request.POST, instance=day)
        if form.is_valid():
            form.save()
            messages.success(request, "✅ Day updated successfully.")
            return redirect("dashboard_home")
    else:
        form = ScheduleDayForm(instance=day)
    return render(request, "schedule/day_form.html", {"form": form, "day": day})


@login_required
def delete_day(request, pk):
    day = get_object_or_404(SummitScheduleDay, id=pk)
    day.delete()
    messages.warning(request, "🗑️ Day deleted successfully.")
    return redirect("dashboard_home")


# ---------------- TIMESLOT CRUD ----------------
@login_required
def add_timeslot(request, day_id):
    day = get_object_or_404(SummitScheduleDay, id=day_id)
    if request.method == "POST":
        form = TimeSlotForm(request.POST)
        if form.is_valid():
            timeslot = form.save(commit=False)
            timeslot.day = day
            timeslot.save()
            messages.success(request, "✅ Time slot added successfully.")
            return redirect("dashboard_home")
    else:
        form = TimeSlotForm(initial={"day": day})
    return render(request, "schedule/timeslot_form.html", {"form": form, "day": day})


# ---------------- SESSION CRUD (WITH PANELISTS) ----------------
@login_required
def add_session(request, timeslot_id):
    timeslot = get_object_or_404(SummitTimeSlot, id=timeslot_id)
    if request.method == "POST":
        form = SessionForm(request.POST)
        formset = PanelistFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            session = form.save(commit=False)
            session.timeslot = timeslot
            session.save()
            formset.instance = session
            formset.save()
            messages.success(request, "✅ Session and panelists added.")
            return redirect("dashboard_home")
    else:
        form = SessionForm()
        formset = PanelistFormSet()
    return render(request, "schedule/session_form.html", {"form": form, "formset": formset})


@login_required
def edit_session(request, pk):
    session = get_object_or_404(Session, id=pk)
    if request.method == "POST":
        form = SessionForm(request.POST, instance=session)
        formset = PanelistFormSet(request.POST, instance=session)
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            messages.success(request, "✅ Session updated successfully.")
            return redirect("dashboard_home")
    else:
        form = SessionForm(instance=session)
        formset = PanelistFormSet(instance=session)
    return render(request, "schedule/session_form.html", {"form": form, "formset": formset})


@login_required
def delete_session(request, pk):
    session = get_object_or_404(SummitSession, id=pk)
    session.delete()
    messages.warning(request, "🗑️ Session deleted successfully.")
    return redirect("dashboard_home")


@require_api_key
def get_registrants(request):
    """
    GET /reg-service/registrations/
    Returns a paginated list of registered participants for Pathways Technologies.

    Query Parameters:
        page (int): The page number to retrieve. Default = 1.
        limit (int): Number of records per page. Default = 50.
        sort (str): Sorting order, either 'asc' or 'desc'. Default = 'desc'.

    Response:
        {
            "count": 230,
            "total_pages": 5,
            "current_page": 1,
            "page_size": 50,
            "sort_order": "asc",
            "next_page": 2,
            "previous_page": null,
            "registrants": [ ... ]
        }
    """
    if request.method != "GET":
        return JsonResponse({"detail": "Method not allowed."}, status=405)

    # --- Get pagination parameters ---
    try:
        page = int(request.GET.get("page", 1))
        limit = int(request.GET.get("limit", 50))
    except ValueError:
        return JsonResponse({"detail": "Invalid pagination parameters."}, status=400)

    # --- Get sorting order ---
    sort_order = request.GET.get("sort", "desc").lower()
    if sort_order not in ["asc", "desc"]:
        return JsonResponse({"detail": "Invalid sort order. Use 'asc' or 'desc'."}, status=400)

    # --- Apply ordering ---
    order_field = "created_at" if sort_order == "asc" else "-created_at"

    # --- Query and paginate ---
    registrants = Registrant.objects.all().order_by(order_field)
    paginator = Paginator(registrants, limit)
    current_page = paginator.get_page(page)

    # --- Serialize paginated results ---
    data = [serialize_registrant(r) for r in current_page]

    # --- Return JSON response ---
    return JsonResponse({
        "count": paginator.count,
        "total_pages": paginator.num_pages,
        "current_page": current_page.number,
        "page_size": limit,
        "sort_order": sort_order,
        "next_page": current_page.next_page_number() if current_page.has_next() else None,
        "previous_page": current_page.previous_page_number() if current_page.has_previous() else None,
        "registrants": data
    }, status=200)


from django.http import HttpResponse
from datetime import datetime

def add_to_calendar(request):
    ics_content = """BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Kenya Software Summit 2025//EN
CALSCALE:GREGORIAN
METHOD:PUBLISH
BEGIN:VEVENT
UID:kenya-software-summit-2025@ict.go.ke
DTSTAMP:{timestamp}
DTSTART;VALUE=DATE:20251110
DTEND;VALUE=DATE:20251113
SUMMARY:Kenya Software Summit 2025
DESCRIPTION:Join Kenya's premier national software innovation event.\\nRegister to participate: https://softwaresummit.go.ke/register
LOCATION:Eldoret City
ORGANIZER;CN=Ministry of ICT and the Digital Economy:MAILTO:softwaresummit@ict.go.ke
END:VEVENT
END:VCALENDAR
""".format(timestamp=datetime.utcnow().strftime("%Y%m%dT%H%M%SZ"))

    response = HttpResponse(ics_content, content_type="text/calendar; charset=utf-8")
    response["Content-Disposition"] = "attachment; filename=KenyaSoftwareSummit2025.ics"
    return response


from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404
from django.utils import timezone
from .models import Registrant, EmailLog
from .utils import send_confirmation_email  # your email sending function

@require_POST
def resend_confirmation_email(request, registrant_id):
    registrant = get_object_or_404(Registrant, id=registrant_id)

    try:
        # Attempt to send the email
        send_confirmation_email(registrant)

        # Update or create EmailLog
        log, created = EmailLog.objects.get_or_create(
            registrant=registrant,
            recipient=registrant.email,
            subject="Confirmation Email",
            defaults={'status': 'success'}
        )
        log.attempts += 1
        log.status = 'success'
        log.sent_at = timezone.now()
        log.error_message = ''
        log.save()

        return JsonResponse({
            "success": True,
            "message": f"Email resent to {registrant.email} successfully.",
            "attempts": log.attempts,
            "status": log.status,
            "last_sent": log.sent_at.strftime("%b %d, %Y %H:%M")
        })

    except Exception as e:
        # Log the failure in EmailLog
        log, _ = EmailLog.objects.get_or_create(
            registrant=registrant,
            recipient=registrant.email,
            subject="Confirmation Email",
            defaults={'status': 'failed'}
        )
        log.attempts += 1
        log.status = 'failed'
        log.error_message = str(e)
        log.sent_at = timezone.now()
        log.save()

        return JsonResponse({
            "success": False,
            "error": str(e),
            "attempts": log.attempts,
            "status": log.status,
            "last_sent": log.sent_at.strftime("%b %d, %Y %H:%M")
        }, status=500)
