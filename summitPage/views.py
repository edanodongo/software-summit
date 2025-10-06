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
from django.contrib.admin.views.decorators import staff_member_required
from .models import Registrant

from django.http import JsonResponse, Http404
from django.views.decorators.http import require_POST

from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import RegistrantForm

from django.http import HttpResponse, JsonResponse
from django.templatetags.static import static
from django.contrib.staticfiles import finders
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
)
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
import os


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
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1E6B52")),
                ('TEXTCOLOR', (0,0), (-1,0), colors.white),
                ('ALIGN', (0,0), (-1,-1), 'LEFT'),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('FONTSIZE', (0,0), (-1,0), 11),
                ('TOPPADDING', (0,0), (-1,0), 4),
                ('BOTTOMPADDING', (0,0), (-1,0), 4),
                ('FONTSIZE', (0,1), (-1,-1), 9.5),
                ('TOPPADDING', (0,1), (-1,-1), 2),
                ('BOTTOMPADDING', (0,1), (-1,-1), 2),
                ('BACKGROUND', (0,1), (-1,-1), colors.whitesmoke),
                ('GRID', (0,0), (-1,-1), 0.25, colors.grey),
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
                return JsonResponse({"success": True, "message": "Registration successful!"})

            messages.success(request, "Registration successful!")
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


# @staff_member_required
# def dashboard_view(request):
#     total_users = Registration.objects.count()
#     updates_count = Registration.objects.filter(updates_opt_in=True).count()

#     registrants = Registration.objects.all().order_by('-created_at')  # newest first

#     context = {
#         "total_users": total_users,
#         "updates_count": updates_count,
#         "registrants": registrants,
#     }
#     return render(request, "summit/dashboard_new.html", context)


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
    return render(request, "summit/speakers.html")

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





# from rest_framework import viewsets, permissions
# from .models import *
# from .serializers import *

# # All endpoints are PUBLIC for now (AllowAny)

# class EventViewSet(viewsets.ModelViewSet):
#     queryset = Event.objects.all()
#     serializer_class = EventSerializer
#     permission_classes = [permissions.AllowAny]

# class TrackViewSet(viewsets.ModelViewSet):
#     queryset = Track.objects.all()
#     serializer_class = TrackSerializer
#     permission_classes = [permissions.AllowAny]

# class SessionViewSet(viewsets.ModelViewSet):
#     queryset = Session.objects.all()
#     serializer_class = SessionSerializer
#     permission_classes = [permissions.AllowAny]

# class SpeakerViewSet(viewsets.ModelViewSet):
#     queryset = Speaker.objects.all()
#     serializer_class = SpeakerSerializer
#     permission_classes = [permissions.AllowAny]

# class ExhibitorViewSet(viewsets.ModelViewSet):
#     queryset = Exhibitor.objects.all()
#     serializer_class = ExhibitorSerializer
#     permission_classes = [permissions.AllowAny]

# class SponsorViewSet(viewsets.ModelViewSet):
#     queryset = Sponsor.objects.all()
#     serializer_class = SponsorSerializer
#     permission_classes = [permissions.AllowAny]

# class RegistrationViewSet(viewsets.ModelViewSet):
#     queryset = Registration.objects.all()
#     serializer_class = RegistrationSerializer
#     permission_classes = [permissions.AllowAny]

# class TicketViewSet(viewsets.ModelViewSet):
#     queryset = Ticket.objects.all()
#     serializer_class = TicketSerializer
#     permission_classes = [permissions.AllowAny]

# class OrderViewSet(viewsets.ModelViewSet):
#     queryset = Order.objects.all()
#     serializer_class = OrderSerializer

#     def perform_create(self, serializer):
#         order = serializer.save()
#         # Issue tickets automatically for each item in order
#         Ticket.objects.create(
#             order=order,
#             ticket_type=order.ticket_type,  # or from your serializer input
#             holder=order.registration
#         )

#     permission_classes = [permissions.AllowAny]

# class PaymentViewSet(viewsets.ModelViewSet):
#     queryset = Payment.objects.all()
#     serializer_class = PaymentSerializer
#     permission_classes = [permissions.AllowAny]

# class ConnectionViewSet(viewsets.ModelViewSet):
#     queryset = ConnectionRequest.objects.all()
#     serializer_class = ConnectionSerializer
#     permission_classes = [permissions.AllowAny]

# class ChatMessageViewSet(viewsets.ModelViewSet):
#     queryset = ChatMessage.objects.all()
#     serializer_class = ChatMessageSerializer
#     permission_classes = [permissions.AllowAny]

# class PollViewSet(viewsets.ModelViewSet):
#     queryset = Poll.objects.all()
#     serializer_class = PollSerializer
#     permission_classes = [permissions.AllowAny]

# class PollOptionViewSet(viewsets.ModelViewSet):
#     queryset = PollOption.objects.all()
#     serializer_class = PollOptionSerializer
#     permission_classes = [permissions.AllowAny]

# class PollVoteViewSet(viewsets.ModelViewSet):
#     queryset = PollResponse.objects.all()
#     serializer_class = PollVoteSerializer
#     permission_classes = [permissions.AllowAny]

# class QnAViewSet(viewsets.ModelViewSet):
#     queryset = Question.objects.all()
#     serializer_class = QnASerializer
#     permission_classes = [permissions.AllowAny]

# class FeedbackViewSet(viewsets.ModelViewSet):
#     queryset = Feedback.objects.all()
#     serializer_class = FeedbackSerializer
#     permission_classes = [permissions.AllowAny]

# class NotificationViewSet(viewsets.ModelViewSet):
#     queryset = Notification.objects.all()
#     serializer_class = NotificationSerializer
#     permission_classes = [permissions.AllowAny]

