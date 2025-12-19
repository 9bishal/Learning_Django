from django import forms
from .models import UserDetail

class UserDetailForm(forms.ModelForm):
    class Meta:
        model = UserDetail
        fields = ['name', 'email', 'age', 'message']
