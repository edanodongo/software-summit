# imports
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models.functions import TruncDate, TruncMonth
from django.forms import inlineformset_factory
from openpyxl import Workbook
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph,
    Image, Spacer
)
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .decorators import require_api_key
from .forms import *
from .models import *
from .serializers_new import serialize_registrant
from .utils import *

PanelistFormSet = inlineformset_factory(
    SummitSession, SummitPanelist, form=PanelistForm, extra=1, can_delete=True
)
import qrcode
from io import BytesIO
from django.http import FileResponse, Http404, HttpResponse, JsonResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A7, portrait
from reportlab.lib.utils import ImageReader
from reportlab.lib import colors
import os
from django.views.decorators.http import require_POST
from datetime import datetime
from django_countries import countries
from django.contrib.auth.views import LogoutView
from django.contrib.auth.views import LoginView
from django.db.models import Case, When, Value, IntegerField, Sum, Count, Max, Q
from django.shortcuts import get_object_or_404, render, redirect
from django.db import transaction, models
from django.utils.timezone import now, timedelta

from django.db.models import Sum
from django.http import JsonResponse
from .models import Exhibitor, DashboardSetting
from summitPage.models import SummitSponsor
from django.db.models import Q
from .models import Category, Registrant

# begin your views here

def is_student_registrant(registrant: Registrant) -> bool:
    """
    Determines whether a registrant is a student based on both
    organization_type and category name (case-insensitive).
    """
    try:
        # 1️⃣ Check by organization_type
        if registrant.organization_type.strip().lower() == "student":
            return True

        # 2️⃣ Check by category (compare to Category name "Student")
        student_category_ids = [
            str(cid) for cid in Category.objects.filter(name__iexact="Student").values_list("id", flat=True)
        ]
        return str(registrant.category) in student_category_ids

    except Exception:
        return False


def home(request):
    if request.method == 'POST':
        form = QuickRegistrationForm(request.POST, request.FILES)

        if form.is_valid():
            registrant = form.save(commit=False)

            # Explicitly assign file fields
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

    summitspeakers = SummitSpeaker.objects.annotate(
        custom_order=Case(
            When(track__icontains='Keynote', then=Value(1)),
            When(track__icontains='Host', then=Value(2)),
            When(track__icontains='Speaker', then=Value(3)),
            default=Value(4),
            output_field=IntegerField(),
        )
    ).order_by('custom_order', 'full_name')

    return render(request, "summit/home.html", {
        'form': form,
        'gallery_items': gallery_items,
        'partners': partners,
        'days': days,
        'speakers': summitspeakers,
        'interest_choices': Registrant.INTEREST_CHOICES,
    })


def reg(request):
    if request.method == 'POST':
        form = QuickRegistrationForm(request.POST, request.FILES)

        if form.is_valid():
            registrant = form.save(commit=False)

            # --- Assign uploaded files ---
            if request.FILES.get("passport_photo"):
                registrant.passport_photo = request.FILES["passport_photo"]
            if request.FILES.get("national_id_scan"):
                registrant.national_id_scan = request.FILES["national_id_scan"]

            # --- Handle interests ---
            interests = form.cleaned_data.get("interests", [])
            other_interest = form.cleaned_data.get("other_interest")
            if "others" in interests and other_interest:
                registrant.other_interest = other_interest
            registrant.interests = interests

            registrant.save()

            # ✅ Use shared student logic
            is_student = is_student_registrant(registrant)

            # --- Send appropriate email ---
            try:
                if is_student:
                    send_student_email(registrant)
                    print("Student")
                else:
                    send_confirmation_email(registrant)
                    print("Delegate")

            except Exception as e:
                print("Email Send error:", e)
                if request.headers.get("x-requested-with") == "XMLHttpRequest":
                    return JsonResponse(
                        {"success": True, "message": "Registration saved, but email failed."},
                        status=200
                    )
                messages.warning(request, "Registered, but confirmation email failed.")

            # --- Return success response ---
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

    # --- Extra context data ---
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


def _fit_text(c, text, max_width, start_font_size=9, font_name="Helvetica-Bold"):
    """Dynamically adjust font size so text fits within the given width."""
    font_size = start_font_size
    while c.stringWidth(text, font_name, font_size) > max_width and font_size > 5:
        font_size -= 0.5
    return font_size


@login_required
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


@login_required
def unsubscribe_view(request, token):
    try:
        registrant = Registrant.objects.get(unsubscribe_token=token)
        registrant.updates_opt_in = False
        registrant.save()
        return render(request, "summit/unsubscribe.html")
    except Registrant.DoesNotExist:
        return HttpResponse("<h2>Invalid unsubscribe link.</h2>", status=400)


@login_required
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
        "AUTO_LOGOUT_TIMEOUT": settings.AUTO_LOGOUT_TIMEOUT,
        'current_year': timezone.now().year,
    })


# --------------------------------------------
# === Excel Export ===
# --------------------------------------------
@login_required
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


# --------------------------------------------
# === PDF Export in Landscape ===
# === PDF Export in Landscape with Logo, Header & Footer ===
# --------------------------------------------

