from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import RegistrationForm
from .models import Registration

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login   # rename login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import RegistrationForm
from .models import Registration

def home(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Registration successful! 🎉")
            return redirect("home")
    else:
        form = RegistrationForm()
    return render(request, "summit/home.html", {"form": form})

def login_view(request):   # ✅ renamed
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user:
            auth_login(request, user)   # ✅ use renamed login function
            return redirect("dashboard")
        else:
            messages.error(request, "Invalid credentials")
    return render(request, "summit/login.html")

@login_required
def dashboard(request):
    registrations = Registration.objects.all().order_by("-created_at")
    return render(request, "summit/dashboard.html", {"registrations": registrations})


# View for event page
def landingEvent(request):
    return render(request, 'landingpage/index.html')

def summit(request):
    return render(request, 'landingpage/summit.html')

def about(request):
    return render(request, 'summit/about.html')

def agenda(request):
    return render(request, 'summit/agenda.html')

def base(request):
    return render(request, 'summit/base.html')

def contact(request):
    return render(request, 'summit/contact.html')

def features(request):
    return render(request, 'summit/features.html')

def media(request):
    return render(request, 'summit/media.html')

def partners(request):
    return render(request, 'summit/partners.html')

def register(request):
    return render(request, 'summit/register.html')

def speakers(request):
    return render(request, 'summit/speakers.html')

def travel(request):
    return render(request, 'summit/travel.html')
