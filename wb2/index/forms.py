
from dataclasses import fields
import email
from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from django import forms
from .models import *


class SystemUserForm(UserCreationForm):
    password1: forms.Field(label='Password')
    password2: forms.Field(label='Confirm Password')
    firstname = forms.CharField(widget=forms.TextInput
                                (attrs={'class': 'form-control'
                                        }))
    midname = forms.CharField(widget=forms.TextInput
                              (attrs={'class': 'form-control'
                                      }))

    lastname = forms.CharField(widget=forms.TextInput
                               (attrs={'class': 'form-control'
                                       }))

    mobilenum = forms.IntegerField(widget=forms.TextInput
                                   (attrs={'class': 'form-control'
                                           }))

    email = forms.CharField(widget=forms.TextInput
                            (attrs={'class': 'form-control'
                                    }))

    password1 = forms.CharField(widget=forms.PasswordInput
                                (attrs={'class': 'form-control'
                                        }))

    password2 = forms.CharField(widget=forms.PasswordInput
                                (attrs={'class': 'form-control'
                                        }))
    authorizedapprover = forms.CharField(widget=forms.TextInput
                                         (attrs={'class': 'form-control'
                                                 }))

    profilepic = forms.ImageField(widget=forms.FileInput
                                  (attrs={'class': 'form-control'
                                          }))

    
    class Meta:
        model = SystemUsers
        fields = (
            'username',
            'email',
            'is_staff',
            'password1',
            'password2',
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
