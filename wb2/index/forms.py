
from dataclasses import fields
import email
from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from django import forms

from .models import *


class SystemUserForm(UserCreationForm):
    CHOICES =(
        ("0", "Approver for Inbound Application"),
        ("1", "Non Approver"),
        ("2", "Supervisor"),
        ("3", "Engineer's Office"),
        ("4", "Mayor's Office"),
    )
    password1 = forms.Field(widget = forms.PasswordInput(attrs={'class': 'form-control'}))
    password2 = forms.Field(widget = forms.PasswordInput(attrs={'class': 'form-control'}))
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    firstname = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    midname = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    lastname = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    mobilenum = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    profilepic = forms.ImageField(widget=forms.FileInput(attrs={'class': 'form-control'}), required=False)
    authorizedapprover = forms.ChoiceField(widget=forms.Select(attrs={'class': 'form-select'}), choices=CHOICES)
    class Meta:
        model = SystemUsers
        fields = (
            'password1',
            'password2',
            'username',
            'email',
            'firstname',
            'lastname',
            'is_admin',
            'is_teller',
            'is_supervisor',
            'is_manager',
            'is_reader',
            'midname',
            'mobilenum',
            'profilepic',
            'authorizedapprover',
        )

class ConsumerCreationForm(ModelForm):
    firstname = forms.CharField(widget=forms.TextInput)
    lastname = forms





# class RatesForm(ModelForm):
#     class Meta:
#         model = Rates
#         fields = (
#             'minReading',
#             'minReadingCharge',
#             'rateAfterMin',
#             'ratePenalty',
#             'ratePenaltyFreq'
#         )

# class BarangayRecordForm(ModelForm):
#     model = BarangayRecord
#     field = (
#         'B_RecordID',
#         'barangaycode',
#         'year',
#     )