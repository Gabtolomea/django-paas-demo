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
def years(id):
    years = []
    alltrans = Transactions.objects.filter(acctID=id, transType='Billing') | Transactions.objects.filter(acctID=id, transType='Reset Meter')
    for i in alltrans:
        if i.date.year not in years:
            years.append(i.date.year)
    if datetime.today().year not in years:
        years.append(datetime.today().year)
    return years
def last_reading(id, year, mo):
    allyears = years(id)
    allyears.sort(reverse=True)
    fyears = [item for item in allyears if item <= year]
    for i in fyears:
        for j in reversed(range(1,mo)):
            try:
                lasttran = Transactions.objects.get(acctID=id, transType='Billing', year=i, month=j)
                lastreading = lasttran.meterReading
                return lastreading
            except ObjectDoesNotExist:
                pass
        mo = 13
    return 0

def create_brec(address_id, year):
    con_b_rec = BarangayRecord()  
    con_b_rec.barangayrec_id = f"{address_id}-{year}"
    con_b_rec.barangaycode = Barangays.objects.get(id=address_id)
    con_b_rec.year = year
    con_b_rec.total_due_jan = 0
    con_b_rec.total_due_feb = 0
    con_b_rec.total_due_mar = 0
    con_b_rec.total_due_apr = 0
    con_b_rec.total_due_may = 0
    con_b_rec.total_due_jun = 0
    con_b_rec.total_due_jul = 0
    con_b_rec.total_due_aug = 0
    con_b_rec.total_due_sept = 0
    con_b_rec.total_due_oct = 0
    con_b_rec.total_due_nov = 0
    con_b_rec.total_due_dec = 0
    con_b_rec.total_paid_jan = 0
    con_b_rec.total_paid_feb = 0
    con_b_rec.total_paid_mar = 0
    con_b_rec.total_paid_apr = 0
    con_b_rec.total_paid_may = 0
    con_b_rec.total_paid_jun = 0
    con_b_rec.total_paid_jul = 0
    con_b_rec.total_paid_aug = 0
    con_b_rec.total_paid_sept = 0
    con_b_rec.total_paid_oct = 0
    con_b_rec.total_paid_nov = 0
    con_b_rec.total_paid_dec = 0
    con_b_rec.total_usage_jan = 0
    con_b_rec.total_usage_feb = 0
    con_b_rec.total_usage_mar = 0
    con_b_rec.total_usage_apr = 0
    con_b_rec.total_usage_may = 0
    con_b_rec.total_usage_jun = 0
    con_b_rec.total_usage_jul = 0
    con_b_rec.total_usage_aug = 0
    con_b_rec.total_usage_sept = 0
    con_b_rec.total_usage_oct = 0
    con_b_rec.total_usage_nov = 0
    con_b_rec.total_usage_dec = 0
    return con_b_rec
def get_balance(id):
    user = ConsumerInfo.objects.get(consumer_id = id)
    trans = Transactions.objects.filter(acctID = id)
    asc_trans = trans.order_by('year', 'month','transactionid')
    bal = 0
    for i in range(len(asc_trans)):
        if asc_trans[i].transType == 'Billing':
            bal+=asc_trans[i].bill
        elif asc_trans[i].transType == 'Payment':
            bal-=asc_trans[i].payment
        elif asc_trans[i].transType == 'Penalty':
            bal+=asc_trans[i].bill
        elif asc_trans[i].transType == 'Discount':
            bal-=asc_trans[i].payment
    user.current_reading = trans.filter(transType='Billing').order_by('-year', '-month')[0].meterReading
    user.current_bal = math.ceil(bal*100)/100
    if user.current_bal < 0:
        user.excess += (user.current_bal*-1)
        user.current_bal = 0
    if user.excess < 0:
        user.excess = 0
        user.current_bal += (user.excess*-1)
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
