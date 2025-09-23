# forms.py
from django import forms
from .models import Registrant

class QuickRegistrationForm(forms.ModelForm):
    interests = forms.MultipleChoiceField(
        choices=Registrant.INTEREST_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )
    updates_opt_in = forms.BooleanField(required=False)

    other_organization_type = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control mt-2',
            'placeholder': 'Please specify...',
            'rows': 3  # optional: controls height
        })
    )
    other_interest = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control mt-2',
            'placeholder': 'Please specify...',
            'rows': 3  # optional: controls height
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
            'second_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Second Name'}),
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

        # If any organization_type is chosen, require textbox
        if organization_type and not other_organization_type:
            self.add_error(
                "other_organization_type",
                "Please specify your organization type."
            )

        # If "Others" is in interests, require textbox
        if "Others" in interests and not other_interest:
            self.add_error(
                "other_interest",
                "Please specify your interest."
            )

        return cleaned_data
