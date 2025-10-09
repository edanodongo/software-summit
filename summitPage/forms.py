from django import forms
from .models import Registrant
from django.core.exceptions import ValidationError


class QuickRegistrationForm(forms.ModelForm):
    # Enforce required fields
    national_id_number = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'National ID Number',
        })
    )

    national_id_scan = forms.FileField(
        required=True,
        widget=forms.FileInput(attrs={'class': 'form-control'}),
        label="Upload Scanned National ID (JPG/PDF)"
    )

    passport_photo = forms.FileField(
        required=True,
        widget=forms.FileInput(attrs={'class': 'form-control'}),
        label="Upload Passport Photo (JPG/PDF)"
    )

    interests = forms.MultipleChoiceField(
        choices=Registrant.INTEREST_CHOICES,
        widget=forms.CheckboxSelectMultiple,
    )
    updates_opt_in = forms.BooleanField(required=False)

    other_organization_type = forms.CharField(
    required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control mt-2',
            'placeholder': 'Please specify...',
        })
    )
    other_interest = forms.CharField(
    required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control mt-2',
            'placeholder': 'Please specify...',
        })
    )

    class Meta:
        model = Registrant
        fields = [
            'title', 'first_name', 'second_name',
            'email', 'phone',
            'organization_type', 'other_organization_type',
            'job_title',
            'interests', 'other_interest',
            'accessibility_needs', 'updates_opt_in'
        ]
        widgets = {
            'title': forms.Select(attrs={'class': 'form-select'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
            'second_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Other Names'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email Address'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'}),
            'organization_type': forms.Select(attrs={'class': 'form-select'}),
            "other_organization_type": forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Institution name'}),
            'job_title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Job Title / Role'}),
            'accessibility_needs': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Accessibility/Dietary Needs (optional)'}),
        }

    # ✅ File validation helper
    def validate_file(self, file, allowed_extensions):
        if not file:
            return
        max_size_mb = 5
        if file.size > max_size_mb * 1024 * 1024:
            raise ValidationError(f"File size should not exceed {max_size_mb} MB.")

        ext = file.name.split('.')[-1].lower()
        if ext not in allowed_extensions:
            allowed = ", ".join(allowed_extensions)
            raise ValidationError(f"Unsupported file format. Allowed types: {allowed}")

    # Individual field validators
    def clean_national_id_scan(self):
        file = self.cleaned_data.get("national_id_scan")
        if not file:
            raise ValidationError("Please upload your scanned national ID.")
        self.validate_file(file, allowed_extensions=["jpg", "jpeg", "png", "pdf"])
        return file

    def clean_passport_photo(self):
        file = self.cleaned_data.get("passport_photo")
        if not file:
            raise ValidationError("Please upload your passport photo.")
        self.validate_file(file, allowed_extensions=["jpg", "jpeg", "png", "pdf"])
        return file

    def clean_national_id_number(self):
        id_number = self.cleaned_data.get('national_id_number', '').strip()
        if not id_number:
            raise ValidationError("Please enter your National ID number.")
        if not id_number.isdigit():
            raise ValidationError("National ID number must contain only digits.")
        if len(id_number) < 6:
            raise ValidationError("Please enter a valid National ID number.")
        return id_number


    def clean(self):
        cleaned_data = super().clean()
        organization_type = cleaned_data.get("organization_type")
        other_organization_type = cleaned_data.get("other_organization_type")
        interests = cleaned_data.get("interests") or []
        other_interest = cleaned_data.get("other_interest")

        # Require other org type only when "other" is selected
        if organization_type == "other" and not other_organization_type:
            self.add_error(
                "other_organization_type",
                "Please specify your organization type."
            )

        # Require other interest only when "others" is selected
        if "others" in interests and not other_interest:
            self.add_error(
                "other_interest",
                "Please specify your interest."
            )

        return cleaned_data

from django import forms
from .models import Registration


