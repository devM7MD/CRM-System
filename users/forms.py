from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm as BaseUserCreationForm, PasswordChangeForm as DjangoPasswordChangeForm
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

User = get_user_model()

class LoginForm(forms.Form):
    """Form for user login."""
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-t-md focus:outline-none focus:ring-yellow-500 focus:border-yellow-500 focus:z-10 sm:text-sm', 'placeholder': 'Email address'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-b-md focus:outline-none focus:ring-yellow-500 focus:border-yellow-500 focus:z-10 sm:text-sm', 'placeholder': 'Password'})
    )
    
    # Remove phone related code
    # def clean_phone_number(self):
    #     """Format phone number with country code if provided."""
    #     phone = self.cleaned_data.get('phone_number')
    #     country_code = self.cleaned_data.get('phone_country_code')
    #     
    #     if phone and country_code and not phone.startswith('+'):
    #         # Add + to country code if not present
    #         if not country_code.startswith('+'):
    #             country_code = f"+{country_code}"
    #             
    #         # If phone already has the country code, return as is
    #         if not phone.startswith(country_code):
    #             # Remove any leading zeros from the phone number
    #             phone = phone.lstrip('0')
    #             phone = f"{country_code}{phone}"
    #     
    #     return phone

class RegisterForm(forms.ModelForm):
    """Form for new user registration."""
    password1 = forms.CharField(
        label=_("Password"),
        widget=forms.PasswordInput(attrs={'class': 'appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-yellow-500 focus:border-yellow-500 sm:text-sm'})
    )
    password2 = forms.CharField(
        label=_("Confirm Password"),
        widget=forms.PasswordInput(attrs={'class': 'appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-yellow-500 focus:border-yellow-500 sm:text-sm'})
    )
    phone_country_code = forms.CharField(
        required=False,
        widget=forms.HiddenInput()
    )
    
    class Meta:
        model = User
        fields = ['full_name', 'email', 'phone_number', 'password1', 'password2', 'company_name', 'country', 'expected_daily_orders', 'profile_image']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make sure role field is not required
        if 'role' in self.fields:
            self.fields['role'].required = False
    
    def clean_password2(self):
        """Check that the two password entries match."""
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError(_("Passwords don't match"))
        return password2
    
    def clean_phone_number(self):
        """Format phone number with country code if provided."""
        phone = self.cleaned_data.get('phone_number')
        country_code = self.cleaned_data.get('phone_country_code')
        
        if phone and country_code and not phone.startswith('+'):
            # Add + to country code if not present
            if not country_code.startswith('+'):
                country_code = f"+{country_code}"
                
            # If phone already has the country code, return as is
            if not phone.startswith(country_code):
                # Remove any leading zeros from the phone number
                phone = phone.lstrip('0')
                phone = f"{country_code}{phone}"
        
        return phone
    
    def save(self, commit=True):
        """Save the new user."""
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user

class UserCreationForm(BaseUserCreationForm):
    """Form for admin to create a new user."""
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={'class': 'appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-yellow-500 focus:border-yellow-500 sm:text-sm'})
    )
    password2 = forms.CharField(
        label="Password confirmation",
        widget=forms.PasswordInput(attrs={'class': 'appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-yellow-500 focus:border-yellow-500 sm:text-sm'})
    )
    
    class Meta:
        model = User
        fields = ('email', 'full_name', 'phone_number', 'role', 'is_active', 'profile_image')
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-yellow-500 focus:border-yellow-500 sm:text-sm'}),
            'full_name': forms.TextInput(attrs={'class': 'appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-yellow-500 focus:border-yellow-500 sm:text-sm'}),
            'phone_number': forms.TextInput(attrs={'class': 'appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-yellow-500 focus:border-yellow-500 sm:text-sm'}),
            'role': forms.Select(attrs={'class': 'appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-yellow-500 focus:border-yellow-500 sm:text-sm'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'focus:ring-yellow-500 h-4 w-4 text-yellow-600 border-gray-300 rounded'}),
            'profile_image': forms.FileInput(attrs={'class': 'appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-yellow-500 focus:border-yellow-500 sm:text-sm'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make sure role field is not required
        if 'role' in self.fields:
            self.fields['role'].required = False
    
    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user

class UserChangeForm(forms.ModelForm):
    """Form for user updates."""
    class Meta:
        model = User
        fields = ('email', 'full_name', 'phone_number', 'role', 'is_active', 'profile_image')
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-yellow-500 focus:border-yellow-500 sm:text-sm'}),
            'full_name': forms.TextInput(attrs={'class': 'appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-yellow-500 focus:border-yellow-500 sm:text-sm'}),
            'phone_number': forms.TextInput(attrs={'class': 'appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-yellow-500 focus:border-yellow-500 sm:text-sm'}),
            'role': forms.Select(attrs={'class': 'appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-yellow-500 focus:border-yellow-500 sm:text-sm'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'focus:ring-yellow-500 h-4 w-4 text-yellow-600 border-gray-300 rounded'}),
            'profile_image': forms.FileInput(attrs={'class': 'appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-yellow-500 focus:border-yellow-500 sm:text-sm'}),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make sure role field is not required
        if 'role' in self.fields:
            self.fields['role'].required = False

class PasswordChangeForm(DjangoPasswordChangeForm):
    """Form for changing user password."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['old_password'].widget.attrs.update({
            'class': 'appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-yellow-500 focus:border-yellow-500 sm:text-sm'
        })
        self.fields['new_password1'].widget.attrs.update({
            'class': 'appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-yellow-500 focus:border-yellow-500 sm:text-sm'
        })
        self.fields['new_password2'].widget.attrs.update({
            'class': 'appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-yellow-500 focus:border-yellow-500 sm:text-sm'
        }) 