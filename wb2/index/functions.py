from .models import *
from django.core.exceptions import ObjectDoesNotExist

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