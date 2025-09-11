# registrations/forms.py
from django import forms
from .models import Registrant

class QuickRegistrationForm(forms.ModelForm):
    interests = forms.MultipleChoiceField(
        choices=Registrant.INTEREST_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )
    updates_opt_in = forms.BooleanField(required=False)

    # Extra fields for user input
    other_category = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control mt-2', 'placeholder': 'Please specify...'})
    )
    other_interest = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control mt-2', 'placeholder': 'Please specify...'})
    )

    class Meta:
        model = Registrant
        fields = [
            'full_name', 'email', 'phone',
            'organization', 'job_title',
            'category', 'other_category',
            'interests', 'other_interest',
            'accessibility_needs', 'updates_opt_in'
        ]
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email Address'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'}),
            'organization': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Organization'}),
            'job_title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Job Title / Role'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'accessibility_needs': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Accessibility/Dietary Needs (optional)'}),
        }



# registrations/forms.py
from django import forms
from .models import Registrant

class BulkEmailForm(forms.Form):
    CATEGORY_CHOICES = [
        ('all', 'All'),
        ('updates', 'Future Updates Mailing List'),
    ] + Registrant.CATEGORY_CHOICES

    subject = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Email Subject"
        })
    )
    message = forms.CharField(
        widget=forms.Textarea(attrs={
            "class": "form-control",
            "rows": 6,
            "placeholder": "Write your message here..."
        })
    )
    category = forms.ChoiceField(
        choices=CATEGORY_CHOICES,
        widget=forms.Select(attrs={"class": "form-select"})
    )