@login_required
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


@login_required
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


@login_required
def dashboard_view(request):
    registrations = Registrant.objects.all().order_by("created_at")
    total_users = Registrant.objects.exclude(
        Q(organization_type='Student') | Q(category='4')
    ).count()

    updates_count = Registrant.objects.filter(updates_opt_in=True).count()

    # Convert category IDs to strings because Registrant.category is a CharField
    student_category_ids = [str(cid) for cid in
                            Category.objects.filter(name__iexact="Student").values_list("id", flat=True)]

    # Exclude students (either via org_type or category)
    registrants = (
        Registrant.objects.exclude(
            Q(organization_type__iexact="Student") | Q(category__in=student_category_ids)
        )
        .order_by("-created_at")
        .annotate(
            email_attempts=Count("emaillog"),
            email_status=Max("emaillog__status"),
            email_last_sent=Max("emaillog__sent_at"),
        )
    )

    for reg in registrants:
        reg.category_name = get_category_name_from_id(reg.category)

    context = {
        "registrations": registrations,
        "total_users": total_users,
        "updates_count": updates_count,
        "registrants": registrants,
        "org_type_choices": Registrant.ORG_TYPE_CHOICES,
        "AUTO_LOGOUT_TIMEOUT": settings.AUTO_LOGOUT_TIMEOUT,
        "current_year": timezone.now().year,
    }
    return render(request, "summit/dashboard.html", context)


# Endpoint for charts (AJAX/React)
@login_required
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

    def form_valid(self, form):
        # Log the user in using the parent method
        response = super().form_valid(form)

        # Handle "Remember me"
        remember_me = self.request.POST.get('rememberMe')

        if remember_me:
            # Session will last 14 days
            self.request.session.set_expiry(60 * 60 * 24 * 14)
        else:
            # Session expires when the browser is closed
            self.request.session.set_expiry(0)

        # Record last activity time for inactivity auto-logout
        self.request.session['last_activity'] = timezone.now().isoformat()

        return response


class SummitLogoutView(LogoutView):
    next_page = 'custom_login'

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        messages.success(request, "You have been logged out successfully.")
        return super().post(request, *args, **kwargs)


@login_required
def about(request):
    return render(request, 'summit/samples/about.html')


def index(request):
    return render(request, 'summit/index.html')


@login_required
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


def places(request):
    return render(request, "summit/venue.html")


def not_found(request):
    return render(request, "summit/404.html")


@login_required
def mailme_view(request):
    emails = Registrant.objects.values_list('email', flat=True)
    return render(request, "setup/mailme.html", {"emails": emails})


def speakers(request):
    speakers = SummitSpeaker.objects.all()
    summitspeakers = SummitSpeaker.objects.annotate(
        custom_order=Case(
            When(track__icontains='Keynote', then=Value(1)),
            When(track__icontains='Host', then=Value(2)),
            When(track__icontains='Speaker', then=Value(3)),
            default=Value(4),
            output_field=IntegerField(),
        )
    ).order_by('custom_order', 'full_name')
    return render(request, "summit/speakers.html", {"speakers": speakers})


def media(request):
    return render(request, "summit/gallery.html")


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


@login_required
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


@login_required
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
        "AUTO_LOGOUT_TIMEOUT": settings.AUTO_LOGOUT_TIMEOUT,
        'current_year': timezone.now().year,
    })


@login_required
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


@login_required
@require_POST
def gallery_delete(request, pk):
    """Delete a gallery item."""
    item = get_object_or_404(SummitGallery, pk=pk)
    item.delete()
    messages.success(request, "Gallery image deleted successfully!")
    return redirect('gallery_dashboard')


@login_required
def speaker_dashboard(request):
    """Speaker management dashboard."""
    speakers = SummitSpeaker.objects.all().order_by('full_name')
    form = SpeakerForm()

    # Handle new speaker creation
    if request.method == "POST":
        form = SpeakerForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Speaker added successfully!")
            return redirect("speaker_dashboard")
        else:
            messages.error(request, "⚠️ Please correct the errors below.")

    context = {
        "speakers": speakers,
        "form": form,
        "AUTO_LOGOUT_TIMEOUT": settings.AUTO_LOGOUT_TIMEOUT,
        'current_year': timezone.now().year,
    }
    return render(request, "speaker/speaker_dashboard.html", context)


@login_required
def speaker_create(request):
    if request.method == "POST":
        form = SpeakerForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Speaker added successfully!")
            return redirect("speaker_dashboard")
    else:
        form = SpeakerForm()
    return render(request, "speaker/speaker_form.html", {
        "form": form,
        "title": "Add Speaker",
        'current_year': timezone.now().year, })


@login_required
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


@login_required
def delete_speaker(request, pk):
    speaker = get_object_or_404(SummitSpeaker, pk=pk)
    if request.method == "POST":
        speaker.delete()
        messages.success(request, "Speaker deleted successfully!")
        return redirect("speaker_dashboard")
    return render(request, "speaker/confirm_delete.html", {"speaker": speaker})


