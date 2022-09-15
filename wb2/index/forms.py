
from dataclasses import fields
from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from django import forms
from .models import *


class SystemUserForm(UserCreationForm):
    password1: forms.Field(label='Password')
    password2: forms.Field(label='Confirm Password')
    class Meta:
        model = SystemUsers
        fields = (
            'username',
            'email',
            'is_staff',
            'password1',
            'password2',
            "usertype",
            'firstname',
            'midname',
            'lastname',
            'profilepic',
            'mobilenum',
            'authorizedapprover'

        )

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

        


