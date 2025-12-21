"""
Forms for user registration, login, and profile management

Django Forms handle:
- Form validation
- CSRF protection
- HTML rendering
- Error messages
"""

from django import forms
from django.contrib.auth.models import User
from .models import UserProfile, Address


# ============================================
# LOGIN FORM
# ============================================
class UserLoginForm(forms.Form):
    """
    Form for user login
    """
    
    username = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Username',
            'autocomplete': 'username'
        }),
        label='Username'
    )
    
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password',
            'autocomplete': 'current-password'
        }),
        label='Password'
    )


# ============================================
# REGISTRATION FORM
# ============================================
class UserRegistrationForm(forms.ModelForm):
    """
    Form for user signup/registration
    """
    
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter password'
        }),
        label='Password'
    )
    
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm password'
        }),
        label='Confirm Password'
    )
    
    class Meta:
        model = User
        fields = ['username', 'email']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Choose a username'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your email'
            }),
        }
    
    def clean(self):
        """Validate that passwords match"""
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password2 = cleaned_data.get('password2')
        
        if password and password2:
            if password != password2:
                raise forms.ValidationError("Passwords do not match!")
        
        return cleaned_data
    
    def clean_username(self):
        """Check if username already exists"""
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Username already taken!")
        return username
    
    def clean_email(self):
        """Check if email already exists"""
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email already registered!")
        return email


# ============================================
# USER PROFILE FORM
# ============================================
class UserProfileForm(forms.ModelForm):
    """
    Form to edit user profile information
    """
    
    class Meta:
        model = UserProfile
        fields = ['phone', 'address', 'city', 'state', 'pincode', 'country']
        widgets = {
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Phone number'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Street address',
                'rows': 3
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'City'
            }),
            'state': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'State'
            }),
            'pincode': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Pincode'
            }),
            'country': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Country'
            }),
        }


# ============================================
# ADDRESS FORM
# ============================================
class AddressForm(forms.ModelForm):
    """
    Form to add/edit delivery addresses
    """
    
    class Meta:
        model = Address
        fields = ['address_type', 'street_address', 'city', 'state', 'pincode', 'country', 'phone']
        widgets = {
            'address_type': forms.Select(attrs={
                'class': 'form-control'
            }),
            'street_address': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Street address'
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'City'
            }),
            'state': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'State'
            }),
            'pincode': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Pincode'
            }),
            'country': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Country'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Phone number'
            }),
        }