# Partner

@login_required
def partner_dashboard(request):
    partners = SummitPartner.objects.all().order_by("order")
    return render(request, "partner/partner_dashboard.html", {
        "partners": partners,
        "AUTO_LOGOUT_TIMEOUT": settings.AUTO_LOGOUT_TIMEOUT,
        'current_year': timezone.now().year, })


@login_required
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
            messages.success(request, "Partner updated successfully!")
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
            messages.success(request, "Partner added successfully!")

        return redirect("partner_dashboard")


@login_required
def delete_partner(request, partner_id):
    if request.method == "POST":
        partner = get_object_or_404(SummitPartner, pk=partner_id)
        partner.delete()
        messages.success(request, "🗑️ Partner deleted successfully!")
        return redirect("partner_dashboard")


# --------------------------------------------
# Agenda view
# --------------------------------------------

@login_required
def dashboard_home(request):
    days = SummitScheduleDay.objects.all()
    return render(request, "schedule/dashboard_home.html", {
        "days": days,
        "AUTO_LOGOUT_TIMEOUT": settings.AUTO_LOGOUT_TIMEOUT,
        'current_year': timezone.now().year, })


# ---------------- DAY CRUD ----------------
@login_required
def add_day(request):
    if request.method == "POST":
        form = ScheduleDayForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Day added successfully.")
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
            messages.success(request, "Day updated successfully.")
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


# --------------------------------------------
# -TIMESLOT CRUD -
# --------------------------------------------
@login_required
def add_timeslot(request, day_id):
    day = get_object_or_404(SummitScheduleDay, id=day_id)
    if request.method == "POST":
        form = TimeSlotForm(request.POST)
        if form.is_valid():
            timeslot = form.save(commit=False)
            timeslot.day = day
            timeslot.save()
            messages.success(request, "Time slot added successfully.")
            return redirect("dashboard_home")
    else:
        form = TimeSlotForm(initial={"day": day})
    return render(request, "schedule/timeslot_form.html", {
        "form": form,
        "day": day,
        "AUTO_LOGOUT_TIMEOUT": settings.AUTO_LOGOUT_TIMEOUT,
        'current_year': timezone.now().year,
    })


# --------------------------------------------
# -- SESSION CRUD (WITH PANELISTS) --
# --------------------------------------------
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
            messages.success(request, "Session and panelists added.")
            return redirect("dashboard_home")
    else:
        form = SessionForm()
        formset = PanelistFormSet()
    return render(request, "schedule/session_form.html", {
        "form": form, "formset": formset,
        "AUTO_LOGOUT_TIMEOUT": settings.AUTO_LOGOUT_TIMEOUT,
        'current_year': timezone.now().year,
    })


@login_required
def edit_session(request, pk):
    session = get_object_or_404(SummitSession, id=pk)
    if request.method == "POST":
        form = SessionForm(request.POST, instance=session)
        formset = PanelistFormSet(request.POST, instance=session)
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            messages.success(request, "Session updated successfully.")
            return redirect("dashboard_home")
    else:
        form = SessionForm(instance=session)
        formset = PanelistFormSet(instance=session)
    return render(request, "schedule/session_form.html", {
        "form": form,
        "formset": formset,
        "AUTO_LOGOUT_TIMEOUT": settings.AUTO_LOGOUT_TIMEOUT,
        'current_year': timezone.now().year,
    })


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


@login_required
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


@login_required
def guest_category(request):
    category = Category.objects.all().order_by('id')
    category = {"category": category}

    return render(request, "setup/add_category.html", category)


@login_required
def categories_create(request):
    return render(request, "setup/category_form.html")


@login_required
def save_category(request):
    if request.method == "POST":
        category_name = request.POST.get("category")
        description = request.POST.get("description")

        try:
            # Save category in DB
            Category.objects.create(
                name=category_name,
                description=description
            )

            return JsonResponse({
                'status': 'success',
                'message': f'Category "{category_name}" successfully saved.'
            })

        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'Failed to save details: {str(e)}'
            })

    # Invalid request method
    return JsonResponse({
        'status': 'error',
        'message': 'Invalid request method.'
    })


# --------------------------------------------

@login_required
def delete_category(request, pk):
    category = get_object_or_404(Category, pk=pk)

    if request.method == "POST":
        try:
            category_name = category.name  # store before deletion for feedback
            category.delete()

            return JsonResponse({
                'status': 'success',
                'message': f'Category "{category_name}" deleted successfully!'
            })

        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'Failed to delete category: {str(e)}'
            })

    # If not POST, return an error
    return JsonResponse({
        'status': 'error',
        'message': 'Invalid request method. Use POST to delete.'
    })


# --------------------------------------------

@login_required
def update_category(request, pk):
    category = get_object_or_404(Category, pk=pk)

    context = {
        "category": category
    }

    return render(request, "setup/edit_category_form.html", context)


# --------------------------------------------

