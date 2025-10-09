from django.contrib import messages
from django.contrib.auth.views import LoginView
from django.contrib.auth.views import LogoutView
from django.contrib.staticfiles import finders
from django.db.models import Count
from django.db.models.functions import TruncDate
from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.templatetags.static import static
from django.utils.timezone import now
from django.views.decorators.http import require_POST
from openpyxl import Workbook
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
     PageBreak
)
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph,
    Image, Spacer
)
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .forms import QuickRegistrationForm
from .forms import RegistrantForm
from .utils import *
from .serializers_new import serialize_registrant
from .decorators import require_api_key


def home(request):
    # 🟢 DOWNLOAD FEATURE – Full Agenda PDF with Cover, Logo, Header, Footer
    if request.GET.get("download") == "schedule":
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="Kenya_Software_Summit_Schedule.pdf"'

        logo_url = static('images/summit_logo_dark.webp')
        logo_path = finders.find('images/summit_logo_dark.webp') or logo_url

        def add_header_footer(canvas_obj, doc):
            width, height = A4
            try:
                if logo_path and os.path.exists(logo_path):
                    canvas_obj.drawImage(
                        logo_path,
                        x=40, y=height - 60,
                        width=70, height=30,
                        preserveAspectRatio=True,
                        mask='auto'
                    )
            except Exception as e:
                print("Logo load error:", e)

            canvas_obj.setFont("Helvetica-Bold", 9)
            canvas_obj.setFillColor(colors.HexColor("#1E6B52"))
            canvas_obj.drawRightString(width - 40, height - 45, "Kenya Software Summit 2025")

            canvas_obj.setStrokeColor(colors.lightgrey)
            canvas_obj.setLineWidth(0.5)
            canvas_obj.line(40, 50, width - 40, 50)

            canvas_obj.setFont("Helvetica", 8.5)
            canvas_obj.setFillColor(colors.grey)
            canvas_obj.drawString(40, 38, "Connecting minds, Shaping software, Driving growth")
            canvas_obj.drawRightString(width - 40, 38, f"Page {doc.page}")

        doc = SimpleDocTemplate(
            response,
            pagesize=A4,
            leftMargin=40,
            rightMargin=40,
            topMargin=90,
            bottomMargin=50,
        )

        elements = []
        styles = getSampleStyleSheet()

        # Styles (smaller spacing, tighter layout)
        title_style = ParagraphStyle(
            name='TitleStyle',
            parent=styles['Heading1'],
            alignment=1,
            textColor=colors.HexColor("#1E6B52"),
            fontSize=20,
            spaceAfter=10,
        )
        subtitle_style = ParagraphStyle(
            name='Subtitle',
            parent=styles['Heading2'],
            textColor=colors.HexColor("#1E6B52"),
            spaceBefore=6,
            spaceAfter=6,
        )
        normal_center = ParagraphStyle(
            name='NormalCenter',
            parent=styles['Normal'],
            alignment=1,
            fontSize=11,
            spaceAfter=8,
        )

        # 🟣 COVER PAGE (tighter spacing)
        try:
            if logo_path and os.path.exists(logo_path):
                elements.append(Spacer(1, 100))
                elements.append(Image(logo_path, width=100, height=50))
            else:
                elements.append(Spacer(1, 120))
        except Exception:
            elements.append(Spacer(1, 120))

        elements.append(Spacer(1, 20))
        elements.append(Paragraph("Kenya Software Summit 2025", title_style))
        elements.append(Paragraph("Official 3-Day Agenda", normal_center))
        elements.append(Spacer(1, 10))
        elements.append(Paragraph("November 10 – 12, 2025 | Eldoret, Kenya", normal_center))
        elements.append(Spacer(1, 200))
        elements.append(PageBreak())

        # 🔹 Compact table styling
        def make_table(data):
            t = Table(data, colWidths=[70, 170, 220])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1E6B52")),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('TOPPADDING', (0, 0), (-1, 0), 4),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 4),
                ('FONTSIZE', (0, 1), (-1, -1), 9.5),
                ('TOPPADDING', (0, 1), (-1, -1), 2),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 2),
                ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
                ('GRID', (0, 0), (-1, -1), 0.25, colors.grey),
            ]))
            return t

        # --- DAY 1 ---
        elements.append(Paragraph("Day 1 – November 10", subtitle_style))
        day1 = [
            ["Time", "Session", "Details"],
            ["All Day", "Exhibition", "Ongoing at Innovation Expo Area"],
            ["7:30 AM", "Registration & Morning Networking", "Main Hall"],
            ["8:30 AM", "Opening Ceremony", "Anthems, Welcoming Remarks, Keynote Address"],
            ["9:50 AM", "Software Ecosystem Landscape", "Baseline Survey, Global Trends, Panel Discussion"],
            ["10:45 AM", "Tea Break", ""],
            ["11:15 AM", "Software Quality & IP", "Frameworks, Policies, Data Adequacy"],
            ["12:15 PM", "Fireside Chat", "Industry Leaders' Insights"],
            ["1:00 PM", "Lunch Break", "Main Lobby"],
            ["2:00 PM", "Tech Labs", "Workshops & Partner Sessions"],
            ["5:30 PM", "Business Matchmaking", "Networking Event"],
        ]
        elements.append(make_table(day1))
        elements.append(Spacer(1, 10))

        # --- DAY 2 ---
        elements.append(Paragraph("Day 2 – November 11", subtitle_style))
        day2 = [
            ["Time", "Session", "Details"],
            ["All Day", "Exhibition", "Open to all registered delegates"],
            ["8:00 AM", "Registration & Networking", "Main Hall"],
            ["8:30 AM", "Day 1 Recap & Highlights", ""],
            ["9:00 AM", "Academia Panel", "Talent Strategies (Higher Ed & TVET)"],
            ["10:00 AM", "Tea Break", ""],
            ["10:30 AM", "Digital / Remote Work", "Future of Jobs, Labour Rights, Policy Directions"],
            ["11:30 AM", "Blockchain Technology", "Virtual Assets, Legal Framework, Q&A"],
            ["1:00 PM", "Lunch Break", "Main Lobby"],
            ["2:00 PM", "Software Innovation Opportunities", "DevSecOps, Creative Economy, Accessibility"],
            ["4:00 PM", "Gala Dinner & Recognition", "Main Hall"],
        ]
        elements.append(make_table(day2))
        elements.append(Spacer(1, 10))

        # --- DAY 3 ---
        elements.append(Paragraph("Day 3 – November 12", subtitle_style))
        day3 = [
            ["Time", "Session", "Details"],
            ["All Day", "Exhibition", "Innovation Expo"],
            ["7:30 AM", "Software Advisory Council Breakfast", "Promoting Software Industry Dialogue"],
            ["8:30 AM", "Startup Support Panel", "Next-Gen Developers & Startup Ecosystem"],
            ["10:30 AM", "Tea Break", ""],
            ["11:00 AM", "Software Global Export", "Panel: Building for Export Markets"],
            ["12:15 PM", "Hackathon Finals & Awards", "Startup Showcase Presentations"],
            ["1:00 PM", "Lunch Break", "Main Lobby"],
            ["2:00 PM", "Closing Keynote & Ceremony", "Call to Action, Closing Remarks, Press Conference"],
            ["4:00 PM", "Tea Break & Guest Departures", "Main Lobby"],
        ]
        elements.append(make_table(day3))
        elements.append(Spacer(1, 12))
        elements.append(Paragraph(
            "© 2025 Kenya Software Summit – Visit the official website for updates.",
            ParagraphStyle(name="FooterText", parent=styles["Normal"], fontSize=9, textColor=colors.grey)
        ))

        doc.build(elements, onFirstPage=add_header_footer, onLaterPages=add_header_footer)
        return response

    # 🟢 END DOWNLOAD FEATURE

    # 🔹 Existing registration logic (unchanged)
    if request.method == 'POST':
        form = QuickRegistrationForm(request.POST)

        if form.is_valid():
            registrant = form.save(commit=False)

            # Save interests properly
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
                        {"success": False, "message": "Registration saved but email could not be sent."},
                        status=500
                    )
                messages.warning(request, "Registered, but confirmation email failed.")

            if request.headers.get("x-requested-with") == "XMLHttpRequest":
                return JsonResponse({"success": True, "message": "Registration successful"})

            messages.success(request, "Registration successful")
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


    return render(request, "summit/home.html", {
        'form': form,
        'gallery_items': gallery_items,
        'partners': partners,
        'days': days,
        'interest_choices': Registrant.INTEREST_CHOICES,
    })


