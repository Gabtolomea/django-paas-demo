import calendar
from dis import dis
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
from wb2 import settings
from .forms import *
from .decorators import *
from .models import *
from .dataporter import *
from .ledger import *
import math
from .tokens import generate_token

def porter(request):
    porter_in()
    porter_out(sorted_tables)
    billing_out()
    balance()
    return render(request, "landing.html")

@unauthenticated_user
def lp(request):
    return render(request, "landing.html")
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
                return redirect('bills_list')
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
        print(request.POST)
        form = SystemUserForm(request.POST)
        username = request.POST['username']
        firstname = request.POST['firstname']
        midname = request.POST['midname']
        lastname = request.POST['lastname']
        mobilenum = request.POST['mobilenum']
        email = request.POST['email']
        password2 = request.POST['password2']
        is_admin = request.POST['is_admin'] == 'on'
        is_teller = request.POST['is_teller'] == 'on'
        is_admin = request.POST['is_admin'] == 'on'
        is_supervisor = request.POST['is_supervisor'] == 'on'
        is_manager = request.POST['is_manager'] == 'on'
        is_reader = request.POST['is_reader'] == 'on'
        authorizedapprover = request.POST['authorizedapprover']
        profilepic = request.POST['profilepic']
        if form.is_valid():
            user = SystemUsers()
            passAscii = password2.encode("ascii")
            p = base64.b64encode(passAscii)
            user.password = p
            user.username = username
            user.first_name = firstname
            user.mid_name = midname
            user.last_name = lastname
            user.mobilenum = mobilenum
            user.email = email
            user.is_admin = is_admin
            user.is_teller = is_teller
            user.is_admin = is_admin
            user.is_supervisor = is_supervisor
            user.is_manager = is_manager
            user.is_reader = is_reader
            user.authorizedapprover = authorizedapprover
            user.profilepic = profilepic
            user.save()
            return redirect('dashboard')
    context = {
        'form':form,
        'errors':form.errors,
    }
    return render(request, 'registration.html', context)

@login_required(login_url='login')
def dashboard(request):
    user = request.user
    context = {
        'user':user
    }
    return render(request, 'dashboard.html',context)
def ledger(request, id):
    table = []
    class ledgerclass():
        def __init__(self, transid, date, prev, reading, usage, bill, payment, pb, ornum, bal, rateid, style):
            self.transid = transid
            self.date = date
            self.prev = prev
            self.reading = reading
            self.usage = usage
            self.bill = bill
            self.payment = payment
            self.pb = pb
            self.ornum = ornum
            self.bal = bal
            self.rateid = rateid
            self.style = style
        def id(self):
            return self.transid
    if ConsumerInfo.objects.filter(pk = id).exists():
        u = ConsumerInfo.objects.get(pk = id)
        trans = Transactions.objects.filter(acctID = u.consumer_id)
        asc_trans = trans.order_by('date')
        bal = 0
        for i in range(len(asc_trans)):
            p = 0
            if i == 0:
                prev = 0
            if asc_trans[i].transType == 'Billing':
                usage = asc_trans[i].usage
                bill = asc_trans[i].bill
                rate = asc_trans[i].ratescode
                cur = asc_trans[i].meterReading
                current = cur
                style = ''
                pb = ''
                bal+=bill
            elif asc_trans[i].transType == 'Payment':
                usage = ''
                bill = ''
                rate = ''
                prev = ''
                cur = ''
                style = 'text-success table-success'
                pb = asc_trans[i].processedBy
                bal=bal-asc_trans[i].payment
            date = asc_trans[i].date
            payment = asc_trans[i].payment
            ornum = asc_trans[i].or_number
            transid = asc_trans[i].transactionid
            bal = math.ceil(bal*100)/100
            new_row = ledgerclass(transid, date, prev, cur, usage, bill, payment, pb, ornum, bal, rate, style)
            table.append(new_row)
            if i < len(asc_trans)-1:
                if asc_trans[i+1].transType == 'Payment':
                    p = cur
                else:
                    p = p + current
            prev = p

    context = {
        'u':u,
        'table':table,
        'bal':math.ceil(bal*100)/100
    }
    return render(request, 'ledger.html', context)
    
def forgetpassword (request):

    if request.method == "POST":
        u_email = request.POST['email']
        if  SystemUsers.objects.filter(email = u_email).exists():
            user = SystemUsers.objects.get(email = u_email)
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
            messages.success(request, 'Please verify your account by clicking the link in your email: '+str(u_email))
                
            return redirect('login')
            
        context = {'email':email,'errors': errors}
    return render(request,'forgetpassword.html')




def password_reset_form(request):
    # form = SystemUserForm()
    # if request.method == "POST":
    #     print(request.POST)
    #     form = SystemUserForm(request.POST)

    return render(request,'password_reset_form')


def meterreading(request):
    meterred = ConsumerInfo.objects.all()
    return render(request,'meterreading.html',{'meterred': meterred})
def inputreading(request, id):
    table = []
    class meterreaderclass():
        def __init__(self, month, usage, reading):
            self.month = month
            self.usage = usage
            self.reading = reading
    consumer = ConsumerInfo.objects.get(consumer_id = id)
    trans = Transactions.objects.filter(acctID_id = id,transType = 'Billing')
    for t in trans:
        month = calendar.month_name[t.date.month]
        usage = t.usage
        reading = t.meterReading
        m = meterreaderclass(month, usage, reading)
        table.append(m)
    context = {
        'consumer':consumer,
        'table':table,
    }
    return render(request,'input-meter-reading.html', context)


def bills_list(request):
    bills_list = ConsumerInfo.objects.all()
    return render(request,'billslist.html',{'bills_list': bills_list})


def consumer_list(request):
    consumer_list = ConsumerInfo.objects.all()
    return render(request, 'conlist.html',{'consumer_list': consumer_list})


def sysuser(request):
    sysuser = SystemUsers.objects.all()



    
    return render(request, 'sysuser.html',{'sysuser':sysuser})


def consumercreation (request):
    form = ConsumerCreationForm()
    if request.method == "POST":
        print(request.POST)
        form = ConsumerCreationForm(request.POST)
        firstname  = request.POST['firstname']
        middlename = request.POST['middlename']
        lastname = request.POST['lastname']
        mobilenum = request.POST['mobilenum']
        email = request.POST['email']
        birthdate = request.POST['birthdate']
        sex = request.POST['sex']
        sitio = request.POST['sitio'] 
        homeaddress = request.POST['homeaddress']
        picture = request.POST['picture']
        meternumber = request.POST['meternumber']
        initialmeterreading = request.POST['initialmeterreading']
        installation_address = request.POST['installation']
        rateid = request.POST['rateid']
        if form.is_valid():
            cr = ConsumerInfo
            cr.firstname = firstname
            cr.middlename = middlename
            cr.lastname = lastname
            cr.mobilenum = mobilenum
            cr.email = email
            cr.birthdate = birthdate
            cr.sex = sex
            cr.sitio = sitio
            cr.homeaddress = homeaddress
            cr.picture = picture 
            cr.meternumber = meternumber
            cr.initialmeterreading = initialmeterreading
            cr.installation_address = installation_address
            cr.rateid = rateid
    context = {
        'form':form,
        'errors':form.errors,
    }
    return render(request, 'consumercreation.html',context)

def stopmeter(request, id):
    if request.method == 'POST':
        consumer = ConsumerInfo.objects.get(consumer_id = id)
        consumer.stopmeterflag = not consumer.stopmeterflag
        consumer.save()
    return redirect('inputreading', id = id)