@login_required
def edit_category(request):
    if request.method == "POST":
        category_id = request.POST.get("id")
        name = request.POST.get("category")
        description = request.POST.get("description")

        try:
            # Update existing record
            category = Category.objects.get(pk=category_id)
            category.name = name
            category.description = description
            category.save()
            message = f'Category "{name}" successfully updated.'

            return JsonResponse({'status': 'success', 'message': message})

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': f'Error: {str(e)}'})

    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'})


# --------------------------------------------

def gallery(request):
    gallery_items = SummitGallery.objects.filter(is_active=True).order_by('order')
    return render(request, "summit/gallery.html", {
        'gallery_items': gallery_items,
    })


# --------------------------------------------
# Exhibitor Registration
# --------------------------------------------


def exhibitor(request):
    # --- Total and remaining counts/booths ---
    dashboard_setting, _ = DashboardSetting.objects.get_or_create(id=1)
    max_count = dashboard_setting.max_count or 0

    # --- Calculate total taken booths (include nulls and zeros) ---
    total_taken = Exhibitor.objects.aggregate(total=Sum('total_count'))['total'] or 0
    null_or_zero_count = Exhibitor.objects.filter(
        Q(total_count__isnull=True) | Q(total_count=0)
    ).count()
    total_taken += null_or_zero_count

    remaining = max(max_count - total_taken, 0)

    # --- Build the alert message ---
    if remaining > 4:
        alert_message = f"{remaining} booths available."
        alert_class = "alert-success"
    elif 2 < remaining <= 4:
        alert_message = f"{remaining} booths available."
        alert_class = "alert-info"
    elif 1 < remaining <= 2:
        alert_message = f"{remaining} booths available."
        alert_class = "alert-warning"
    elif remaining == 1:
        alert_message = "1 booth remaining!"
        alert_class = "alert-danger"
    else:
        alert_message = "0 booths available. Registration closed!"
        alert_class = "alert-danger"

    registration_closed = remaining <= 0

    # --- Handle submission ---
    if request.method == "POST":
        form = ExhibitorRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            selected_count = int(form.cleaned_data.get("count", 1))

            try:
                with transaction.atomic():
                    # Lock the DashboardSetting to prevent race conditions
                    locked_setting = DashboardSetting.objects.select_for_update().get(id=1)
                    total_sum_locked = Exhibitor.objects.aggregate(total=Sum('total_count'))['total'] or 0
                    remaining_locked = max(locked_setting.max_count - total_sum_locked, 0)

                    if selected_count > remaining_locked:
                        msg = f"Cannot register {selected_count} booths. Only {remaining_locked} remaining."
                        if request.headers.get("x-requested-with") == "XMLHttpRequest":
                            return JsonResponse({"success": False, "errors": {"count": [msg]}}, status=400)
                        messages.error(request, msg)
                        return render(request, "summit/exhibitor.html", {
                            "form": form,
                            "alert_message": alert_message,
                            "alert_class": alert_class,
                            "remaining": remaining_locked,
                        })

                    # Save exhibitor safely
                    exhibitor = form.save(commit=False)
                    exhibitor.total_count = selected_count
                    exhibitor.save()

            except Exception as e:
                print("❌ Transaction error:", e)
                msg = "An unexpected error occurred. Please try again."
                if request.headers.get("x-requested-with") == "XMLHttpRequest":
                    return JsonResponse({"success": False, "errors": {"server": [msg]}}, status=500)
                messages.error(request, msg)
                return render(request, "summit/exhibitor.html", {
                    "form": form,
                    "alert_message": alert_message,
                    "alert_class": alert_class,
                    "remaining": remaining,
                })

            # --- Try sending confirmation email ---
            try:
                send_confirmation_mail(exhibitor)
            except Exception as e:
                print("❌ Email send error:", e)
                if request.headers.get("x-requested-with") == "XMLHttpRequest":
                    return JsonResponse({
                        "success": True,
                        "message": "Registration successful, but confirmation email failed."
                    })
                messages.warning(request, "Registration saved, but email could not be sent.")

            # Success
            if request.headers.get("x-requested-with") == "XMLHttpRequest":
                return JsonResponse({"success": True, "message": "Registration successful!"})
            messages.success(request, "Registration successful!")
            return redirect("home")

        # ❌ Invalid form
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse({"success": False, "errors": form.errors}, status=400)
        messages.error(request, "Please correct the errors.")
    else:
        form = ExhibitorRegistrationForm()

    return render(request, "summit/exhibitor.html", {
        "form": form,
        "registration_closed": registration_closed,
        "alert_message": alert_message,
        "alert_class": alert_class,
        # "remaining": remaining,
    })


# --------------------------------------------

