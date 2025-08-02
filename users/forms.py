from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm as BaseUserCreationForm, PasswordChangeForm as DjangoPasswordChangeForm
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

User = get_user_model()

class LoginForm(forms.Form):
    """Form for user login."""
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-t-md focus:outline-none focus:ring-yellow-500 focus:border-yellow-500 focus:z-10 sm:text-sm', 'placeholder': 'Email address'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-b-md focus:outline-none focus:ring-yellow-500 focus:border-yellow-500 focus:z-10 sm:text-sm', 'placeholder': 'Password'})
    )

class RegisterForm(forms.ModelForm):
    """Form for user registration."""
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={'class': 'appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-yellow-500 focus:border-yellow-500 sm:text-sm'})
    )
    password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={'class': 'appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-yellow-500 focus:border-yellow-500 sm:text-sm'})
    )
    
    class Meta:
        model = User
        fields = ['email', 'full_name', 'phone_number', 'company_name', 'country', 'expected_daily_orders', 'profile_image']
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-yellow-500 focus:border-yellow-500 sm:text-sm'}),
            'full_name': forms.TextInput(attrs={'class': 'appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-yellow-500 focus:border-yellow-500 sm:text-sm'}),
            'phone_number': forms.TextInput(attrs={'class': 'appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-yellow-500 focus:border-yellow-500 sm:text-sm'}),
            'company_name': forms.TextInput(attrs={'class': 'appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-yellow-500 focus:border-yellow-500 sm:text-sm'}),
            'country': forms.TextInput(attrs={'class': 'appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-yellow-500 focus:border-yellow-500 sm:text-sm'}),
            'expected_daily_orders': forms.NumberInput(attrs={'class': 'appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-yellow-500 focus:border-yellow-500 sm:text-sm'}),
            'profile_image': forms.FileInput(attrs={'class': 'appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-yellow-500 focus:border-yellow-500 sm:text-sm'}),
        }
    
    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords don't match")
        return password2
    
    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user

class UserCreationForm(BaseUserCreationForm):
    """Form for admin to create a new user."""
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-input w-full',
            'placeholder': 'Enter first name'
        })
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-input w-full',
            'placeholder': 'Enter last name'
        })
    )
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={
            'class': 'form-input w-full pr-10',
            'placeholder': 'Enter password'
        })
    )
    password2 = forms.CharField(
        label="Password confirmation",
        widget=forms.PasswordInput(attrs={
            'class': 'form-input w-full pr-10',
            'placeholder': 'Confirm password'
        })
    )
    primary_role = forms.ModelChoiceField(
        queryset=None,
        required=False,
        empty_label="Select a role",
        widget=forms.Select(attrs={
            'class': 'form-select w-full'
        })
    )
    
    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'phone_number', 'is_active', 'profile_image')
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'form-input w-full',
                'placeholder': 'user@atlasfulfillment.ae'
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-input w-full',
                'placeholder': '+971501234567'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-checkbox h-5 w-5 text-yellow-600 border-gray-300 rounded focus:ring-yellow-500'
            }),
            'profile_image': forms.FileInput(attrs={
                'class': 'form-input w-full',
                'accept': 'image/*'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        try:
            from roles.models import Role
            self.fields['primary_role'].queryset = Role.objects.filter(is_active=True).order_by('name')
        except ImportError:
            # If roles app is not available, hide the field
            del self.fields['primary_role']
    
    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2
    
    def save(self, commit=True):
        user = super().save(commit=False)
        
        # Combine first_name and last_name into full_name
        first_name = self.cleaned_data.get('first_name', '')
        last_name = self.cleaned_data.get('last_name', '')
        user.full_name = f"{first_name} {last_name}".strip()
        
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
            
            # Handle role assignment
            if 'primary_role' in self.cleaned_data and self.cleaned_data['primary_role']:
                try:
                    from roles.models import UserRole
                    new_role = self.cleaned_data['primary_role']
                    
                    # Create user role
                    UserRole.objects.create(
                        user=user,
                        role=new_role,
                        is_primary=True,
                        is_active=True
                    )
                except ImportError:
                    pass
        
        return user

class UserChangeForm(forms.ModelForm):
    """Form for user updates."""
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-input w-full',
            'placeholder': 'Enter first name'
        })
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-input w-full',
            'placeholder': 'Enter last name'
        })
    )
    primary_role = forms.ModelChoiceField(
        queryset=None,
        required=False,
        empty_label="Select a role",
        widget=forms.Select(attrs={
            'class': 'form-select w-full'
        })
    )
    
    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'phone_number', 'is_active', 'profile_image')
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'form-input w-full',
                'placeholder': 'user@atlasfulfillment.ae'
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-input w-full',
                'placeholder': '+971501234567'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-checkbox h-5 w-5 text-yellow-600 border-gray-300 rounded focus:ring-yellow-500'
            }),
            'profile_image': forms.FileInput(attrs={
                'class': 'form-input w-full',
                'accept': 'image/*'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Set initial values for first_name and last_name from full_name
        if self.instance.pk and self.instance.full_name:
            name_parts = self.instance.full_name.split(' ', 1)
            if len(name_parts) > 1:
                self.fields['first_name'].initial = name_parts[0]
                self.fields['last_name'].initial = name_parts[1]
                print(f"Setting first_name: {name_parts[0]}, last_name: {name_parts[1]}")  # Debug
            else:
                self.fields['first_name'].initial = name_parts[0]
                print(f"Setting first_name only: {name_parts[0]}")  # Debug
        else:
            print(f"No instance or full_name. Instance: {self.instance}, full_name: {getattr(self.instance, 'full_name', 'N/A')}")  # Debug
        
        try:
            from roles.models import Role
            self.fields['primary_role'].queryset = Role.objects.filter(is_active=True).order_by('name')
            
            # Set initial value for primary_role
            if self.instance.pk:
                primary_role = self.instance.primary_role
                if primary_role:
                    self.fields['primary_role'].initial = primary_role
        except ImportError:
            # If roles app is not available, hide the field
            del self.fields['primary_role']
    
    def save(self, commit=True):
        user = super().save(commit=False)
        
        # Combine first_name and last_name into full_name
        first_name = self.cleaned_data.get('first_name', '')
        last_name = self.cleaned_data.get('last_name', '')
        user.full_name = f"{first_name} {last_name}".strip()
        
        if commit:
            user.save()
            
            # Handle role assignment
            if 'primary_role' in self.cleaned_data and self.cleaned_data['primary_role']:
                try:
                    from roles.models import UserRole
                    new_role = self.cleaned_data['primary_role']
                    
                    # Remove existing primary role
                    UserRole.objects.filter(user=user, is_primary=True).update(is_primary=False)
                    
                    # Create or update user role
                    user_role, created = UserRole.objects.get_or_create(
                        user=user,
                        role=new_role,
                        defaults={'is_primary': True, 'is_active': True}
                    )
                    if not created:
                        user_role.is_primary = True
                        user_role.is_active = True
                        user_role.save()
                except ImportError:
                    pass
        
        return user

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