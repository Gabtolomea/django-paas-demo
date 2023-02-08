
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
    password1 = forms.Field(widget = forms.PasswordInput(attrs={'class': 'form-control'}), required=True)
    password2 = forms.Field(widget = forms.PasswordInput(attrs={'class': 'form-control'}), required=True)
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=True)
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}), required=True)
    first_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=True)
    mid_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)
    last_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=True)
    mobilenum = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control','placeholder':'09XXXXXXXXX','onkeypress':'return onlyNumberKey(event)', 'maxlength':'11'}))
    authorizedapprover = forms.ChoiceField(widget=forms.Select(attrs={'class': 'form-select input-group m-0'}), choices=CHOICES)
    class Meta:
        model = SystemUsers
        fields = (
            'password1',
            'password2',
            'username',
            'email',
            'first_name',
            'last_name',
            'mid_name',
            'is_admin',
            'is_teller',
            'is_supervisor',
            'is_manager',
            'is_reader',
            'mid_name',
            'mobilenum',
            'authorizedapprover',
        )
class ProfileForm(forms.ModelForm):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    first_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    mid_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}),required=False)
    last_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    profilepic = forms.ImageField(widget=forms.FileInput(attrs={'class': 'form-control'}))
    class Meta:
        model = SystemUsers
        fields = ('first_name', 'mid_name',
                  'last_name', 'email', 'profilepic')

class sysup(ModelForm):
    CHOICES =(
        ("0", "Approver for Inbound Application"),
        ("1", "Non Approver"),
        ("2", "Supervisor"),
        ("3", "Engineer's Office"),
        ("4", "Mayor's Office"),
    )
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}),required=True)
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}),required=True)
    last_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}),required=True)
    first_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}),required=True)
    mid_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}),required=False)
    mobilenum = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)

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
        'profilepic',)


class ConsumerForm(ModelForm):
    CHOICES = (
        ("MALE", "MALE"),
        ("FEMALE", "FEMALE"),
    )

    firstname = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    middlename = forms.CharField(widget = forms.TextInput(attrs={'class': 'form-control'}),required=False)
    lastname = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    mobilenum = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control','placeholder':'09XXXXXXXXX','onkeypress':'return onlyNumberKey(event)', 'maxlength':'11'}),required=False)
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}),required=False)
    birthdate = forms.DateField(widget=forms.DateInput(attrs={'class': 'form-control', 'type':'date'}),required=False)
    sex = forms.ChoiceField(widget=forms.Select(attrs={'class': 'form-select input-group'}), choices=CHOICES)
    sitio = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}),required=False)
    homeaddress = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    meternumber = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    initialmeterreading = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'form-control','min': 0}))
    installation_address = forms.ModelChoiceField(widget=forms.Select(attrs={'class': 'form-select input-group'}),queryset=Barangays.objects.all())
    contypeid = forms.ModelChoiceField(widget=forms.Select(attrs={'class': 'form-select input-group'}),queryset=ConsumerType.objects.all())
    penaltycode = forms.ModelChoiceField(widget=forms.Select(attrs={'class': 'form-select input-group'}),queryset=Penalty.objects.all(),required=False)
    
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
            'deleteflag',
            'mobilenum',
            'email',
            'birthdate',
            'sex',
            'sitio',
            'penaltycode',
        )
class addPenalty(ModelForm):
    penalty_info = forms.CharField(widget=forms.Textarea(attrs={'class':'form-control'}))
    penalty_rate = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'form-control','min':0}))
    penalty_after = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'form-control','min':0}))
    daysappliedafter = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'form-control','min':0}))

    class Meta():
        model = Penalty
        fields = (
            'penalty_info',
            'penalty_rate',
            'penalty_after',
            'daysappliedafter'
         )



class addDiscount(ModelForm):
    discount_rate = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'form-control','min':0}))

    class Meta():
        model = Discount
        fields = (
             'discount_rate',
        )

class ConscumertypecreationForm (ModelForm):
    contype = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}))
    minReading = forms.IntegerField(widget=forms.NumberInput(attrs={'class':'form-control', 'min':0}))
    minReadingCharge = forms.IntegerField(widget=forms.NumberInput(attrs={'class':'form-control', 'min':0}))
    rateAfterMin = forms.IntegerField(widget=forms.NumberInput(attrs={'class':'form-control', 'min':0}))

    class Meta():
        model = ConsumerType
        fields = (
            'contype',
            'minReading',
            'minReadingCharge',
            'rateAfterMin'
        )
