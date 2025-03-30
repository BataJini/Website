from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.utils.translation import gettext_lazy as _
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': _('Enter your email address')
        })
    )
    
    full_name = forms.CharField(
        max_length=255,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('Enter your full name')
        })
    )
    
    user_type = forms.CharField(
        widget=forms.HiddenInput(),
        required=True
    )
    
    company_name = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('Enter your company name')
        })
    )
    
    phone_number = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('Enter your phone number'),
            'type': 'tel',
            'pattern': '[0-9]*',
            'title': _('Please enter digits only.')
        })
    )
    
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': _('Create a password')
        })
    )
    
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': _('Confirm your password')
        })
    )
    
    terms_accepted = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        error_messages={
            'required': _('You must accept the Terms and Conditions and Privacy Policy to continue.')
        }
    )

    class Meta:
        model = CustomUser
        fields = ('email', 'full_name', 'password1', 'password2', 'user_type', 'company_name', 'phone_number')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Hide password validation help text
        self.fields['password1'].help_text = None
        self.fields['password2'].help_text = None

        # Determine the user_type based on POST data first, then initial data
        user_type = None
        if self.data: # Check if form was submitted (POST)
            user_type = self.data.get('user_type')
        elif self.initial: # Check initial data (GET)
            user_type = self.initial.get('user_type')

        # Make company fields required only for recruiters.
        # Visibility will be controlled by the template.
        if user_type == 'recruiter':
            self.fields['company_name'].required = True
            self.fields['phone_number'].required = True
        else: # Candidate or unknown
            self.fields['company_name'].required = False
            self.fields['phone_number'].required = False
            # DO NOT hide the fields here; let the template handle it.

    def clean(self):
        cleaned_data = super().clean()
        user_type = cleaned_data.get('user_type')
        
        if user_type == 'recruiter':
            company_name = cleaned_data.get('company_name')
            phone_number = cleaned_data.get('phone_number')
            
            if not company_name:
                self.add_error('company_name', _('Company name is required for recruiters.'))
            # Phone number presence is checked by required=True in __init__, 
            # but we keep the validation message here for consistency if needed.
            # if not phone_number:
            #     self.add_error('phone_number', _('Phone number is required for recruiters.'))
        
        return cleaned_data

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if phone_number and not phone_number.isdigit():
            raise forms.ValidationError(_('Phone number must contain only digits.'))
        return phone_number

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['email']
        user.email = self.cleaned_data['email']
        user.full_name = self.cleaned_data['full_name']
        user.user_type = self.cleaned_data['user_type']
        
        if user.user_type == 'recruiter':
            user.company_name = self.cleaned_data['company_name']
            user.phone_number = self.cleaned_data['phone_number']
        
        if commit:
            user.save()
        return user

class CustomAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('Enter your email address'),
            'autofocus': True
        })
    ) 