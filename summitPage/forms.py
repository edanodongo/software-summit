from django import forms
from .models import Registrant
from .models import Registration


class QuickRegistrationForm(forms.ModelForm):
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
