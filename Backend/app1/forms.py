from django import forms

class LoginForm(forms.Form):
    username = forms.CharField(max_length=150, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Username'
    }))
    
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Password'
    }))



class RegistrationForm(forms.Form):
    username = forms.CharField(max_length=150, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Username'
    }))
    
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'Email'
    }))
    
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Password'
    }))
    
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Confirm Password'
    }))

    phone = forms.CharField(max_length=15, required=False, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Phone'
    }))

    address = forms.CharField(max_length=255, required=False, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Address'
    }))

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise forms.ValidationError(
                "Password and Confirm Password do not match"
            )


from django.utils import timezone
from .models import ShortURL


class ShortURLForm(forms.Form):
    def __init__(self, *args, **kwargs):
        # optional exclude_pk to allow editing without hitting uniqueness against self
        self.exclude_pk = kwargs.pop('exclude_pk', None)
        super().__init__(*args, **kwargs)

    original_url = forms.URLField(widget=forms.URLInput(attrs={
        'class': 'form-control',
        'placeholder': 'https://example.com/very/long/url'
    }))
    custom_key = forms.CharField(required=False, max_length=32, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Optional custom alias (alphanumeric)'
    }))
    expires_at = forms.DateTimeField(required=False, widget=forms.DateTimeInput(attrs={
        'class': 'form-control',
        'placeholder': 'YYYY-MM-DD HH:MM'
    }))

    def clean_custom_key(self):
        key = self.cleaned_data.get('custom_key')
        if key:
            if not key.isalnum():
                raise forms.ValidationError('Custom alias must be alphanumeric')
            qs = ShortURL.objects.filter(key=key)
            if self.exclude_pk:
                qs = qs.exclude(pk=self.exclude_pk)
            if qs.exists():
                raise forms.ValidationError('This alias is already taken. Please choose another.')
        return key

    def clean_expires_at(self):
        expires = self.cleaned_data.get('expires_at')
        if expires:
            now = timezone.now()
            if expires <= now:
                raise forms.ValidationError('Expiration time must be in the future.')
        return expires

