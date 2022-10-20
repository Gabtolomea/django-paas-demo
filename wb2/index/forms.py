
from dataclasses import fields
import email
from fileinput import FileInput
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

class sysup(ModelForm):
    CHOICES =(
        ("0", "Approver for Inbound Application"),
        ("1", "Non Approver"),
        ("2", "Supervisor"),
        ("3", "Engineer's Office"),
        ("4", "Mayor's Office"),
    )
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    first_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    mid_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    mobilenum = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}),required=False)
    authorizedapprover = forms.ChoiceField(widget=forms.Select(attrs={'class': 'form-select'}), choices=CHOICES)

    # password = forms.Field(widget = forms.PasswordInput(attrs={'class': 'form-control'}))
    class Meta:
        model = SystemUsers
        fields =(
        'first_name',
        'last_name',
        'email',
        'username',
        'is_admin',
        'is_teller',
        'is_supervisor',
        'is_manager',
        'is_reader',
        'mid_name',
        'mobilenum',
        'profilepic',
        'authorizedapprover',)



class ConsumerCreationForm(ModelForm):
    CHOICES = (
        ("MALE", "MALE"),
        ("FEMALE", "FEMALE"),
    )

    firstname = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    middlename = forms.CharField(widget = forms.TextInput(attrs={'class': 'form-control'}))
    lastname = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    mobilenum = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    birthdate = forms.DateField(widget=forms.DateInput(attrs={'class': 'form-control', 'type':'date'}))
    sex = forms.ChoiceField(widget=forms.Select(attrs={'class': 'form-control'}), choices=CHOICES)
    sitio = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    homeaddress = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    picture = forms.ImageField(widget=forms.FileInput(attrs={'class': 'form-control'}),required=False)
    meternumber = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    initialmeterreading = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'form-control','min': 0}))
    installation_address = forms.ModelChoiceField(widget=forms.Select(attrs={'class': 'form-control'}),queryset=Barangays.objects.all())
    rateid = forms.ModelChoiceField(widget=forms.Select(attrs={'class': 'form-control'}),queryset=ConsumerType.objects.all())

    class Meta():
        model = ConsumerInfo
        fields = (
            'meternumber',
            'firstname',
            'lastname',
            'middlename',
            'homeaddress',
            'installation_address',
            'initialmeterreading',
            'rateid',
            'deleteflag',
            'mobilenum',
            'email',
            'birthdate',
            'sex',
            'sitio',
            'picture'
        )
class Userinfoupdate(ModelForm):
    
    class Meta():
        model = ConsumerInfo
        fields = (
            'meternumber',
            'firstname',
            'lastname',
            'middlename',
            'homeaddress',
            'installation_address',
            'initialmeterreading',
            'contypeid',
            'mobilenum',
            'email',
            'birthdate',
            'sex',
            'sitio',
            'picture'
        )
    
# class addPenalty(ModelForm):
#     penaltycode = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
#     penaltyrate = forms.NumberInput(widget=forms.NumberInput(attrs={'class': 'form-control'}))
#     addedby = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))

        # class Meta:
        #     models = 

class addDiscount(ModelForm):
    discountcode = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    discount_rate = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'form-control'}))
    added_by = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta():
        model = Discount
        fields = (
            'discountcode',
            'discount_rate',
            'added_by'
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