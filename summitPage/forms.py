from django import forms
from django.core.exceptions import ValidationError
from .models import Registrant,get_category_choices
from .models import SummitSpeaker, Registration, SummitGallery, SummitPartner
from django_countries.widgets import CountrySelectWidget
from .models import Exhibitor, Booth, ExhibitionSection

from .models import SummitScheduleDay, SummitTimeSlot, SummitSession, SummitPanelist

class QuickRegistrationForm(forms.ModelForm):
    # =====================================================
    # 🔹 Custom Field Definitions
    # =====================================================
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
            'class': 'form-control',
            'placeholder': 'Please enter organization/institution name',
        })
    )

    other_interest = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'rows': 3,
            'class': 'form-control',
            'placeholder': 'Please specify...',
        })
    )

    category = forms.ChoiceField(
        choices=get_category_choices,
        required=True,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Registration Category"
    )

    privacy_agreed = forms.BooleanField(
        required=True,
        label='I have read and agree to the Privacy Policy',
        error_messages={'required': 'You must agree to the Privacy Policy to register.'},
    )

    # =====================================================
    # 🔹 Meta Configuration
    # =====================================================
    class Meta:
        model = Registrant
        fields = [
            'title', 'first_name', 'second_name',
            'email', 'phone',
            'organization_type', 'other_organization_type',
            'job_title', 'category',
            'interests', 'other_interest',
            'accessibility_needs', 'updates_opt_in',
            'privacy_agreed',

            # ✅ Added fields that were missing before
            'national_id_number',
            'national_id_scan',
            'passport_photo',
        ]
        widgets = {
            'title': forms.Select(attrs={'class': 'form-select'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
            'second_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Other Names'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email Address'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'}),
            'organization_type': forms.Select(attrs={'class': 'form-select'}),
            'other_organization_type': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Institution name'
            }),
            'job_title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Job Title / Role'}),
            'accessibility_needs': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Accessibility/Dietary Needs (optional)'
            }),
        }

    # =====================================================
    # 🔹 Validation Helpers
    # =====================================================
    def validate_file(self, file, allowed_extensions):
        """Generic file validation utility."""
        if not file:
            return
        max_size_mb = 2
        if file.size > max_size_mb * 1024 * 1024:
            raise ValidationError(f"File size should not exceed {max_size_mb} MB.")

        ext = file.name.split('.')[-1].lower()
        if ext not in allowed_extensions:
            allowed = ", ".join(allowed_extensions)
            raise ValidationError(f"Unsupported file format. Allowed types: {allowed}")

    def clean_national_id_scan(self):
        file = self.cleaned_data.get("national_id_scan")
        if not file:
            raise ValidationError("Please upload your scanned National ID.")
        self.validate_file(file, ["jpg", "jpeg", "png", "pdf"])
        return file

    def clean_passport_photo(self):
        file = self.cleaned_data.get("passport_photo")
        if not file:
            raise ValidationError("Please upload your passport photo.")
        self.validate_file(file, ["jpg", "jpeg", "png", "pdf"])
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

    # =====================================================
    # 🔹 Cross-field Validation
    # =====================================================
    def clean(self):
        cleaned_data = super().clean()
        organization_type = cleaned_data.get("organization_type")
        other_organization_type = cleaned_data.get("other_organization_type")
        interests = cleaned_data.get("interests") or []
        other_interest = cleaned_data.get("other_interest")

        # Require "other organization" details when selected
        if organization_type == "other" and not other_organization_type:
            self.add_error("other_organization_type", "Please specify your organization type.")

        # Require "other interest" details when selected
        if "others" in interests and not other_interest:
            self.add_error("other_interest", "Please specify your interest.")

        # Ensure Privacy Policy is agreed to
        if not cleaned_data.get("privacy_agreed"):
            self.add_error("privacy_agreed", "You must agree to the Privacy Policy before continuing.")

        return cleaned_data


# --------------------------------------------

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



# --------------------------------------------
# Gallery
# --------------------------------------------

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

# --------------------------------------------
# Partner
# --------------------------------------------

class PartnerForm(forms.ModelForm):
    class Meta:
        model = SummitPartner
        fields = ["name", "logo", "website", "order", "is_active"]



#------------------------------------------
# Schedule
# --------------------------------------------


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


# --------------------------------------------
# speakers
# --------------------------------------------

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





# --------------------------------------------
# ✅ Exhibitor Registration Form
# --------------------------------------------


