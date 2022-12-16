from base64 import urlsafe_b64decode

from django.forms import ValidationError
from .models import *
from django.core.exceptions import ObjectDoesNotExist
import math
import random
import string
from datetime import datetime
def n_int(var):
    if var is None:
        return 0
    else:
        return var

def n_str(var):
    if var is None:
        return ''
    else:
        return var

def str_int(var):
    if var == '':
        return 0
    else:
        return int(var)
def camelize():
    cons = ConsumerInfo.objects.all()
    for c in cons:
        c.firstname = c.firstname.title()
        c.lastname = c.lastname.title()
        c.middlename = c.middlename.title()
        c.save()
def enye(cons):
    cons = ConsumerInfo.objects.all()
    for c in cons:
        chars = ["ã‘","ã±"]
        for char in chars:
            if char in c.firstname:
                c.firstname = c.firstname.replace(char, "ñ")
            if char in c.lastname:
                c.lastname = c.lastname.replace(char, "ñ")
            if char in c.middlename:
                c.middlename = c.middlename.replace(char, "ñ")
            c.save()
def capitalize():
    cons = ConsumerInfo.objects.all()
    for c in cons:
        c.firstname = c.firstname.upper()
        c.lastname = c.lastname.upper()
        c.middlename = c.middlename.upper()
        c.save()
def last_reading(id, year, month):
    cont = month-1
    while year:
        while cont>0:
            try:
                Transactions.objects.get(acctID_id=id, transType = 'Billing',year=year,month=cont)
            except ObjectDoesNotExist:
                cont-=1
            else:
                return Transactions.objects.get(acctID_id=id, transType = 'Billing',year=year,month=cont).meterReading
        year-=1
        cont=12

def get_balance(id):
    user = ConsumerInfo.objects.get(consumer_id = id)
    trans = Transactions.objects.filter(acctID = id)
    asc_trans = trans.order_by('year', 'month','transactionid')
    bal = 0
    for i in range(len(asc_trans)):
        if asc_trans[i].transType == 'Billing':
            bal+=asc_trans[i].bill
        elif asc_trans[i].transType == 'Payment':
            bal=bal-asc_trans[i].payment
    user.current_bal = math.ceil(bal*100)/100
    user.save()


def gen_token():
    nums = [str(x) for x in range(10)]
    alphabet = list(string.ascii_lowercase)
    choices = nums + alphabet
    token = ""
    d = datetime.now().timestamp()
    random.seed(d)
    for i in range(10):
        char = random.choice(choices)
        token+=(char)
    return token