def exhibitor_status(request):
    """Return the accurate remaining booth count including exhibitors with 0 or null total_count."""
    dashboard_setting, _ = DashboardSetting.objects.get_or_create(id=1)
    max_count = dashboard_setting.max_count or 0

    # --- Calculate total taken booths (include nulls and zeros) ---
    total_taken = Exhibitor.objects.aggregate(total=Sum('total_count'))['total'] or 0
    null_or_zero_count = Exhibitor.objects.filter(
        Q(total_count__isnull=True) | Q(total_count=0)
    ).count()
    total_taken += null_or_zero_count

    remaining = max(max_count - total_taken, 0)

    # --- Build the alert message ---
    if remaining > 4:
        alert_message = f"{remaining} booths available."
        alert_class = "alert-success"
    elif 2 < remaining <= 4:
        alert_message = f"{remaining} booths available."
        alert_class = "alert-info"
    elif 1 < remaining <= 2:
        alert_message = f"{remaining} booths available."
        alert_class = "alert-warning"
    elif remaining == 1:
        alert_message = "1 booth remaining!"
        alert_class = "alert-danger"
    else:
        alert_message = "0 booths available. Registration closed!"
        alert_class = "alert-danger"

    return JsonResponse({
        "max_count": max_count,
        "total_taken": total_taken,
        "remaining": remaining,
        "alert_message": alert_message,
        "alert_class": alert_class,
    })


# --------------------------------------------
# Admin Dashboard (Exhibitor Management)
# --------------------------------------------
from django.db.models import Sum, Q, Count, OuterRef, Subquery, Max
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.conf import settings
from django.contrib.auth.decorators import login_required

from summitPage.models import Exhibitor, Booth, ExhibitionSection, EmailLogs, DashboardSetting
from summitPage.forms import DashboardSettingForm


@login_required
def admin_dashboard(request):
    sections = ExhibitionSection.objects.all()
    booths = Booth.objects.all()
    exhibitors = Exhibitor.objects.all()

    # --- Fetch or create dashboard settings ---
    dashboard_setting, _ = DashboardSetting.objects.get_or_create(id=1)

    # --- Handle form submission for editing max_count ---
    if request.method == "POST":
        form = DashboardSettingForm(request.POST, instance=dashboard_setting)
        if form.is_valid():
            form.save()
            messages.success(request, "Dashboard settings updated successfully.")
            return redirect("admin_dashboard")
    else:
        form = DashboardSettingForm(instance=dashboard_setting)

    # --- Total and remaining counts ---
    max_count = dashboard_setting.max_count or 0
    total_taken = Exhibitor.objects.aggregate(total=Sum("total_count"))["total"] or 0
    null_or_zero_count = Exhibitor.objects.filter(Q(total_count__isnull=True) | Q(total_count=0)).count()
    total_taken += null_or_zero_count
    remaining = max(max_count - total_taken, 0)

    # --- Alert message setup ---
    if remaining > 4:
        alert_message, alert_class = f"{remaining} booths available.", "alert-success"
    elif 2 < remaining <= 4:
        alert_message, alert_class = f"{remaining} booths available.", "alert-info"
    elif 1 < remaining <= 2:
        alert_message, alert_class = f"{remaining} booths available.", "alert-warning"
    elif remaining == 1:
        alert_message, alert_class = "1 booth remaining!", "alert-danger"
    else:
        alert_message, alert_class = "0 booths available. Registration closed!", "alert-danger"

    registration_closed = remaining <= 0

    # --- Search & filtering ---
    query = request.GET.get("q", "").strip()
    category_filter = request.GET.get("category", "")
    section_filter = request.GET.get("section", "")
    country_filter = request.GET.get("country_of_registration", "")

    if query:
        exhibitors = exhibitors.filter(
            Q(first_name__icontains=query)
            | Q(second_name__icontains=query)
            | Q(email__icontains=query)
            | Q(phone__icontains=query)
            | Q(organization_type__icontains=query)
        )
    if category_filter:
        exhibitors = exhibitors.filter(category=category_filter)
    if section_filter:
        exhibitors = exhibitors.filter(section_id=section_filter)
    if country_filter:
        exhibitors = exhibitors.filter(country_of_registration=country_filter)

    # --- Stats ---
    total_exhibitors = exhibitors.count()
    total_booths = booths.count()
    booked_booths = booths.filter(is_booked=True).count()
    pending_approvals = exhibitors.filter(privacy_agreed=False).count()
    categories = Exhibitor._meta.get_field("category").choices

    # --- Available countries ---
    used_countries = Exhibitor.objects.values_list("country_of_registration", flat=True).distinct()
    countries = dict(Exhibitor._meta.get_field("country_of_registration").choices)
    available_countries = sorted(
        [(code, countries.get(code, code)) for code in used_countries if code],
        key=lambda x: x[1],
    )

    # --- Annotate exhibitors with latest email log info ---
    latest_log = EmailLogs.objects.filter(exhibitor=OuterRef("pk")).order_by("-sent_at")

    exhibitors = exhibitors.annotate(
        email_last_sent=Subquery(latest_log.values("sent_at")[:1]),
        email_status=Subquery(latest_log.values("status")[:1]),
        email_attempts=Count("emaillog"),
    )

    # --- Add readable country display ---
    for exhibitor in exhibitors:
        exhibitor.country_display = (
            exhibitor.get_country_of_registration_display()
            if exhibitor.country_of_registration
            else "—"
        )

    # --- Render template ---
    return render(
        request,
        "exhibitor/admin_dashboard.html",
        {
            "sections": sections,
            "booths": booths,
            "exhibitors": exhibitors.order_by("-created_at")[:20],
            "total_exhibitors": total_exhibitors,
            "total_booths": total_booths,
            "booked_booths": booked_booths,
            "pending_approvals": pending_approvals,
            "categories": categories,
            "query": query,
            "category_filter": category_filter,
            "section_filter": section_filter,
            "country_filter": country_filter,
            "available_countries": available_countries,
            "form": form,
            "total_count": total_taken,
            "max_count": max_count,
            "remaining": remaining,
            "alert_message": alert_message,
            "alert_class": alert_class,
            "registration_closed": registration_closed,
            "current_year": timezone.now().year,
            "AUTO_LOGOUT_TIMEOUT": settings.AUTO_LOGOUT_TIMEOUT,
        },
    )