import qrcode
from barcode import Code128
from barcode.writer import ImageWriter
from io import BytesIO
from django.http import FileResponse, Http404
from django.contrib.admin.views.decorators import staff_member_required
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import landscape, A7
from reportlab.lib.utils import ImageReader
from reportlab.lib import colors
from .models import Registrant
import os


@staff_member_required
def generate_badge(request, registrant_id):
    try:
        registrant = Registrant.objects.get(pk=registrant_id)
    except Registrant.DoesNotExist:
        raise Http404("Registrant not found")

    # --- Data prep ---
    full_name = registrant.get_full_name() or ""
    org_type = registrant.display_org_type() or ""
    job_title = registrant.job_title or ""
    interests = registrant.display_interests() or ""
    email = registrant.email or ""
    phone = registrant.phone or ""

    # --- Generate QR Code ---
    qr_data = (
        f"Name: {full_name}\nEmail: {email}\nPhone: {phone}\n"
        f"Organization: {org_type}\nJob Title: {job_title}\nInterests: {interests}"
    )
    qr_img = qrcode.make(qr_data)
    qr_buffer = BytesIO()
    qr_img.save(qr_buffer, format="PNG")
    qr_buffer.seek(0)

    # --- Generate Barcode ---
    barcode_data = str(registrant.id)
    barcode_buffer = BytesIO()
    barcode = Code128(barcode_data, writer=ImageWriter())
    barcode.write(barcode_buffer)
    barcode_buffer.seek(0)

    # --- Create Badge PDF ---
    pdf_buffer = BytesIO()
    c = canvas.Canvas(pdf_buffer, pagesize=landscape(A7))
    width, height = landscape(A7)

    # --- Background ---
    c.setFillColorRGB(1, 1, 1)
    c.rect(0, 0, width, height, fill=1)

    # --- Header Bar ---
    header_height = 40
    c.setFillColorRGB(0.05, 0.2, 0.45)  # dark blue
    c.rect(0, height - header_height, width, header_height, fill=1, stroke=0)

    # --- Summit Logo ---
    logo_path = os.path.join(os.getcwd(), "static", "images", "summit_logo_dark.webp")
    if os.path.exists(logo_path):
        logo = ImageReader(logo_path)
        logo_width, logo_height = 48, 24
        logo_y = height - (header_height / 2 + logo_height / 2) + 2
        c.drawImage(logo, 12, logo_y, width=logo_width, height=logo_height, mask='auto')

    # --- Summit Title (aligned with logo center) ---
    c.setFillColor(colors.whitesmoke)
    c.setFont("Helvetica-Bold", 10)
    title_y = height - (header_height / 2) + 3  # vertical alignment fix
    c.drawString(80, title_y, "Kenya Software Summit 2025")

    # --- Info Section ---
    c.setFillColor(colors.black)
    y_start = height - header_height - 15

    c.setFont("Helvetica-Bold", 9)
    c.drawCentredString(width / 2, y_start, full_name[:45])

    c.setFont("Helvetica", 8)
    c.drawCentredString(width / 2, y_start - 12, org_type[:55])
    c.drawCentredString(width / 2, y_start - 24, job_title[:55])

    if interests:
        c.setFont("Helvetica-Oblique", 7)
        text = interests[:70] + ("..." if len(interests) > 70 else "")
        c.drawCentredString(width / 2, y_start - 38, text)

    # --- Divider Line ---
    c.setStrokeColor(colors.lightgrey)
    c.line(10, 40, width - 10, 40)

    # --- QR & Barcode ---
    qr_image = ImageReader(qr_buffer)
    barcode_image = ImageReader(barcode_buffer)
    c.drawImage(qr_image, 10, 15, width=55, height=55, mask='auto')
    c.drawImage(barcode_image, width - 95, 20, width=85, height=35, mask='auto')

    # --- Footer ---
    c.setFont("Helvetica", 6)
    c.setFillColor(colors.grey)
    c.drawCentredString(width / 2, 10, "Scan QR or Barcode for summit check-in")

    # --- Save ---
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


