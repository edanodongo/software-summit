from .forms import QuickRegistrationForm
from .utils import *
from openpyxl import Workbook
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models.functions import TruncDate
from django.http import HttpResponse
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph,
    Image, Spacer
)
from reportlab.lib.styles import getSampleStyleSheet
from django.utils.timezone import now
from django.contrib.auth.views import LogoutView
from django.contrib.auth.views import LoginView
import os

from django.db.models import Count
from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from .models import Registrant

from django.http import JsonResponse, Http404
from django.views.decorators.http import require_POST


def home(request):
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

            # Send confirmation email (safe handling)
            try:
                send_confirmation_email(registrant)  # make sure you implement this
            except Exception as e:
                print("Email Send error:", e)
                if request.headers.get("x-requested-with") == "XMLHttpRequest":
                    return JsonResponse(
                        {"success": False, "message": "Registration saved but email could not be sent."}, 
                        status=500
                    )
                messages.warning(request, "Registered, but confirmation email failed.")

            # AJAX response
            if request.headers.get("x-requested-with") == "XMLHttpRequest":
                return JsonResponse({"success": True, "message": "Registration successful!"})

            messages.success(request, "Registration successful!")
            return redirect('home')

        else:
            # Return errors if AJAX
            if request.headers.get("x-requested-with") == "XMLHttpRequest":
                return JsonResponse({"success": False, "errors": form.errors}, status=400)

            messages.error(request, "There was a problem with your registration.")
    else:
        form = QuickRegistrationForm()

    return render(request, "summit/home.html", {
        'form': form,
        'interest_choices': Registrant.INTEREST_CHOICES,
    })



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

    registrants = Registrant.objects.all().order_by('-created_at')  # newest first

    context = {
        "total_users": total_users,
        "updates_count": updates_count,
        "registrants": registrants,
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
    return render(request, "summit/speakers.html")

def media(request):
    return render(request, "summit/gallery.html")