# --------------------------------------------
# Delete Exhibitor
# --------------------------------------------
@login_required
def admin_exhibitor_delete(request, pk):
    exhibitor = get_object_or_404(Exhibitor, pk=pk)
    if request.method == "POST":
        exhibitor.delete()
        messages.success(request, f"Exhibitor '{exhibitor.get_full_name()}' deleted successfully.")
        return redirect("admin_dashboard")
    return render(request, "exhibitor/admin_exhibitor_confirm_delete.html", {
        "exhibitor": exhibitor,
        "AUTO_LOGOUT_TIMEOUT": settings.AUTO_LOGOUT_TIMEOUT,
        'current_year': timezone.now().year,
    })


# --------------------------------------------
# Section Management
# --------------------------------------------
@login_required
def admin_sections(request):
    sections = ExhibitionSection.objects.all()
    return redirect("admin_dashboard")


@login_required
def admin_add_section(request):
    if request.method == "POST":
        form = ExhibitionSectionForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Section added successfully.")
            return redirect("admin_sections")
    else:
        form = ExhibitionSectionForm()
    return render(request, "exhibitor/admin_section_form.html", {"form": form, "title": "Add Section"})


@login_required
def admin_edit_section(request, pk):
    section = get_object_or_404(ExhibitionSection, pk=pk)
    if request.method == "POST":
        form = ExhibitionSectionForm(request.POST, instance=section)
        if form.is_valid():
            form.save()
            messages.success(request, "Section updated successfully.")
            return redirect("admin_sections")
    else:
        form = ExhibitionSectionForm(instance=section)
    return render(request, "exhibitor/admin_section_form.html", {"form": form, "title": "Edit Section"})


@login_required
def admin_delete_section(request, pk):
    section = get_object_or_404(ExhibitionSection, pk=pk)
    if request.method == "POST":
        section.delete()
        messages.success(request, "Section deleted successfully.")
        return redirect("admin_sections")
    return render(request, "exhibitor/admin_confirm_delete.html", {"object": section, "type": "Section"})


# --------------------------------------------
# Booth Management
# --------------------------------------------
@login_required
def admin_booths(request):
    booths = Booth.objects.all()
    return render(request, "exhibitor/admin_booths.html", {"booths": booths})


@login_required
def admin_add_booth(request):
    if request.method == "POST":
        form = BoothForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Booth added successfully.")
            return redirect("admin_booths")
    else:
        form = BoothForm()
    return render(request, "exhibitor/admin_booth_form.html", {"form": form, "title": "Add Booth"})


@login_required
def admin_edit_booth(request, pk):
    booth = get_object_or_404(Booth, pk=pk)
    if request.method == "POST":
        form = BoothForm(request.POST, instance=booth)
        if form.is_valid():
            form.save()
            messages.success(request, "Booth updated successfully.")
            return redirect("admin_booths")
    else:
        form = BoothForm(instance=booth)
    return render(request, "exhibitor/admin_booth_form.html", {"form": form, "title": "Edit Booth"})


@login_required
def admin_delete_booth(request, pk):
    booth = get_object_or_404(Booth, pk=pk)
    if request.method == "POST":
        booth.delete()
        messages.success(request, "Booth deleted successfully.")
        return redirect("admin_booths")
    return render(request, "exhibitor/admin_confirm_delete.html", {"object": booth, "type": "Booth"})


# --------------------------------------------