class ExhibitorRegistrationForm(forms.ModelForm):
    class Meta:
        model = Exhibitor
        fields = [
            'title', 'first_name', 'second_name', 'email', 'phone',
            'organization_type', 'job_title', 'category',
            'section', 'booth', 'product_description',
            'business_type', 'kra_pin', 'business_registration_doc',
            'international_business_doc', 'country_of_registration',
            'beneficial_owner_details', 'beneficial_owner_doc',
            'national_id_number', 'national_id_scan', 'passport_photo',
            'privacy_agreed',
        ]
        widgets = {
            'country_of_registration': CountrySelectWidget(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        placeholders = {
            'first_name': "Enter your first name",
            'second_name': "Enter your other names (optional)",
            'email': "Enter your email address",
            'phone': "Enter your phone number",
            'organization_type': "Enter your organization or institution name",
            'job_title': "Enter your job title or role",
            'product_description': "Briefly describe your product or service",
            'kra_pin': "Enter your KRA PIN (if Kenyan)",
            'beneficial_owner_details': "List owners/directors with ownership percentages",
            'national_id_number': "Enter your National ID or Passport number",
        }

        for field_name, field in self.fields.items():
            if isinstance(field.widget, (forms.TextInput, forms.EmailInput, forms.Textarea, forms.FileInput)):
                field.widget.attrs.update({'class': 'form-control'})
            elif isinstance(field.widget, forms.Select):
                field.widget.attrs.update({'class': 'form-select'})
            elif isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.update({'class': 'form-check-input'})

            if field_name in placeholders:
                field.widget.attrs['placeholder'] = placeholders[field_name]

        required_fields = [
            'title', 'first_name', 'email', 'phone',
            'organization_type', 'job_title', 'category',
            'section', 'booth', 'national_id_number',
            'national_id_scan', 'passport_photo',
            'country_of_registration', 'privacy_agreed'
        ]
        for f in required_fields:
            self.fields[f].required = True

        # Add frontend min length hints
        self.fields['national_id_number'].widget.attrs['minlength'] = 8
        self.fields['kra_pin'].widget.attrs['minlength'] = 11

        self.fields['booth'].queryset = Booth.objects.filter(is_booked=False)
        self.fields['section'].queryset = ExhibitionSection.objects.all()

        self.fields['category'].empty_label = "Select exhibitor category"
        self.fields['section'].empty_label = "Select exhibition section"
        self.fields['booth'].empty_label = "Choose preferred booth"

    def clean(self):
        cleaned_data = super().clean()
        business_type = cleaned_data.get('business_type')
        kra_pin = cleaned_data.get('kra_pin')
        id_number = cleaned_data.get('national_id_number')
        country = cleaned_data.get('country_of_registration')

        if not country:
            self.add_error('country_of_registration', "Please select the country of registration.")

        if id_number and len(id_number.strip()) < 8:
            self.add_error('national_id_number', "National ID / Passport number must be at least 8 characters long.")

        if business_type == 'local':
            if not kra_pin:
                self.add_error('kra_pin', "KRA PIN is required for Kenyan businesses.")
            elif len(kra_pin.strip()) < 11:
                self.add_error('kra_pin', "KRA PIN must be at least 11 characters long.")
            if not cleaned_data.get('business_registration_doc'):
                self.add_error('business_registration_doc', "Upload your Business Registration Certificate.")
        elif business_type == 'international':
            if not cleaned_data.get('international_business_doc'):
                self.add_error('international_business_doc', "Upload your Trade License or Registration Document.")

        return cleaned_data


# --------------------------------------------
# ✅ Booth Form
# --------------------------------------------
class BoothForm(forms.ModelForm):
    class Meta:
        model = Booth
        fields = ["section", "booth_number", "booth_type", "size", "price", "is_booked"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if isinstance(field.widget, (forms.TextInput, forms.NumberInput, forms.Select)):
                field.widget.attrs.update({'class': 'form-control'})


# --------------------------------------------
# ✅ Exhibition Section Form
# --------------------------------------------
class ExhibitionSectionForm(forms.ModelForm):
    class Meta:
        model = ExhibitionSection
        fields = ["name", "description"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.TextInput):
                field.widget.attrs.update({'class': 'form-control'})
            elif isinstance(field.widget, forms.Textarea):
                field.widget.attrs.update({'class': 'form-control', 'rows': 3})