@staff_member_required
def dashboard_view(request):
    total_users = Registrant.objects.count()
    updates_count = Registrant.objects.filter(updates_opt_in=True).count()

    registrants = Registrant.objects.all().order_by('-created_at')

    context = {
        "total_users": total_users,
        "updates_count": updates_count,
        "registrants": registrants,
        "org_type_choices": Registrant.ORG_TYPE_CHOICES,  # ✅ send choices
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







from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.views.decorators.http import require_POST
from .models import SummitGallery
from .forms import GalleryForm

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



# Speaker

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import SummitSpeaker
from .forms import SpeakerForm


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

#---------------------------------
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import SummitPartner

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
  
#--------------------------------------------



from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import SummitScheduleDay, SummitTimeSlot, SummitSession, SummitPanelist
from .forms import ScheduleDayForm, TimeSlotForm, SessionForm, PanelistForm
from django.forms import inlineformset_factory

PanelistFormSet = inlineformset_factory(
    SummitSession, SummitPanelist, form=PanelistForm, extra=1, can_delete=True
)

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


# registration API function
@require_api_key
def get_registrants(request):
    """
    GET /reg-service/registrations/
    Returns a list of registered participants for Patherways Technologies
    """
    if request.method != "GET":
        return JsonResponse({"detail": "Method not allowed."}, status=405)

    registrants = Registrant.objects.all().order_by("-created_at")

    data = [serialize_registrant(r) for r in registrants]

    return JsonResponse({"count": len(data), "registrants": data}, safe=False)