@login_required
def main_dashboard_view(request):
    today = now().date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    year_ago = today - timedelta(days=365)

    # --- Base totals ---
    total_registrants = Registrant.objects.count()
    total_exhibitors = Exhibitor.objects.count()
    total_partners = SummitPartner.objects.count()
    total_gallery = SummitGallery.objects.count()
    total_booths = Booth.objects.count()

    # --- Growth comparisons ---
    new_registrants_week = Registrant.objects.filter(created_at__gte=week_ago).count()
    new_registrants_month = Registrant.objects.filter(created_at__gte=month_ago).count()
    new_exhibitors_month = Exhibitor.objects.filter(created_at__gte=month_ago).count()
    new_partners_month = SummitPartner.objects.filter(created_at__gte=month_ago).count()

    # --- Verification & opt-in stats ---
    verified_registrants = Registrant.objects.filter(privacy_agreed=True).count()
    opted_in_registrants = Registrant.objects.filter(updates_opt_in=True).count()

    # --- Booth stats ---
    active_booths = Booth.objects.filter(is_booked=True).count()
    available_booths = total_booths - active_booths
    booth_utilization = (active_booths / total_booths * 100) if total_booths else 0

    # --- Partner status ---
    partners_active = SummitPartner.objects.filter(is_active=True).count()
    partners_inactive = total_partners - partners_active

    # --- 7-day registration trend ---
    daily_labels, daily_counts = [], []
    for i in range(7):
        day = today - timedelta(days=i)
        daily_labels.append(day.strftime("%a"))
        daily_counts.append(Registrant.objects.filter(created_at__date=day).count())
    daily_labels.reverse()
    daily_counts.reverse()

    # --- Monthly registration trend (last 6 months) ---
    monthly_reg_data = (
        Registrant.objects.filter(created_at__gte=year_ago)
        .annotate(month=TruncMonth("created_at"))
        .values("month")
        .annotate(count=Count("id"))
        .order_by("month")
    )
    monthly_labels = [r["month"].strftime("%b %Y") for r in monthly_reg_data]
    monthly_counts = [r["count"] for r in monthly_reg_data]

    # --- Exhibitor distribution by category ---
    exhibitor_data = (
        Exhibitor.objects.values("category")
        .annotate(count=Count("id"))
        .order_by("-count")
    )
    exhibitor_labels = [e["category"] or "Uncategorized" for e in exhibitor_data]
    exhibitor_counts = [e["count"] for e in exhibitor_data]

    # --- Registrant organization breakdown ---
    org_data = (
        Registrant.objects.values("organization_type")
        .annotate(count=Count("id"))
        .order_by("-count")
    )
    org_labels = [o["organization_type"] or "Other" for o in org_data]
    org_counts = [o["count"] for o in org_data]

    # --- Recent activity lists ---
    recent_registrants = Registrant.objects.order_by("-created_at")[:5]
    recent_exhibitors = Exhibitor.objects.order_by("-created_at")[:5]
    recent_partners = SummitPartner.objects.order_by("-created_at")[:5]

    # --- Engagement score (simple metric) ---
    engagement_score = 0
    if total_registrants:
        engagement_score = ((opted_in_registrants + verified_registrants) / total_registrants) * 50
    if total_exhibitors:
        engagement_score += (new_exhibitors_month / total_exhibitors) * 50
    engagement_score = round(min(100, engagement_score), 1)

    # --- Optional API/email logs ---
    emails_today = 0
    try:
        emails_today = EmailLog.objects.filter(sent_at__date=today).count()
    except Exception:
        pass

    context = {
        # Totals
        "total_registrants": total_registrants,
        "total_exhibitors": total_exhibitors,
        "total_partners": total_partners,
        "total_gallery": total_gallery,
        "total_booths": total_booths,

        # Growth & insights
        "new_registrants_week": new_registrants_week,
        "new_registrants_month": new_registrants_month,
        "new_exhibitors_month": new_exhibitors_month,
        "new_partners_month": new_partners_month,
        "verified_registrants": verified_registrants,
        "opted_in_registrants": opted_in_registrants,

        # Booths
        "active_booths": active_booths,
        "available_booths": available_booths,
        "booth_utilization": round(booth_utilization, 1),

        # Partners
        "partners_active": partners_active,
        "partners_inactive": partners_inactive,

        # Trends
        "daily_labels": daily_labels,
        "daily_counts": daily_counts,
        "monthly_labels": monthly_labels,
        "monthly_counts": monthly_counts,

        # Charts
        "exhibitor_labels": exhibitor_labels,
        "exhibitor_counts": exhibitor_counts,
        "org_labels": org_labels,
        "org_counts": org_counts,

        # Lists
        "recent_registrants": recent_registrants,
        "recent_exhibitors": recent_exhibitors,
        "recent_partners": recent_partners,

        # Others
        "emails_today": emails_today,
        "engagement_score": engagement_score,
        'current_year': timezone.now().year,
    }

    return render(request, "dashboard/stats_dashboard.html", context)


def summit_sponsor_registration(request):
    """View for registering summit sponsors and partners."""
    if request.method == "POST":
        form = SummitSponsorForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            if request.headers.get("x-requested-with") == "XMLHttpRequest":
                return JsonResponse({"success": True, "message": "Your sponsorship application has been received."})
            messages.success(request, "Thank you! Your sponsorship application has been submitted successfully.")
            return redirect("summit_sponsor_registration")
        else:
            if request.headers.get("x-requested-with") == "XMLHttpRequest":
                return JsonResponse({"success": False, "errors": form.errors})
            messages.error(request, "Please correct the errors below.")
    else:
        form = SummitSponsorForm()

    return render(request, "summit/sponsor.html", {"form": form})


# --------------------------------------------





