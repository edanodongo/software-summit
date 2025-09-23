from .forms import QuickRegistrationForm
from .utils import *

def home(request):
    if request.method == 'POST':
        form = QuickRegistrationForm(request.POST)

        if form.is_valid():
            registrant = form.save(commit=False)

            # Save interests cleanly
            interests = form.cleaned_data.get("interests", [])
            if "other" in interests and form.cleaned_data.get("other_interest"):
                interests = [i for i in interests if i != "other"]
                interests.append("other")
                registrant.other_interest = form.cleaned_data["other_interest"]

            registrant.interests = interests
            registrant.save()

            # send email
            try:
                send_confirmation_email(registrant)
            except Exception as e:
                print("Email Send error:", e)
                if request.headers.get("x-requested-with") == "XMLHttpRequest":
                    return JsonResponse({"success": False, "message": "Registration saved but email could not be sent."}, status=500)
                messages.warning(request, "Registered, but confirmation email failed.")



            if request.headers.get("x-requested-with") == "XMLHttpRequest":
                return JsonResponse({"success": True, "message": "Registration successful!"})

            messages.success(request, "Registration successful!")\



            return redirect('home')

        else:
            if request.headers.get("x-requested-with") == "XMLHttpRequest":
                return JsonResponse({"success": False, "errors": form.errors}, status=400)

            messages.error(request, "There was a problem with your registration.")
    else:
        form = QuickRegistrationForm()

    return render(request, "summit/home.html", {
        'form': form,
        'interest_choices': Registrant.INTEREST_CHOICES,
    })


def unsubscribe_view(request, token):
    try:
        registrant = Registrant.objects.get(unsubscribe_token=token)
        registrant.updates_opt_in = False
        registrant.save()
        return render(request, "summit/unsubscribe.html")
    except Registrant.DoesNotExist:
        return HttpResponse("<h2>Invalid unsubscribe link.</h2>", status=400)


from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models.functions import TruncDate


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


from openpyxl import Workbook


# # === CSV Export ===
# from django.template.loader import render_to_string
# from weasyprint import HTML
# from django.utils import timezone


# def export_registrants_csv(request):
#     registrants = Registrant.objects.all()

#     category_counts = (
#         registrants.values("category")
#         .annotate(count=Count("id"))
#         .order_by()
#     )

#     # Render HTML
#     html_string = render_to_string("summit/print_registrants.html", {
#         "registrants": registrants,
#         "category_counts": list(category_counts),
#         "now": timezone.now(),
#         "pdf_mode": True,  # flag to hide print button
#     })

#     # Convert to PDF
#     html = HTML(string=html_string, base_url=request.build_absolute_uri())
#     pdf = html.write_pdf()

#     # Return as file download
#     response = HttpResponse(pdf, content_type="application/pdf")
#     response["Content-Disposition"] = "attachment; filename=registrants_report.pdf"
#     return response


# === Excel Export ===
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
from django.http import HttpResponse
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph,
    Image, Spacer
)
from reportlab.lib.styles import getSampleStyleSheet
from django.utils.timezone import now
import os


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


def print_registrants(request):
    registrants = Registrant.objects.all()

    # Aggregated counts
    category_counts = (
        registrants.values("category")
        .annotate(count=Count("id"))
        .order_by()
    )

    return render(request, "summit/print_registrants.html", {
        "registrants": registrants,
        "category_counts": list(category_counts),
    })


from django.core.mail import send_mass_mail
from django.contrib.admin.views.decorators import staff_member_required
from django.conf import settings
from django.shortcuts import redirect
from django.contrib import messages
from .forms import BulkEmailForm


