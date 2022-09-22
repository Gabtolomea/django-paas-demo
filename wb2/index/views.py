from email import errors
from os import system
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
import base64
from wb2.wb2 import settings
from .forms import *
from .decorators import *
from .models import *
from .dataporter import *
from .ledger import *
import math
from .tokens import generate_token

def lp(request):
    porter()
    return render(request, "home.html")
@unauthenticated_user
def signin(request):
    if request.method == "POST":
        u = request.POST['username']
        password = request.POST['password']
        pkval = SystemUsers.objects.filter(username = u)
        passAscii = password.encode("ascii")
        p = base64.b64encode(passAscii)
        if pkval.exists():
            user = SystemUsers.objects.get(username = u)
            if user.password == p:
                login(request,user)
                messages.success(request, 'Logged in')
                return redirect('dashboard')
            else:
                messages.error(request, "Invalid Password")
        else:
            messages.error(request, "Invalid Username")
    return render(request, 'login.html')
@login_required(login_url='login')
def signout(request):
    logout(request)
    messages.success(request, 'Logout successful')
    return redirect('login')
def home(request):
    return render(request, 'home.html')
def user_creation(request):
    form = SystemUserForm()
    if request.method == "POST":
        form = SystemUserForm(request.POST)
        if request.method == 'POST':
            is_admin = request.POST['admin']
            is_teller = request.POST['teller']
            is_supervisor = request.POST['supervisor']
            is_manager = request.POST['manager']
            is_meter = request.POST['meter']
            if form.is_valid():
                form.save()
                user = SystemUsers.objects.get(username=form.cleaned_data.get('username'))
                user.is_admin = is_admin
                user.is_teller = is_teller
                user.is_supervisor = is_supervisor
                user.is_manager = is_manager
                user.is_meter = is_meter
                user.save()
                return redirect('login')
    context = {
        'form':form, 
        'errors':form.errors,
    }
    return render(request, 'registration.html', context)
def dashboard(request):
    return render(request, 'dashboard.html')
def ledger(request, id):
    dates = []
    prevs = []
    readings = []
    usages = []
    bills = []
    payments = []
    pbs = []
    ids = []
    bals = []
    table = []
    if ConsumerInfo.objects.filter(pk = id).exists():
        user = ConsumerInfo.objects.get(pk = id)
        trans = Transactions.objects.filter(acctID = user.consumer_id)
        asc_trans = trans.order_by('date')
        bal = 0
        for i in range(len(asc_trans)):
            dates.append(asc_trans[i].date)
            if i == 0:
                prev = 0
            else:
                if asc_trans[i-1].meterReading is None:
                    prev = ''
                else:
                    prev = asc_trans[i-1].meterReading
            prevs.append(prev)
            
            if asc_trans[i].meterReading is None:
                cur = ''
            else:
                cur = asc_trans[i].meterReading
            if asc_trans[i].usage is None:
                usage = ''
            else:
                usage = asc_trans[i].usage
            if asc_trans[i].bill is None:
                bill = ''
            else:
                bill = asc_trans[i].bill
            if asc_trans[i].processedBy is None:
                pb = ''
            else:
                pb = asc_trans[i].processedBy
            readings.append(cur)
            usages.append(usage)
            bills.append(bill)
            payments.append(asc_trans[i].payment)
            pbs.append(pb)
            ids.append(asc_trans[i].transactionid)
            
            if asc_trans[i].transType == 'Billing':
                bal+=bill
            else:
                bal=bal-asc_trans[i].payment
            bals.append(math.ceil(bal*100)/100)
        
        
        for i in range(len(asc_trans)):
            arr = [
                dates[i],
                prevs[i],
                readings[i],
                usages[i],
                bills[i],
                payments[i],
                pbs[i],
                ids[i],
                bals[i],
            ]
            table.append(arr)

    context = {
        'user':user,
        'table':table,
        'bal':math.ceil(bal*100)/100
    }
    return render(request, 'ledger.html', context)



def forgetpassword (request):
    if request.method == "POST":
        u_email = request.POST['email']
    if  SystemUsers.objects.filter(email = email).excesit():
        user = SystemUsers.objects.get(email = email)
        user.is_active = False
        user.save()

        current_site = get_current_site(request)
        email_subject = "Confirm your Email"
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = generate_token.make_token(user)
        message = render_to_string('email_verif.html',{
                'name': user.first_name,
                'domain': current_site.domain,
                'uid': uid,
                'token': token
            })
        print(f"http://{current_site.domain}/activate/{uid}/{token}")
        email = EmailMessage(
                email_subject,
                message,
                settings.EMAIL_HOST_USER,
                [user.email],
            )
        email.fail_silently = True
        email.send()
        messages.success(request, 'Please verify your account by clicking the link in your email: '+u_email)
            
        return redirect('signin')
            
    context = {'email':email,'errors': errors}
    return render(request,'forgetpassword.html',context)
    




