import calendar
from dis import dis
from email import errors
from multiprocessing import context
from os import system
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.shortcuts import redirect
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import EmailMessage
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.core.exceptions import ObjectDoesNotExist
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
    # porter_in()
    # porter_out(sorted_tables)
    # billing_out()
    # balance()
    return render(request, "landing.html")

# @unauthenticated_user
def lp(request):
    return render(request, "landing.html")
# @unauthenticated_user
def signin(request):
    if request.method == "POST":
        u = request.POST['username']
        password = request.POST['password']
        pkval = SystemUsers.objects.filter(username=u)
        passAscii = password.encode("ascii")
        p = base64.b64encode(passAscii)
        if pkval.exists():
            user = SystemUsers.objects.get(username=u)
            if user.password == p:
                login(request, user)
                messages.success(request, 'Logged in')
                return redirect('bills_list')
            else:
                messages.error(request, "Invalid Password")
        else:
            messages.error(request, "Invalid Username")
    return render(request, 'login.html')
# @login_required(login_url='login')
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
        'form': form,
        'errors': form.errors,
    }
    return render(request, 'registration.html', context)

# @login_required(login_url='login')
def dashboard(request):
    user = request.user
    context = {
        'user': user
    }
    return render(request, 'dashboard.html', context)


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
    if ConsumerInfo.objects.filter(pk=id).exists():
        u = ConsumerInfo.objects.get(pk=id)
        trans = Transactions.objects.filter(acctID=u.consumer_id)
        asc_trans = trans.order_by('date')
        bal = 0
        p = 0
        current = 0
        print(asc_trans)
        for i in range(len(asc_trans)):
            if i == 0:
                prev = 0
            if asc_trans[i].transType == 'Billing':
                usage = asc_trans[i].usage
                bill = asc_trans[i].bill
                connectionType = Rates.objects.get(rate_id=asc_trans[i].ratescode)
                cur = asc_trans[i].meterReading
                current = cur
                style = ''
                pb = ''
                bal += bill
            elif asc_trans[i].transType == 'Payment':
                usage = ''
                bill = ''
                connectionType = ''
                prev = ''
                cur = ''
                style = 'text-success table-success'
                pb = asc_trans[i].processedBy
                bal = bal-asc_trans[i].payment
            date = asc_trans[i].date
            payment = asc_trans[i].payment
            ornum = asc_trans[i].or_number
            transid = asc_trans[i].transactionid
            bal = math.ceil(bal*100)/100
            new_row = ledgerclass(transid, date, prev, cur, usage, bill, payment, pb, ornum, bal, connectionType, style)
            table.append(new_row)
            if i < len(asc_trans)-1:
                if asc_trans[i+1].transType == 'Payment':
                    p = cur
                else:
                    p = p + current
            prev = p

    context = {
        'u': u,
        'table': table,
        'bal': math.ceil(bal*100)/100
    }
    return render(request, 'ledger.html', context)