@login_required
def sponsor_dashboard(request):
    """Admin dashboard to view and manage sponsor partners."""
    query = request.GET.get("q", "")
    sponsors = SummitSponsor.objects.all().order_by("-submitted_at")

    if query:
        sponsors = sponsors.filter(organization_name__icontains=query)

    context = {
        "sponsors": sponsors,
        "query": query,
    }
    return render(request, "sponsors/sponsor_dashboard.html", context)


@login_required
def delete_sponsor(request, sponsor_id):
    """Delete a sponsor record."""
    sponsor = get_object_or_404(SummitSponsor, id=sponsor_id)
    sponsor.delete()
    messages.success(request, f"Sponsor '{sponsor.organization_name}' deleted successfully.")
    return redirect("sponsor_dashboard")


@login_required
def dashboard_student_view(request):
    registrations = Registrant.objects.all().order_by("created_at")

    total_users = Registrant.objects.filter(
        Q(organization_type='Student') | Q(category='4')
    ).count()
    updates_count = Registrant.objects.filter(updates_opt_in=True).count()

    # Convert category IDs to strings because Registrant.category is a CharField
    student_category_ids = [str(cid) for cid in
                            Category.objects.filter(name__iexact="Student").values_list("id", flat=True)]

    # Include only students
    registrants = (
        Registrant.objects.filter(
            Q(organization_type__iexact="Student") | Q(category__in=student_category_ids)
        )
        .order_by("-created_at")
        .annotate(
            email_attempts=Count("emaillog"),
            email_status=Max("emaillog__status"),
            email_last_sent=Max("emaillog__sent_at"),
        )
    )

    for reg in registrants:
        reg.category_name = get_category_name_from_id(reg.category)

    context = {
        "registrations": registrations,
        "total_users": total_users,
        "updates_count": updates_count,
        "registrants": registrants,
        "org_type_choices": Registrant.ORG_TYPE_CHOICES,
        "AUTO_LOGOUT_TIMEOUT": settings.AUTO_LOGOUT_TIMEOUT,
        "current_year": timezone.now().year,
    }
    return render(request, "summit/student.html", context)





@login_required
@require_POST
def approve_student(request, registrant_id):
    registrant = get_object_or_404(Registrant, id=registrant_id)
    name = f"{registrant.first_name} {registrant.second_name}"

    try:
        with transaction.atomic():
            registrant.approved = True
            registrant.save(update_fields=["approved"])

        # Try sending verification email — if it fails, just log it
        try:
            send_student_email_verify(registrant)
        except Exception as e:
            print(f"Email send error for {name}: {e}")

        # Always return success JSON to JS
        return JsonResponse({
            "status": "success",
            "message": f"{name} has been approved successfully."
        })

    except Exception as e:
        print(f"Approval error for {name}: {e}")
        return JsonResponse({
            "status": "error",
            "message": "An unexpected error occurred while approving the student."
        }, status=500)


@login_required
def api_trails(request):
    api_user = ApiAccessLog.objects.all().order_by('id')

    context = {
        "api_user": api_user,
        "org_type_choices": Registrant.ORG_TYPE_CHOICES,
        "AUTO_LOGOUT_TIMEOUT": settings.AUTO_LOGOUT_TIMEOUT,
        "current_year": timezone.now().year,
    }
    return render(request, "audit/api.html", context)


@login_required
@require_POST
def resend_exhibitor_confirmation_email(request, exhibitor_id):
    exhib = get_object_or_404(Exhibitor, id=exhibitor_id)
    try:
        send_confirmation_mail(exhib)
        log, created = EmailLogs.objects.get_or_create(
            exhibitor=exhib,
            recipient=exhib.email,
            subject="Confirmation Email",
            defaults={'status': 'success'},
        )
        log.attempts += 1
        log.status = 'success'
        log.sent_at = timezone.now()
        log.error_message = ''
        log.save()

        return JsonResponse({
            "success": True,
            "message": f"Email resent to {exhib.email} successfully.",
            "attempts": log.attempts,
            "status": log.status,
            "last_sent": log.sent_at.strftime("%b %d, %Y %H:%M"),
        })
    except Exception as e:
        log, _ = EmailLogs.objects.get_or_create(
            exhibitor=exhib,
            recipient=exhib.email,
            subject="Confirmation Email",
            defaults={'status': 'failed'},
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
            "last_sent": log.sent_at.strftime("%b %d, %Y %H:%M"),
        }, status=500)

@login_required
def generate_exhibitor_badge(request, exhibitor_id):
    try:
        exhib = Exhibitor.objects.get(pk=exhibitor_id)
    except Exhibitor.DoesNotExist:
        raise Http404("Exhibitor not found")

    # --- Data ---
    full_name = exhib.get_full_name() or ""
    job_title = exhib.job_title or ""

    # --- Generate QR Code ---
    qr_data = (
        f"Name: {full_name}\n"
        f"Job Title: {job_title}\n"
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

    if exhib.passport_photo:
        photo_path = os.path.join(settings.MEDIA_ROOT, exhib.passport_photo.name)
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

    # Interests

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

    filename = f"{exhib.first_name}_{exhib.second_name}_Badge.pdf"
    return FileResponse(pdf_buffer, as_attachment=True, filename=filename)

