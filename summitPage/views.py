from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login   # rename login
from django.contrib import messages
from django.contrib.auth.decorators import login_required

# registrations/views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import QuickRegistrationForm

def home(request):
    if request.method == 'POST':
        form = QuickRegistrationForm(request.POST)
        if form.is_valid():
            registrant = form.save()
            # send confirmation email
            send_confirmation_email(registrant)
            messages.success(request, "Registration successful! Check your email for confirmation.")
            return redirect('home')
    else:
        form = QuickRegistrationForm()
    return render(request, "summit/home.html", {'form': form})

# registrations/views.py
from django.http import HttpResponse
from django.shortcuts import render

def unsubscribe_view(request, token):
    try:
        registrant = Registrant.objects.get(unsubscribe_token=token)
        registrant.updates_opt_in = False
        registrant.save()
        return render(request, "registrations/unsubscribe.html")
    except Registrant.DoesNotExist:
        return HttpResponse("<h2>Invalid unsubscribe link.</h2>", status=400)


# registrations/views.py
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models import Count
from django.db.models.functions import TruncDate
from .models import Registrant

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


# registrations/views.py
import csv
from django.http import HttpResponse

def export_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="registrants.csv"'

    writer = csv.writer(response)
    writer.writerow([
        'Full Name', 'Email', 'Phone', 'Organization',
        'Job Title', 'Category', 'Interests',
        'Accessibility Needs', 'Updates Opt-in', 'Date'
    ])

    for r in Registrant.objects.all():
        writer.writerow([
            r.full_name, r.email, r.phone,
            r.organization, r.job_title, r.category,
            ", ".join(r.interests), r.accessibility_needs,
            "Yes" if r.updates_opt_in else "No",
            r.created_at.strftime("%Y-%m-%d")
        ])

    return response

from openpyxl import Workbook
from django.http import HttpResponse

def export_excel(request):
    wb = Workbook()
    ws = wb.active
    ws.title = "Registrants"

    headers = [
        'Full Name', 'Email', 'Phone', 'Organization',
        'Job Title', 'Category', 'Interests',
        'Accessibility Needs', 'Updates Opt-in', 'Date'
    ]
    ws.append(headers)

    for r in Registrant.objects.all():
        ws.append([
            r.full_name, r.email, r.phone,
            r.organization, r.job_title, r.category,
            ", ".join(r.interests), r.accessibility_needs,
            "Yes" if r.updates_opt_in else "No",
            r.created_at.strftime("%Y-%m-%d")
        ])

    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response['Content-Disposition'] = 'attachment; filename=registrants.xlsx'
    wb.save(response)
    return response

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from django.http import HttpResponse

def export_pdf(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="registrants.pdf"'

    p = canvas.Canvas(response, pagesize=letter)
    width, height = letter

    y = height - 50
    p.setFont("Helvetica-Bold", 14)
    p.drawString(50, y, "Summit Registrants")
    y -= 30

    p.setFont("Helvetica", 10)
    for r in Registrant.objects.all():
        text = f"{r.full_name} | {r.email} | {r.category} | {', '.join(r.interests)}"
        p.drawString(50, y, text)
        y -= 15
        if y < 50:  # new page if space runs out
            p.showPage()
            y = height - 50

    p.save()
    return response




# registrations/views.py
from django.core.mail import send_mass_mail
from django.contrib.admin.views.decorators import staff_member_required
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import BulkEmailForm
from .models import Registrant

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




























def login_view(request):   
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user:
            auth_login(request, user)   # ✅ use renamed login function
            return redirect("dashboard")
        else:
            messages.error(request, "Invalid credentials")
    return render(request, "summit/samples/login.html")

@login_required
def dashboard(request):
    registrations = Registration.objects.all().order_by("-created_at")
    return render(request, "summit/samples/dashboard.html", {"registrations": registrations})


# View for event page
def landingEvent(request):
    return render(request, 'landingpage/index.html')

def summit(request):
    return render(request, 'landingpage/summit.html')

def about(request):
    return render(request, 'summit/samples/about.html')

def agenda(request):
    return render(request, 'summit/samples/agenda.html')

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
