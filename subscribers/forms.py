from django import forms
from django.contrib.auth.forms import UserCreationForm
from users.models import User
from .models import Subscriber

class SubscriberForm(forms.ModelForm):
    """Form for creating and editing subscribers"""
    
    class Meta:
        model = Subscriber
        fields = [
            'full_name', 'email', 'phone_number', 'business_name', 
            'residence_country', 'address', 'city', 'postal_code',
            'subscription_type', 'is_active', 'notes'
        ]
        widgets = {
            'full_name': forms.TextInput(attrs={
                'class': 'form-input w-full',
                'placeholder': 'Enter full name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-input w-full',
                'placeholder': 'Enter email address'
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-input w-full',
                'placeholder': 'Enter phone number'
            }),
            'business_name': forms.TextInput(attrs={
                'class': 'form-input w-full',
                'placeholder': 'Enter business name (optional)'
            }),
            'residence_country': forms.TextInput(attrs={
                'class': 'form-input w-full',
                'placeholder': 'Enter country'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-textarea w-full',
                'rows': 3,
                'placeholder': 'Enter address (optional)'
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-input w-full',
                'placeholder': 'Enter city (optional)'
            }),
            'postal_code': forms.TextInput(attrs={
                'class': 'form-input w-full',
                'placeholder': 'Enter postal code (optional)'
            }),
            'subscription_type': forms.Select(attrs={
                'class': 'form-select w-full'
            }, choices=[
                ('basic', 'Basic'),
                ('premium', 'Premium'),
                ('enterprise', 'Enterprise')
            ]),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-checkbox h-4 w-4 text-primary-600'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-textarea w-full',
                'rows': 4,
                'placeholder': 'Enter any additional notes (optional)'
            }),
        }
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and Subscriber.objects.filter(email=email).exists():
            if self.instance and self.instance.pk:
                # This is an update, so it's okay if the email belongs to this instance
                pass
            else:
                raise forms.ValidationError('A subscriber with this email already exists.')
        return email

class UserForm(forms.ModelForm):
    """Form for creating and editing users"""
    
    class Meta:
        model = User
        fields = [
            'full_name', 'email', 'phone_number', 'company_name', 
            'country', 'is_active'
        ]
        widgets = {
            'full_name': forms.TextInput(attrs={
                'class': 'form-input w-full',
                'placeholder': 'Enter full name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-input w-full',
                'placeholder': 'Enter email address'
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-input w-full',
                'placeholder': 'Enter phone number'
            }),
            'company_name': forms.TextInput(attrs={
                'class': 'form-input w-full',
                'placeholder': 'Enter company name (optional)'
            }),
            'country': forms.TextInput(attrs={
                'class': 'form-input w-full',
                'placeholder': 'Enter country (optional)'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-checkbox h-4 w-4 text-primary-600'
            }),
        }
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email=email).exists():
            if self.instance and self.instance.pk:
                # This is an update, so it's okay if the email belongs to this instance
                pass
            else:
                raise forms.ValidationError('A user with this email already exists.')
        return email

class UserSearchForm(forms.Form):
    """Form for searching and filtering users"""
    
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-input w-full',
            'placeholder': 'Search by name, email, phone, or company...'
        })
    )
    
    status = forms.ChoiceField(
        required=False,
        choices=[
            ('', 'All Statuses'),
            ('active', 'Active'),
            ('inactive', 'Inactive')
        ],
        widget=forms.Select(attrs={'class': 'form-select w-full'})
    )
    
    country = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-input w-full',
            'placeholder': 'Filter by country'
        })
    )
    
    sort_by = forms.ChoiceField(
        required=False,
        choices=[
            ('-date_joined', 'Newest First'),
            ('date_joined', 'Oldest First'),
            ('full_name', 'Name A-Z'),
            ('email', 'Email A-Z')
        ],
        widget=forms.Select(attrs={'class': 'form-select w-full'})
    ) 