class RegistrantForm(forms.ModelForm):
    interests = forms.MultipleChoiceField(
        choices=Registration.INTEREST_CHOICES,
        widget=forms.CheckboxSelectMultiple,
    )
    updates_opt_in = forms.BooleanField(required=False)

    other_organization_type = forms.CharField(
        required=False,  # always visible, required only if org_type == "other"
        widget=forms.TextInput(attrs={
            'class': 'form-control mt-2',
            'placeholder': 'Please specify...',
        })
    )
    other_interest = forms.CharField(
        required=False,  # hidden by JS until "Others" is selected
        widget=forms.TextInput(attrs={
            'class': 'form-control mt-2',
            'placeholder': 'Please specify...',
        })
    )

    class Meta:
        model = Registration
        fields = [
            'title', 'first_name', 'second_name',
            'email', 'phone',
            'organization_type', 'other_organization_type',
            'job_title',
            'interests', 'other_interest',
            'accessibility_needs', 'updates_opt_in'
        ]
        widgets = {
            'title': forms.Select(attrs={'class': 'form-select'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
            'second_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Other Names'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email Address'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'}),
            'organization_type': forms.Select(attrs={'class': 'form-select'}),
            'job_title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Job Title / Role'}),
            'accessibility_needs': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Accessibility/Dietary Needs (optional)'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        organization_type = cleaned_data.get("organization_type")
        other_organization_type = cleaned_data.get("other_organization_type")
        interests = cleaned_data.get("interests") or []
        other_interest = cleaned_data.get("other_interest")

        # Require other org type only when "other" is selected
        if organization_type == "other" and not other_organization_type:
            self.add_error(
                "other_organization_type",
                "Please specify your Institution type."
            )

        # Require other interest only when "others" is selected
        if "others" in interests and not other_interest:
            self.add_error(
                "other_interest",
                "Please specify your interest."
            )

        return cleaned_data



# Gallery


from django import forms
from .models import SummitGallery

class GalleryForm(forms.ModelForm):
    class Meta:
        model = SummitGallery
        fields = ['title', 'image', 'description', 'is_active', 'order']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'order': forms.NumberInput(attrs={'class': 'form-control'}),
        }

# Partner

from django import forms
from .models import SummitPartner

class PartnerForm(forms.ModelForm):
    class Meta:
        model = SummitPartner
        fields = ["name", "logo", "website", "order", "is_active"]



#------------------------------------------
# Schedule

from django import forms
from .models import SummitScheduleDay, SummitTimeSlot, SummitSession, SummitPanelist

class ScheduleDayForm(forms.ModelForm):
    class Meta:
        model = SummitScheduleDay
        fields = ["title", "date", "is_active"]
        widgets = {"date": forms.DateInput(attrs={"type": "date"})}

class TimeSlotForm(forms.ModelForm):
    class Meta:
        model = SummitTimeSlot
        fields = ["day", "start_time", "end_time", "label", "duration"]
        widgets = {
            "start_time": forms.TimeInput(attrs={"type": "time"}),
            "end_time": forms.TimeInput(attrs={"type": "time"}),
        }

class SessionForm(forms.ModelForm):
    class Meta:
        model = SummitSession
        fields = ["session_type", "title", "description", "venue", "is_break", "order"]

class PanelistForm(forms.ModelForm):
    class Meta:
        model = SummitPanelist
        fields = ["role", "name", "organization", "order"]


#------------------------------
# speakers

from django import forms
from .models import SummitSpeaker

class SpeakerForm(forms.ModelForm):
    class Meta:
        model = SummitSpeaker
        fields = [
            "full_name",
            "position",
            "organization",
            "track",
            "topic",
            "summary",
            "bio",
            "photo",
            "linkedin_url",
            "twitter_url",
        ]
        widgets = {
            "full_name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Full name"}),
            "position": forms.TextInput(attrs={"class": "form-control", "placeholder": "Position / Title"}),
            "organization": forms.TextInput(attrs={"class": "form-control", "placeholder": "Organization"}),
            "track": forms.TextInput(attrs={"class": "form-control", "placeholder": "Track or Role"}),
            "topic": forms.TextInput(attrs={"class": "form-control", "placeholder": "Talk Topic"}),
            "summary": forms.Textarea(attrs={"class": "form-control", "rows": 2, "placeholder": "Short summary"}),
            "bio": forms.Textarea(attrs={"class": "form-control", "rows": 4, "placeholder": "Speaker bio"}),
            "linkedin_url": forms.URLInput(attrs={"class": "form-control", "placeholder": "LinkedIn profile URL"}),
            "twitter_url": forms.URLInput(attrs={"class": "form-control", "placeholder": "Twitter profile URL"}),
        }
