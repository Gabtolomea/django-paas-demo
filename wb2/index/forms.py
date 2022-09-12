
from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from django import forms
from .models import *

"""
class CustomUserForm(UserCreationForm):
    password1: forms.Field(label='Password')
    password2: forms.Field(label='Confirm Password')
    class Meta:
        model = SystemUsers
        fields = (
            'username',
            'email',
            "usertype",
            'is_staff',
            'password1',
            'password2'
        )
"""