def forgetpassword(request):

    if request.method == "POST":
        u_email = request.POST['email']
        if SystemUsers.objects.filter(email=u_email).exists():
            user = SystemUsers.objects.get(email=u_email)
            user.is_active = False
            user.save()

            current_site = get_current_site(request)
            email_subject = "Confirm your Email"
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = generate_token.make_token(user)
            message = render_to_string('email_verif.html', {
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
            messages.success(
                request, 'Please verify your account by clicking the link in your email: '+str(u_email))

            return redirect('login')

        context = {'email': email, 'errors': errors}
    return render(request, 'forgetpassword.html')


def password_reset_form(request):
    # form = SystemUserForm()
    # if request.method == "POST":
    #     print(request.POST)
    #     form = SystemUserForm(request.POST)

    return render(request, 'password_reset_form')


def meterreading(request):
    meterred = ConsumerInfo.objects.all()
    context = {
        'meterred': meterred,
        'year': date.today().year
    }
    return render(request, 'meterreading.html', context)


def inputreading(request, id, year):
    table = []
    years = []
    class meterreaderclass():
        def __init__(self, transid , month, usage, prev, reading):
            self.transid = transid
            self.month = month
            self.usage = usage
            self.prev = prev
            self.reading = reading
    consumer = ConsumerInfo.objects.get(consumer_id = id)
    lastid = Transactions.objects.latest('transactionid').transactionid
    alltrans = Transactions.objects.filter(acctID_id = id, transType = 'Billing')
    trans = Transactions.objects.filter(acctID_id = id, transType = 'Billing', date__year = year)
    dec = None
    if year<date.today().year:
        nexttrans = Transactions.objects.filter(acctID_id = id, transType = 'Billing', date__year = year+1)
        try:
            dec = nexttrans.get(date__month=1)
        except ObjectDoesNotExist:
            dec = None
    asc_trans = trans.order_by('date')
    count = len(asc_trans)
    j = 0
    if asc_trans[0].date.month == 1:
        j = 1
    for i in alltrans:
        if i.date.year not in years:
            years.append(i.date.year)
    if int(year) in years:
        years.remove(int(year))
    # print(asc_trans)
    # print(count)
    lastreading = 0
    for i in range(1,13):
        month = calendar.month_name[i]
        lastid+=1
        transid = lastid
        usage = 0
        prev = lastreading
        reading = prev
        if i<12:
            # print(str(i)+" "+str(j+1))
            if j<count and count != 0:
                if i == asc_trans[j].date.month-1:
                    transid = asc_trans[j].transactionid
                    usage = asc_trans[j].usage
                    reading = asc_trans[j].meterReading
                    prev = asc_trans[j].meterReading-usage
                    lastreading = reading
                    j+=1
        else:
            if dec:
                transid = dec.transactionid
                usage = dec.usage
                reading = dec.meterReading
                prev = asc_trans[j].meterReading-usage
        print(str(prev)+" "+str(reading))
        m = meterreaderclass(transid, month, usage, prev, reading)
        table.append(m)
        
    if request.method=="POST":
        readings = []
        for i in range(12):
            r = request.POST.get('reading-'+calendar.month_name[i+1],0)
            readings.append(int(r))
            if r!=0:
                try:
                    Transactions.objects.get(acctID_id=id, transType = 'Billing',date__year=year,date__month=i+1)
                except ObjectDoesNotExist:
                    t = Transactions()
                    t.acctID = id
                    t.transType = 'Billing'
                    t.date = date.today()
                    t.meterReading = r

                else:
                    t = Transactions.objects.get(acctID_id=id, transType = 'Billing',date__year=year,date__month=i+1)
        print(readings)
    context = {
        'consumer':consumer,
        'table':table,
        'cur_year':year,
        'years':years
    }
    return render(request, 'input-meter-reading.html', context)


def bills_list(request):
    bills_list = ConsumerInfo.objects.all()
    return render(request, 'billslist.html', {'bills_list': bills_list})


def consumer_list(request):
    consumer_list = ConsumerInfo.objects.all()
    return render(request, 'conlist.html', {'consumer_list': consumer_list})


def sysuser(request):
    sysuser = SystemUsers.objects.all()
    return render(request, 'sysuser.html', {'sysuser': sysuser})


def consumercreation(request):
    form = ConsumerCreationForm()
    if request.method == "POST":
        print(request.POST)
        form = ConsumerCreationForm(request.POST)
        firstname = request.POST['firstname']
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
        'form': form,
        'errors': form.errors,
    }
    return render(request, 'consumercreation.html', context)


def stopmeter(request, id):
    if request.method == 'POST':
        consumer = ConsumerInfo.objects.get(consumer_id=id)
        consumer.stopmeterflag = not consumer.stopmeterflag
        consumer.save()
    return redirect('inputreading', id=id, year=date.today().year)


def sysuser(request):
    table = []

    class sysuserclass():
        def __init__(self, first_name, last_name, mid_name, username, email, role):
            self.email = email
            self.first_name = first_name
            self.mid_name = mid_name
            self.last_name = last_name
            self.username = username
            self.role = role
    sys = SystemUsers.objects.all()
    for s in sys:
        firstname = s.first_name
        lastname = s.last_name
        username = s.username
        midname = s.mid_name
        email = s.email
        role = ""
        if s.is_admin:
            role = role + "Admin "
        if s.is_teller:
            role = role + "Teller "
        if s.is_supervisor:
            role = role + "Supervisor "
        if s.is_manager:
            role = role + "Manager "
        if s.is_reader:
            role = role + "Reader "

        su = sysuserclass(firstname, lastname, midname, username, email, role)
        table.append(su)
    context = {
        'table': table
    }
    return render(request, 'sysuser.html', context)


def userupdate(request, id):
    user = ConsumerInfo.objects.get(consumer_id=id)
    form = Userinfoupdate(instance=user)
    if request.method == 'POST':
        form = Userinfoupdate(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('consumer_list')
    context = {
        'form': form,
        'user': user

    }

    return render(request, 'userupdate.html', context)


def user_edit(request, id):
    sys = SystemUsers.objects.get(username=id)
    form = sysup(instance=sys)
    if request.method == 'POST':
        form = sysup(request.POST, instance=sys)
        if form.is_valid():
            form.save()
        return redirect('sysuser')
    context = {
        'form': form,
        'sys':sys
    }
    return render(request, 'user_edit.html', context)
