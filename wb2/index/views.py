from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.shortcuts import redirect
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import EmailMessage
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string

import mysql.connector

from wb2 import settings
from .forms import *
from .decorators import *
from .models import *

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="yjh434ctuG@-@",
    database="lgu_ginatilan_db"
)
def landingpage(request):
    tablenames = [
        'accountinfo',
        'accountrecord',
        'barangay_record',
        'consumerinfo',
        'gettotalbill',
        'meterreadingmodification_table',
        'oldconsumerinfo',
        'payment_history',
        'ratestable',
        'revenuecode',
        'systemuser',
        'yearly_records'
    ]

    mycursor = mydb.cursor()

    for t in tablenames:
        tablename = t
        mycursor.execute("SELECT "+ columnname +" FROM "+tablename)
        myresult = mycursor.fetchall()
        accountinfoid = []
        for x in myresult:
            accountinfoid.append(x[0])


    accountinfo = [accountinfoid]
    """
    accountrecord
    barangay_record
    consumerinfo
    gettotalbill
    meterreadingmodification_table
    oldconsumerinfo
    payment_history
    ratestable
    revenuecode
    systemuser
    yearly_records"""

    context = {    
        'accountinfo':accountinfo,
        
        #'accountrecord':accountrecord,
        #'barangay_record':barangay_record,
        #'consumerinfo':consumerinfo,
        #'gettotalbill':gettotalbill,
        #'meterreadingmodification_table':meterreadingmodification_table,
        #'oldconsumerinfo':oldconsumerinfo,
        #'payment_history':payment_history,
        #'ratestable':ratestable,
        #'revenuecode':revenuecode,
        #'systemuser':systemuser,
        #'yearly_records':yearly_records,
    }

    return render(request, 'home.html', context)


def login(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, 'Logged in')
            return redirect('home')
        else:
            messages.error(request, "Invalid Username or Password")

    return render(request, 'login2.0.html')

def home(request):
    return render(request, 'home.html')