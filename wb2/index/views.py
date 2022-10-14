import calendar
from datetime import datetime

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
from .functions import *
import math
from .tokens import generate_token
from django.core.files.storage import FileSystemStorage
from django.db.models import F, Sum
from .decorators import unauthenticated_user


def porter(request):
    porter_in()
    porter_out(sorted_tables)
    billing_out()
    balance()
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

# @login_required(login_url='login')
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
        asc_trans = trans.order_by('year', 'month', 'transactionid')
        bal = 0
        current = 0
        for i in range(len(asc_trans)):
            p = 0
            if i == 0:
                prev = 0
            if asc_trans[i].transType == 'Billing':
                usage = asc_trans[i].usage
                bill = asc_trans[i].bill
                connectionType = Rates.objects.get(
                rate_id=asc_trans[i].ratescode)
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
            elif asc_trans[i].transType == 'Penalty':
                usage = ''
                bill = asc_trans[i].bill
                connectionType = ''
                prev = ''
                cur = ''
                style = 'text-danger table-danger'
                pb = asc_trans[i].processedBy
                bal += bill
            elif asc_trans[i].transType == 'Discount':
                usage = ''
                bill = asc_trans[i].bill
                connectionType = ''
                prev = ''
                cur = ''
                style = 'text-primary table-primary'
                pb = asc_trans[i].processedBy
                bal = bal-asc_trans[i].payment
            mdate = asc_trans[i].date
            payment = asc_trans[i].payment
            ornum = asc_trans[i].or_number
            transid = asc_trans[i].transactionid
            bal = math.ceil(bal*100)/100
            new_row = ledgerclass(transid, mdate, prev, cur, usage,
                                  bill, payment, pb, ornum, bal, connectionType, style)
            table.append(new_row)
            if i < len(asc_trans)-1:
                if asc_trans[i+1].transType == 'Payment' or asc_trans[i+1].transType == 'Discount':
                    p = cur
                else:
                    p = p + current
            prev = p
    year = date.today().year
    context = {
        'u': u,
        'table': table,
        'year': year,
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

# @login_required(login_url='login')
def meterreading(request):
    meterred = ConsumerInfo.objects.all()
    context = {
        'meterred': meterred,
        'year': date.today().year
    }
    return render(request, 'meterreading.html', context)


# @login_required(login_url='login')
def inputreading(request, id, year):
    table = []
    years = []

    class meterreaderclass():
        def __init__(self, transid, month, usage, prev, reading, next, style):
            self.transid = transid
            self.month = month
            self.usage = usage
            self.prev = prev
            self.reading = reading
            self.next = next
            self.style = style
    user = request.user
    consumer = ConsumerInfo.objects.get(consumer_id=id)
    lastid = Transactions.objects.latest('transactionid').transactionid
    alltrans = Transactions.objects.filter(acctID_id=id, transType='Billing')
    trans = Transactions.objects.filter(acctID_id=id, transType='Billing', year=year)
    asc_trans = trans.order_by('month')
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
    j = 0
    lastreading = 0
    for i in range(1, 13):
        month = calendar.month_name[i]
        lastid += 1
        transid = lastid
        usage = 0
        prev = lastreading
        reading = 0
        style = ''
        next = False
        # print(str(i)+" "+str(j+1))
        if j < count and count != 0:
            if i == asc_trans[j].month:
                transid = asc_trans[j].transactionid
                usage = asc_trans[j].usage
                reading = asc_trans[j].meterReading
                prev = asc_trans[j].meterReading-usage
                if j < count-1:
                    next = asc_trans[j+1].meterReading
                else:
                    next = False
                lastreading = reading
                style = 'table-success'
                j += 1
        # print(str(prev)+" "+str(reading)+" "+str(next))
        m = meterreaderclass(transid, month, usage, prev, reading, next, style)
        table.append(m)
        print(table)

    con_penalty = Penalty.objects.get(penaltycode=consumer.penaltycode)
    cummulative = get_cummulative(id)
    interest = 0
    usage = 0
    if request.method == "POST":
        try:
            BarangayRecord.objects.get(
                barangaycode_id=consumer.installation_address_id, year=year)
        except ObjectDoesNotExist:
            con_b_rec = BarangayRecord()
        else:
            con_b_rec = BarangayRecord.objects.get(barangaycode_id = consumer.installation_address_id, year = year)
            readings = []
        for i in range(12):
            r = request.POST.get('reading-'+calendar.month_name[i+1], 0)
            readings.append(int(r))
        # print(readings)
        d = 1
        for i in readings:
            if i != 0:
                if consumer.penaltycounter >= con_penalty.penalty_after and con_penalty.penalty_rate != 0:
                  # via percentage
                    xy = con_penalty.penalty_rate * cummulative
                    interest = xy/100
                try:
                    Transactions.objects.get(
                        acctID_id=id, transType='Billing', year=year, month=d)
                except ObjectDoesNotExist:
                    # print("create transaction")
                    bill = 0
                    t = Transactions()
                    t.acctID = id
                    t.transType = 'Billing'
                    t.date = date.today()
                    t.month = d
                    t.year = year
                    t.meterReading = i
                    t.usage = i - lastreading
                    usage = i - lastreading
                    t.ratescode = consumer.rateid_id
                    rate = Rates.objects.get(rate_id=consumer.rateid_id)
                    if t.usage <= rate.minReading:
                        t.bill = rate.minReadingCharge
                    else:
                        xcubic = t.usage - rate.minReading
                        xmincharge = xcubic * rate.rateAfterMin
                        bill = xmincharge + rate.minReadingCharge
                        t.bill = xmincharge + rate.minReadingCharge
                    t.payment = 0
                    t.processedBy = user.username
                    t.save()
                    if interest:
                        t = Transactions()
                        t.acctID = consumer
                        t.transType = 'Penalty'
                        t.date = date.today()
                        t.month = d
                        t.year = year
                        t.bill = interest
                        bill += interest
                        t.payment = 0
                        t.processedBy = user.username
                        t.save()
                    if consumer.discountcode is not None:
                        discount = consumer.discountcode
                        t = Transactions()
                        t.acctID = consumer
                        t.transType = 'Discount'
                        t.date = date.today()
                        t.month = d
                        t.year = year
                        t.bill = 0
                        t.payment = bill-(bill*(discount.discount_rate/100))
                        bill -= bill*(discount.discount_rate/100)
                        t.processedBy = user.username
                        t.save()
                else:
                    # print("update transaction")
                    t = Transactions.objects.get(
                        acctID_id=id, transType='Billing', year=year, month=d)
                    lastreading = Transactions.objects.get(
                        acctID_id=id, transType='Billing', year=year, month=d-1).meterReading
                    try:
                        Transactions.objects.get(
                            acctID_id=id, transType='Billing', year=year, month=d+1)
                    except ObjectDoesNotExist:
                        print("asdf")
                    else:
                        next = Transactions.objects.get(
                            acctID_id=id, transType='Billing', year=year, month=d+1)
                        next.usage = next.meterReading - i
                        next.save()

                    lastreading = Transactions.objects.get(
                        acctID_id=id, transType='Billing', year=year, month=d-1).meterReading
                    t.meterReading = i
                    t.date = date.today()
                    t.usage = i - lastreading
                    usage = i - lastreading
                    rate = Rates.objects.get(rate_id=t.ratescode)
                    if t.usage <= rate.minReading:
                        t.bill = rate.minReadingCharge
                    else:
                        xcubic = t.usage - rate.minReading
                        xmincharge = xcubic * rate.rateAfterMin
                        t.bill = xmincharge + rate.minReadingCharge
                    t.processedBy = user.username

                    t.save()
                    if interest:
                        t = Transactions()
                        t.acctID = consumer
                        t.transType = 'Penalty'
                        t.date = date.today()
                        t.month = d
                        t.year = year
                        t.bill = interest
                        t.payment = 0
                        t.processedBy = user.username
                        t.save()
                    if consumer.discountcode is not None:
                        discount = consumer.discountcode
                        t = Transactions()
                        t.acctID = consumer
                        t.transType = 'Discount'
                        t.date = date.today()
                        t.month = d
                        t.year = year
                        t.bill = 0
                        t.payment = bill-(bill*(discount.discount_rate/100))
                        bill -= bill*(discount.discount_rate/100)
                        t.processedBy = user.username
                        t.save()
                get_balance(id)

            match d:
                case 1:
                    con_b_rec.total_due_jan += bill
                    con_b_rec.total_usage_jan += usage
                case 2:
                    con_b_rec.total_due_feb += bill
                    con_b_rec.total_usage_feb += usage
                case 3:
                    con_b_rec.total_due_mar += bill
                    con_b_rec.total_usage_mar += usage
                case 4:
                    con_b_rec.total_due_apr += bill
                    con_b_rec.total_usage_apr += usage
                case 5:
                    con_b_rec.total_due_may += bill
                    con_b_rec.total_usage_may += usage
                case 6:
                    con_b_rec.total_due_jun += bill
                    con_b_rec.total_usage_jun += usage
                case 7:
                    con_b_rec.total_due_jul += bill
                    con_b_rec.total_usage_jul += usage
                case 8:
                    con_b_rec.total_due_aug += bill
                    con_b_rec.total_usage_aug += usage
                case 9:
                    con_b_rec.total_due_sept += bill
                    con_b_rec.total_usage_sept += usage
                case 10:
                    con_b_rec.total_due_oct += bill
                    con_b_rec.total_usage_oct += usage
                case 11:
                    con_b_rec.total_due_nov += bill
                    con_b_rec.total_usage_nov += usage
                case 12:
                    con_b_rec.total_due_dec += bill
                    con_b_rec.total_usage_dec += usage
            d += 1
        return redirect('inputreading', id=id, year=date.today().year)

    # CHARLIE DIRI PAGHIMO

    context = {
        'consumer': consumer,
        'table': table,
        'cur_year': year,
        'years': years
    }
    return render(request, 'input-meter-reading.html', context)



# def landing(request):
#     return render(request,'landing.html')

# @login_required(login_url='login')
def bills_list(request):
    user = request.user
    bills_list = ConsumerInfo.objects.all()
    context = {
        'bills_list': bills_list,
        'user': user,
    }
    return render(request, 'billslist.html', context)

# @login_required(login_url='login')
def consumer_list(request):
    consumer_list = ConsumerInfo.objects.all()
    return render(request, 'conlist.html', {'consumer_list': consumer_list})

# @login_required(login_url='login')
def sysuser(request):
    sysuser = SystemUsers.objects.all()
    return render(request, 'sysuser.html', {'sysuser': sysuser})

# @login_required(login_url='login')
def consumercreation(request):
    form = ConsumerCreationForm()
    if request.method == "POST":
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
        installation_address = request.POST['installation_address']
        rateid = request.POST['rateid']
        if form.is_valid():
            cr = ConsumerInfo()
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
            cr.save()
            return redirect('consumer_list')
    context = {
        'form': form,
        'errors': form.errors,
    }
    return render(request, 'consumercreation.html', context)

# @login_required(login_url='login')
def stopmeter(request, id):
    if request.method == 'POST':
        consumer = ConsumerInfo.objects.get(consumer_id=id)
        consumer.stopmeterflag = not consumer.stopmeterflag
        consumer.save()
    return redirect('inputreading', id=id, year=date.today().year)

# @login_required(login_url='login')
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

# @login_required(login_url='login')
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

    return render(request, 'consumercreation.html', context)

# @login_required(login_url='login')
def user_edit(request, id):
    sys = SystemUsers.objects.get(username=id)
    encoded = sys.password
    decode64 = base64.b64decode(encoded)
    password = decode64.decode("ascii")
    form = sysup(instance=sys)
    if request.method == 'POST':
        form = sysup(request.POST, instance=sys)
        # pic = request.POST['profilepic']
        if form.is_valid():
            upload = request.FILES['profilepic']
            fss = FileSystemStorage()
            fss.save(upload.name, upload)
            # sys.profilepic = pic
            sys.save()

        return redirect('sysuser')
    context = {
        'sys': sys,
        'form': form,
        'password': password,
    }
    return render(request, 'user_edit.html', context)


def deleteUser(request, id):
    sys = SystemUsers.objects.get(username=id)
    if request.method == "POST":
        sys.delete()
        return redirect('sysuser')
    return render(request, 'delete.html',)


def about(request):
    return render(request, 'about.html')

def payment(request, id):
    if request.method == 'POST':
        amount = request.POST['amount']
        or_num = request.POST['or_num']
        t = Transactions()
        t.acctID = ConsumerInfo.objects.get(consumer_id=id)
        t.transType = "Payment"
        t.date = date.today()
        t.year = date.today().year
        t.month = date.today().month
        t.payment = amount
        t.processedBy = request.user.username
        t.or_number = or_num
        t.save()
        get_balance(id)
    return redirect('ledger', id=id)

def br(request):
    return redirect('barangayreport', date.today().year)
# @login_required(login_url='login')
def barangayreport(request, year):
    years = []
    my = BarangayRecord.objects.all()
    for i in my:
        if i.year not in years:
            years.append(i.year)
    if int(year) in years:
        years.remove(int(year))
        print(years)
    br = BarangayRecord.objects.filter(year=year).annotate(
        total_usage=F('total_usage_jan') + F('total_usage_feb') + F('total_usage_mar') + F('total_usage_apr') + F('total_usage_may') + F('total_usage_jun') +
        F('total_usage_jul') + F('total_usage_aug') + F('total_usage_sept') +
        F('total_usage_oct') + F('total_usage_nov') + F('total_usage_dec'),
        total_due=F('total_due_jan') + F('total_due_feb') + F('total_due_mar') + F('total_due_apr') + F('total_due_may') + F('total_due_jun') +
        F('total_due_jul') + F('total_due_aug') + F('total_due_sept') +
        F('total_due_oct') + F('total_due_nov') + F('total_due_dec'),
        total_paid=F('total_paid_jan') + F('total_paid_feb') + F('total_paid_mar') + F('total_paid_apr') + F('total_paid_may') + F('total_paid_jun') +
        F('total_paid_jul') + F('total_paid_aug') + F('total_paid_sept') +
        F('total_paid_oct') + F('total_due_nov') + F('total_paid_dec'),
        total_rec=F('total_due') - F('total_paid')
    )
    fr = BarangayRecord.objects.filter(year=year).annotate(
        total_usage=F('total_usage_jan') + F('total_usage_feb') + F('total_usage_mar') + F('total_usage_apr') + F('total_usage_may') + F('total_usage_jun') +
        F('total_usage_jul') + F('total_usage_aug') + F('total_usage_sept') +
        F('total_usage_oct') + F('total_usage_nov') + F('total_usage_dec'),
        total_due=F('total_due_jan') + F('total_due_feb') + F('total_due_mar') + F('total_due_apr') + F('total_due_may') + F('total_due_jun') +
        F('total_due_jul') + F('total_due_aug') + F('total_due_sept') +
        F('total_due_oct') + F('total_due_nov') + F('total_due_dec'),
        total_paid=F('total_paid_jan') + F('total_paid_feb') + F('total_paid_mar') + F('total_paid_apr') + F('total_paid_may') + F('total_paid_jun') +
        F('total_paid_jul') + F('total_paid_aug') + F('total_paid_sept') +
        F('total_paid_oct') + F('total_due_nov') + F('total_paid_dec'),
        total_rec=F('total_due') - F('total_paid')
    ).aggregate(
        tu=Sum('total_usage'),
        tp=Sum('total_paid'),
        tr=Sum('total_due') - Sum('total_paid')
    )
    context = {
        'br': br,
        'cur_year': year,
        'years': years,
        'fr': fr,


    }
    return render(request, 'waterusage.html', context)


def view_barangay(request, id):
    bang = BarangayRecord.objects.get(barangayrec_id=id)
    context = {
        'bang': bang
    }
    return render(request, 'view_barangay.html', context)

def unsettled_bill(request):
    ub = ConsumerInfo.objects.all()
    context = {
        'ub':ub
    }
    return render(request, 'unsettled_bill.html', context)



def usage_report_data(request, year):
    years = []
    my = BarangayRecord.objects.all()
    for i in my:
        if i.year not in years:
            years.append(i.year)
    if int(year) in years:
        years.remove(int(year))
        print(i)
    # Monthly total usage
    tu_mon = BarangayRecord.objects.filter(year=year).aggregate(
        jan=Sum('total_usage_jan'),
        feb=Sum('total_usage_feb'),
        mar=Sum('total_usage_mar'),
        apr=Sum('total_usage_apr'),
        may=Sum('total_usage_may'),
        jun=Sum('total_usage_jun'),
        jul=Sum('total_usage_jul'),
        aug=Sum('total_usage_aug'),
        sept=Sum('total_usage_sept'),
        oct=Sum('total_usage_oct'),
        nov=Sum('total_usage_nov'),
        dec=Sum('total_usage_dec'),
    )

    # By Barangay total Usage
    tu_bay = BarangayRecord.objects.filter(year=year,).annotate(sum=Sum(
        F('total_usage_jan') + F('total_usage_feb') + F('total_usage_mar') + F('total_usage_apr') + F('total_usage_may') + F('total_usage_jun') +
        F('total_usage_jul') + F('total_usage_aug') + F('total_usage_sept') +
        F('total_usage_oct') + F('total_usage_nov') + F('total_usage_dec')
    )
    ).order_by()

    context = {
        'tu_mon': tu_mon,
        'tu_bay': tu_bay,
        'cur_year': year,
        'years': years,

    }
    return render(request, 'usage_report_data.html', context)


def barangay_by_monthly(request, id, year):
    bbm = BarangayRecord.objects.filter(barangayrec_id=id, year=year).aggregate(
        jan=Sum('total_usage_jan'),
        feb=Sum('total_usage_feb'),
        mar=Sum('total_usage_mar'),
        apr=Sum('total_usage_apr'),
        may=Sum('total_usage_may'),
        jun=Sum('total_usage_jun'),
        jul=Sum('total_usage_jul'),
        aug=Sum('total_usage_aug'),
        sept=Sum('total_usage_sept'),
        oct=Sum('total_usage_oct'),
        nov=Sum('total_usage_nov'),
        dec=Sum('total_usage_dec'),
    )
    context = {
        'bbm': bbm
    }
    return render(request, 'usage_report_data.html', context)

def revenue_report(request, year):
    years = []
    my = BarangayRecord.objects.all()
    for i in my:
        if i.year not in years:
            years.append(i.year)
    if int(year) in years:
        years.remove(int(year))

    # Total Collection
    rev_col = BarangayRecord.objects.filter(year=year).aggregate(
        jan=Sum('total_paid_jan'),
        feb=Sum('total_paid_feb'),
        mar=Sum('total_paid_mar'),
        apr=Sum('total_paid_apr'),
        may=Sum('total_paid_may'),
        jun=Sum('total_paid_jun'),
        jul=Sum('total_paid_jul'),
        aug=Sum('total_paid_aug'),
        sept=Sum('total_paid_sept'),
        oct=Sum('total_paid_oct'),
        nov=Sum('total_paid_nov'),
        dec=Sum('total_paid_dec'),
    )
    # Total Receivables
    rev_rec = BarangayRecord.objects.filter(year=year).aggregate(
        jan=Sum('total_due_jan') - Sum('total_paid_jan'),
        feb=Sum('total_due_feb') - Sum('total_paid_jan'),
        mar=Sum('total_due_mar') - Sum('total_paid_jan'),
        apr=Sum('total_due_apr') - Sum('total_paid_jan'),
        may=Sum('total_due_may') - Sum('total_paid_jan'),
        jun=Sum('total_due_jun') - Sum('total_paid_jan'),
        jul=Sum('total_due_jul') - Sum('total_paid_jan'),
        aug=Sum('total_due_aug') - Sum('total_paid_jan'),
        sept=Sum('total_due_sept') - Sum('total_paid_jan'),
        oct=Sum('total_due_oct') - Sum('total_paid_jan'),
        nov=Sum('total_due_nov') - Sum('total_paid_jan'),
        dec=Sum('total_due_dec') - Sum('total_paid_jan'),
    )

    context = {
        'rev_col': rev_col,
        'rev_rec': rev_rec,
        'cur_year': year,
        'years': years,
    }
    return render( request, 'revenue_report.html',  context)


def deleteconsumer(request, id):
    con = ConsumerInfo.objects.get(consumer_id = id)
    con.delete()
    return redirect('consumer_list')

def unsettled_bill(request):
    ub = ConsumerInfo.objects.all()
    context = {
        'ub':ub
    }
    return render(request, 'unsettled_bill.html', context)


def view_unsettled_bills(request, id, year):
    years = []
    table = []
    uv = ConsumerInfo.objects.get(consumer_id=id)
    class view_utang():
        def __init__(self, month, reading, reading_date, usage,total_bill,total_amount_paid):
            self.month = month
            self.reading = reading
            self.reading_date = reading_date
            self.consumption = usage
            self.total_bill = total_bill
            self.total_amount_paid = total_amount_paid
    con = ConsumerInfo.objects.get(consumer_id=id)
    alltran = Transactions.objects.filter(acctID_id=id, transType='Billing')
    billing = Transactions.objects.filter(acctID_id=id, transType='Billing',  year=year)
    payment = Transactions.objects.filter(acctID_id=id, transType = 'Payment', year = year)
    pcount = len(payment)
    count = len(billing)
    j = 0
    if billing[0].date.month == 1:
        j = 1
    for i in alltran:
            if i.year not in years:
                if i.year is not None:
                    years.append(i.year)
    if int(year) in years:
            years.remove(int(year))
    # --------------------------#
    j = 0
    c = 0
    for i in range(1,13):
        month = calendar.month_name[i]
        usage = 0
        reading = 0
        total_bill = 0
        reading_date = ''
        total_amount_paid = 0
        if c < pcount and pcount !=0:
            if i == payment[c].month:
                total_amount_paid= payment[c].payment
                c+=1
        if j < count and count != 0:
            if i == billing[j].month:
                usage = billing[j].usage
                reading = billing[j].meterReading
                reading_date = billing[j].date
                total_bill = billing[j].bill
                j += 1

        a = view_utang(month, reading, reading_date, usage,total_bill,total_amount_paid)
        table.append(a)

    context ={'uv':uv,
            'years':years,
            'current':year,
            'table':table,}
    return render(request, 'view_unsettled_bills.html', context)