@staff_member_required
def bulk_email_view(request):
    if request.method == "POST":
        form = BulkEmailForm(request.POST)
        if form.is_valid():
            subject = form.cleaned_data["subject"]
            message = form.cleaned_data["message"]
            category = form.cleaned_data["category"]

            # Choose recipients based on category
            if category == "all":
                recipients = Registrant.objects.values_list("email", flat=True)
            elif category == "updates":
                recipients = Registrant.objects.filter(updates_opt_in=True).values_list("email", flat=True)
            else:
                recipients = Registrant.objects.filter(category=category).values_list("email", flat=True)

            # Prepare datatuple with unsubscribe links
            datatuple = []
            for email in recipients:
                try:
                    registrant = Registrant.objects.get(email=email)
                    unsubscribe_link = request.build_absolute_uri(registrant.get_unsubscribe_url())
                    message_with_unsub = (
                        f"{message}\n\n---\n"
                        f"To stop receiving these updates, click here: {unsubscribe_link}"
                    )
                except Registrant.DoesNotExist:
                    message_with_unsub = message  # fallback (shouldn’t normally happen)

                datatuple.append((subject, message_with_unsub, settings.DEFAULT_FROM_EMAIL, [email]))

            # Send all at once
            if datatuple:
                send_mass_mail(datatuple, fail_silently=False)
                messages.success(request, f"Bulk email sent to {len(datatuple)} recipients.")
            else:
                messages.warning(request, "No recipients found for this segment.")

            return redirect("bulk_email")
    else:
        form = BulkEmailForm()

    return render(request, "summit/bulk_email.html", {"form": form})


from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count
from django.http import JsonResponse
from django.shortcuts import render
from .models import Registrant


@staff_member_required
def dashboard_view(request):
    total_users = Registrant.objects.count()
    updates_count = Registrant.objects.filter(updates_opt_in=True).count()

    registrants = Registrant.objects.all().order_by('-created_at')

    # Breakdown by category
    category_counts = (
        Registrant.objects.values("category")
        .annotate(count=Count("id"))
        .order_by("category")
    )

    # # Breakdown by interests (if stored as CSV)
    # interests_raw = Registrant.objects.exclude(interests__isnull=True).values_list("interests", flat=True)
    # interest_map = {}
    # for row in interests_raw:
    #     for i in row.split(","):
    #         i = i.strip()
    #         if i:
    #             interest_map[i] = interest_map.get(i, 0) + 1

    # # Registrations over time
    # registrations_over_time = (
    #     Registrant.objects.extra({"date": "date(created_at)"})
    #     .values("date")
    #     .annotate(count=Count("id"))
    #     .order_by("date")
    # )

    context = {
        "total_users": total_users,
        "updates_count": updates_count,
        "category_counts": list(category_counts),
        "registrants": registrants,
        # "interest_counts": interest_map,
        # "registrations_over_time": list(registrations_over_time),
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


from django.contrib.auth.views import LoginView


class SummitLoginView(LoginView):
    template_name = "summit/login.html"


from django.contrib.auth.views import LogoutView


class SummitLogoutView(LogoutView):
    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)


# def login_view(request):
#     if request.method == "POST":
#         username = request.POST.get("username")
#         password = request.POST.get("password")
#         user = authenticate(request, username=username, password=password)
#         if user:
#             auth_login(request, user)   # ✅ use renamed login function
#             return redirect("dashboard")
#         else:
#             messages.error(request, "Invalid credentials")
#     return render(request, "summit/samples/login.html")

# @login_required
# def dashboard(request):
#     registrations = Registration.objects.all().order_by("-created_at")
#     return render(request, "summit/samples/dashboard.html", {"registrations": registrations})


# View for event page
def landingEvent(request):
    return render(request, 'landingpage/index.html')


def summit(request):
    return render(request, 'landingpage/summit.html')


def about(request):
    return render(request, 'summit/samples/about.html')


def agenda(request):
    return render(request, 'summit/agenda.html')


def base(request):
    return render(request, 'summit/samples/base.html')


def contact(request):
    return render(request, 'summit/samples/contact.html')


def features(request):
    return render(request, 'summit/samples/features.html')


def media(request):
    return render(request, 'summit/samples/media.html')


def partners(request):
    return render(request, 'summit/samples/partners.html')


def register(request):
    return render(request, 'summit/samples/register.html')


def speakers(request):
    return render(request, 'summit/samples/speakers.html')


def travel(request):
    return render(request, 'summit/samples/travel.html')
