from django import forms
from .models import Registration

class RegistrationForm(forms.ModelForm):
    class Meta:
        model = Registration
        fields = ["first_name", "last_name", "email", "phone", "reg_type", "organization"]
        widgets = {
            "first_name": forms.TextInput(attrs={"class": "form-control rounded-3", "placeholder": "First Name"}),
            "last_name": forms.TextInput(attrs={"class": "form-control rounded-3", "placeholder": "Last Name"}),
            "email": forms.EmailInput(attrs={"class": "form-control rounded-3", "placeholder": "Email Address"}),
            "phone": forms.TextInput(attrs={"class": "form-control rounded-3", "placeholder": "Phone Number"}),
            "reg_type": forms.Select(attrs={"class": "form-select rounded-3"}),
            "organization": forms.TextInput(attrs={"class": "form-control rounded-3", "placeholder": "Organization"}),
        }
