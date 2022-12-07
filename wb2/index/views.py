import calendar
from datetime import datetime, timedelta
import datetime
from email import errors
from django.contrib import messages
from django.shortcuts import render
from django.shortcuts import redirect
from django.utils import timezone
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import EmailMessage
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.core.exceptions import ObjectDoesNotExist
from wb2.settings import EMAIL_HOST_USER
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import base64
from .DBdb import *
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
from django.shortcuts import render
from django.db.models import Q


def porter(request):
    porter_in()
    porter_out(sorted_tables)
    billing_out()
    balance()
    cons = ConsumerInfo.objects.all()
    for i in cons:
        i.cummulative = get_cummulative(i.consumer_id)
        i.save()
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
                login_rec = LoginRec()
                request.session[ReqParams.username] = user.username
                request.session[ReqParams.auth] = True
                request.session.modified = True
                # cache.set('message', message('success', 'Logged in as '+user.username, 5))
                login_rec.username = user.username
                login_rec.token = gen_token()
                login_rec.last_access = timezone.now()
                login_rec.expiration = login_rec.last_access + timedelta(minutes=ReqParams.expiration_time)
                login_rec.save()
                return redirect('bills_list')
            else:
                messages.error(request, "Invalid Password")
        else:
            messages.error(request, "Invalid Username")
    context = {
        'ReqParams':ReqParams,
    }
    return render(request, 'login.html', context)

# @authenticated_user
def bills_list(request):
    return redirect('bills_list_p', p=10)

# @authenticated_user
def meterreading(request):
    return redirect('meterreading_p', p=10)

# @authenticated_user
def bills_list_p(request, p):
    pages = int(p)
    user = request.session.get(ReqParams.username)
    count = bills.count()
    if pages == 0:
        paginate_by = request.GET.get('paginate_by', count)
    else:
        paginate_by = request.GET.get('paginate_by', pages)

    paginator = Paginator(bills, paginate_by)
    try:
        bills_list = paginator.page(page)

    except PageNotAnInteger:
        bills_list = paginator.page(1)

    except EmptyPage:
        bills_list = paginator.page(paginator.num_pages)
    
    context = {
        'last':range(paginator.num_pages - 3, paginator.num_pages),
        'five':range(1,6),
        'paginate_by': paginate_by,
        'bills_list': bills_list,
        'user': user,
    }
    return render(request, 'billslist.html', context)

def signout(request):
    lr = LoginRec.objects.get(username = request.session[ReqParams.username])
    lr.delete()
    messages.success(request, 'Logout successful')
    return redirect('login')


# @authenticated_user
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
            return redirect('bills_list')
    context = {
        'form': form,
        'errors': form.errors,
        'user': request.session.get(ReqParams.username)
    }
    return render(request, 'registration.html', context)


# @authenticated_user
def ledger(request, id):
    table = []
    year = datetime.today().year
    usage = 0
    transid = 0
    connectionType = 0
    pre = 0
    cur = 0
    pen = 0
    bill = 0
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
                pre = asc_trans[i].meterReading - usage
                pen = asc_trans[i].penaltyCode
                bill = asc_trans[i].bill
                connectionType = ConsumerType.objects.get(contypeid=asc_trans[i].contypeid).contype
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
            date = asc_trans[i].date
            payment = asc_trans[i].payment
            ornum = asc_trans[i].or_number
            transid = asc_trans[i].transactionid
            bal = math.ceil(bal*100)/100
            new_row = ledgerclass(transid, date, prev, cur, usage,bill, payment, pb, ornum, bal, connectionType, style)
            table.append(new_row)
            if i < len(asc_trans)-1:
                if asc_trans[i+1].transType == 'Payment' or asc_trans[i+1].transType == 'Discount':
                    p = cur
                else:
                    p = p + current
            prev = p

    context = {
        'month':calendar.month_name[datetime.today().month-1],
        'date_today':datetime.today(),
        'u': u,
        'table': table,
        'year': year,       
        'usage':usage,
        'transid':transid,
        'contype':connectionType,
        'pre':pre,
        'cur':cur,
        'pen':pen,
        'bal':bal,
        'bill':bill,
        'user':request.session.get(ReqParams.username)
    }
    return render(request, 'ledger.html', context)

@unauthenticated_user
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
                EMAIL_HOST_USER,
                [user.email],
            )
            email.fail_silently = True
            email.send()
            messages.success(
                request, 'Please verify your account by clicking the link in your email: '+str(u_email))

            return redirect('login')

        context = {'email': email, 'errors': errors}
    return render(request, 'forgetpassword.html')

# @unauthenticated_user
def password_reset_form(request):
    # form = SystemUserForm()
    # if request.method == "POST":
    #     print(request.POST)
    #     form = SystemUserForm(request.POST)

    return render(request, 'password_reset_form')


# @authenticated_user
def meterreading_p(request, p):
    meterred = ConsumerInfo.objects.all()
    months = []
    years = []
    class monthname():
        def __init__(self, name, num):
            self.name = name
            self.num = num
    for i in range(1, 13):
        month = calendar.month_name[i]
        months.append(monthname(month, i))
    
    
    pages = int(p)
    user = request.session.get(ReqParams.username)
    meterred = ConsumerInfo.objects.all().order_by('lastname', 'firstname', 'middlename')
    
    
    count = meterred.count()
    
    my = BarangayRecord.objects.all()
    for i in my:
        if i.year not in years:
            years.append(i.year)
    
    if pages == 0:
        paginate_by = request.GET.get('paginate_by', count)
    else:
        paginate_by = request.GET.get('paginate_by', pages)
    page = request.GET.get('page')

    paginator = Paginator(meterred, paginate_by)
    try:
        m = paginator.page(page)

    except PageNotAnInteger:
        m = paginator.page(1)

    except EmptyPage:
        m = paginator.page(paginator.num_pages)

    context = {
        'last':range(paginator.num_pages - 3, paginator.num_pages),
        'five':range(1,6),
        'paginate_by': paginate_by,
        'meterred': m,
        'user': user,
        'year': datetime.today().year,
        'months': months,
        'years':years
    }
    return render(request, 'meterreading.html', context)

# @authenticated_user
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
    alltrans = Transactions.objects.filter(acctID=consumer.consumer_id, transType='Billing')
    trans = Transactions.objects.filter(acctID=consumer.consumer_id, transType='Billing', year=year)

    if not trans:
        for i in range(1, 13):
            month = calendar.month_name[i]
            m = meterreaderclass('', month, '', '', '', '', '')
            table.append(m)
        context = {
            'consumer': consumer,
            'table': table,
            'cur_year': year,
            'years': years,
            'user': request.session.get(ReqParams.username)
        }
    else:
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
            m = meterreaderclass(transid, month, usage, prev, reading, next, style)
            table.append(m)

        con_penalty = Penalty.objects.get(penaltycode=consumer.penaltycode)
        cummulative = get_cummulative(id)
        interest = 0
        usage = 0
        if request.method == "POST":
            try:
                BarangayRecord.objects.get(barangaycode_id=consumer.installation_address_id, year=year)
            except ObjectDoesNotExist:
                con_b_rec = BarangayRecord()
            else:
                con_b_rec = BarangayRecord.objects.get(
                    barangaycode_id=consumer.installation_address_id, year=year)
                readings = []
            for i in range(12):
                r = request.POST.get('reading-'+calendar.month_name[i+1], 0)
                readings.append(int(r))
            d = 1
            bill = 0
            for i in readings:
                if i != 0:
                    if consumer.penaltycounter >= con_penalty.penalty_after and con_penalty.penalty_rate != 0:
                        xy = con_penalty.penalty_rate * cummulative
                        interest = xy/100
                    
                    t = Transactions.objects.filter(acctID=consumer, transType='Billing', year=year, month=d)
                    if not t:
                        # print("create transaction")
                        bill = 0
                        t = Transactions()
                        t.acctID = consumer
                        t.transType = 'Billing'
                        t.date = datetime.today()
                        t.month = d
                        t.year = year
                        t.meterReading = i
                        t.usage = i - lastreading
                        usage = i - lastreading
                        t.contypeid = consumer.contypeid_id
                        rate = ConsumerType.objects.get(contypeid=consumer.contypeid_id)
                        if t.usage <= rate.minReading:
                            t.bill = rate.minReadingCharge
                        else:
                            bill = ((t.usage - rate.minReading) * rate.rateAfterMin) + rate.minReadingCharge
                            t.bill = bill
                        t.payment = 0
                        t.processedBy = user.username
                        t.save()
                        if interest:
                            t = Transactions()
                            t.acctID = consumer
                            t.transType = 'Penalty'
                            t.date = datetime.today()
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
                            t.date = datetime.today()
                            t.month = d
                            t.year = year
                            t.bill = 0
                            t.payment = bill-(bill*(discount.discount_rate/100))
                            bill -= bill*(discount.discount_rate/100)
                            t.processedBy = user.username
                            t.save()
                    else:
                        # print("update transaction")
                        t = Transactions.objects.get(acctID=consumer.consumer_id, transType='Billing', year=year, month=d)
                        lastreading = Transactions.objects.get(acctID=consumer.consumer_id, transType='Billing', year=year, month=d-1).meterReading
                        try:
                            Transactions.objects.get(acctID=consumer.consumer_id, transType='Billing', year=year, month=d+1)
                        except ObjectDoesNotExist:
                            print("asdf")
                        else:
                            next = Transactions.objects.get(acctID=consumer.consumer_id, transType='Billing', year=year, month=d+1)
                            next.usage = next.meterReading - i
                            next.save()

                        lastreading = Transactions.objects.get(acctID=consumer.consumer_id, transType='Billing', year=year, month=d-1).meterReading
                        t.meterReading = i
                        t.date = datetime.today()
                        t.usage = i - lastreading
                        usage = i - lastreading
                        rate = ConsumerType.objects.get(contypeidid=t.contypeid)
                        if t.usage <= rate.minReading:
                            t.bill = rate.minReadingCharge
                        else:
                            t.bill = ((t.usage - rate.minReading) *
                                    rate.rateAfterMin) + rate.minReadingCharge
                        t.processedBy = user.username

                        t.save()
                        if interest:
                            t = Transactions()
                            t.acctID = consumer
                            t.transType = 'Penalty'
                            t.date = datetime.today()
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
                            t.date = datetime.today()
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
            return redirect('inputreading', id=id, year=datetime.today().year)

        # CHARLIE DIRI PAGHIMO

        context = {
            'consumer': consumer,
            'table': table,
            'cur_year': year,
            'years': years,
            'user': request.session.get(ReqParams.username)
        }
    return render(request, 'input-meter-reading.html', context)


# @authenticated_user
def consumer_list(request):
    return redirect('consumer_list_p', p=10)


def consumer_list_p(request, p):
    pages = int(p)
    user = request.session.get(ReqParams.username)
    cons = ConsumerInfo.objects.all().order_by('lastname', 'firstname', 'middlename')
    count = cons.count()
    if pages == 0:
        paginate_by = request.GET.get('paginate_by', count)
    else:
        paginate_by = request.GET.get('paginate_by', pages)
    page = request.GET.get('page')

    paginator = Paginator(cons, paginate_by)
    try:
        cons_list = paginator.page(page)

    except PageNotAnInteger:
        cons_list = paginator.page(1)

    except EmptyPage:
        cons_list = paginator.page(paginator.num_pages)

    context = {
        'last':range(paginator.num_pages - 3, paginator.num_pages),
        'five':range(1,6),
        'paginate_by': paginate_by,
        'consumer_list': cons_list,
        'user': user,
    }
    return render(request, 'conlist.html',context)

# @authenticated_user
def sysuser(request):
    sysuser = SystemUsers.objects.all()
    return render(request, 'sysuser.html', {'sysuser': sysuser})

# @authenticated_user
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
        'user': request.session.get(ReqParams.username)
    }
    return render(request, 'consumercreation.html', context)

# @authenticated_user
def stopmeter(request, id):
    if request.method == 'POST':
        consumer = ConsumerInfo.objects.get(consumer_id=id)
        consumer.stopmeterflag = not consumer.stopmeterflag
        consumer.save()
    return redirect('inputreading', id=id, year=datetime.today().year)

# @authenticated_user
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
        'table': table,
        'user': request.session.get(ReqParams.username)
    }
    return render(request, 'sysuser.html', context)

# @authenticated_user
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

# @authenticated_user
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
        'user': request.session.get(ReqParams.username)
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
        t.date = datetime.today()
        t.year = datetime.today().year
        t.month = datetime.today().month
        t.payment = amount
        t.processedBy = request.user.username
        t.or_number = or_num
        t.save()
        get_balance(id)
    return redirect('ledger', id=id)

def reports(request):
    return redirect('barangayreport', datetime.today().year)

# @authenticated_user
def barangayreport(request, year):
    years = []
    my = BarangayRecord.objects.all()
    for i in my:
        if i.year not in years:
            years.append(i.year)
    if int(year) in years:
        years.remove(int(year))
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
        'user': request.session.get(ReqParams.username)
    }
    return render(request, 'waterusage.html', context)


def view_barangay(request, id):
    bang = BarangayRecord.objects.get(barangayrec_id=id)

    context = {
        'bang': bang,


    }
    return render(request, 'view_barangay.html', context)


def unsettled_bill(request):
    ub = ConsumerInfo.objects.all()
    year = datetime.today().year
    print(year)
    context = {
        'year': year,
        'ub': ub
    }
    return render(request, 'unsettled_bill.html', context)


def usage_report_data(request, year):
    
    years = []
    class bm():
        def __init__(self, jan, feb, mar, apr, may, jun, jul, aug, sept, oct, nov, dec):
            self.jan = jan
            self.feb = feb
            self.mar = mar
            self.apr = apr
            self.may = may
            self.jun = jun
            self.jul = jul
            self.aug = aug
            self.sept = sept
            self.oct = oct
            self.nov = nov
            self.dec = dec
    my = BarangayRecord.objects.all()
    for i in my:
        if i.year not in years:
            years.append(i.year)
    if int(year) in years:
        years.remove(int(year))
        print(years)
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
    tu_bay = BarangayRecord.objects.filter(year=year,).annotate(sum=Sum(F('total_usage_jan') + F('total_usage_feb') + F('total_usage_mar') + F('total_usage_apr') + F('total_usage_may') + F('total_usage_jun') + F('total_usage_jul') + F('total_usage_aug') + F('total_usage_sept') + F('total_usage_oct') + F('total_usage_nov') + F('total_usage_dec')))

    context = {
        'tu_mon': tu_mon,
        'tu_bay': tu_bay,
        'cur_year': year,
        'years': years,
        'my': my,
        'user':request.session.get(ReqParams.username),

    }
    return render(request, 'usage_report_data.html', context)

def bbm (request,id):
    m = BarangayRecord.objects.filter(barangayrec_id = id).aggregate(
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
    context  = {
        'm'  : m,
   
    }
    return render (request, 'bbm.html', context)

def revenue_report(request, year):
    years = []
    my = BarangayRecord.objects.all()
    for i in my:
        if i.year not in years:
            years.append(i.year)
    if int(year) in years:
        years.remove(int(year))
        print(years)
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
    values = rev_col.values()
    col = sum(values)
    
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

    filt = dict((i, j) for i, j in rev_rec.items() if j >= 0)
    values = filt.values()
    rec = sum(values)
    # filter negative since mo float ang result niya, did you know its called 'dictionary value?' new learningss.

    context = {
        'my': my,
        'rev_col': rev_col,
        'rev_rec': filt,
        'cur_year': year,
        'years': years,
        'col': col,
        'rec': rec



    }
    return render(request, 'revenue_report.html',  context)


def deleteconsumer(request, id):
    con = ConsumerInfo.objects.get(consumer_id=id)
    con.delete()
    return redirect('consumer_list')


def unsettled_bills(request):
    return redirect('unsettled_bills_p', p=10)

def unsettled_bills_p(request, p):
    class ub_year:
        def __init__(self, y, u):
            self.y = y
            self.u = u
    tb =ConsumerInfo.objects.all().aggregate(tots = Sum('current_bal'))
    pages = int(p)
    ubs = ConsumerInfo.objects.filter(current_bal__gt=0).order_by('lastname', 'firstname', 'middlename')
    
    table = []
    for j in ubs:
        alltran = Transactions.objects.filter(acctID_id=j.consumer_id, transType='Billing')
        years = []
        for i in alltran:
            if i.year not in years:
                if i.year is not None:
                    years.append(i.year)
        years.reverse()
        if years:
            a = years[0]
        else:
            a = 0
        yeah = ub_year(a,j)
        table.append(yeah)
    count = len(table)
    if pages == 0:
        paginate_by = request.GET.get('paginate_by', count)
    else:
        paginate_by = request.GET.get('paginate_by', pages)
    page = request.GET.get('page')

    paginator = Paginator (table,paginate_by)
    try:
        ub = paginator.page(page)
    
    except PageNotAnInteger:
        ub = paginator.page(1)
    except EmptyPage:
        ub = paginator.page(paginator.num_pages)
    context = {
        'ub': ub,
        'paginate_by': paginate_by,
        'last' : range(paginator.num_pages-3, paginator.num_pages),
        'five' : range(1,6),
        'tb' : tb,
        'user' : request.session.get(ReqParams.username),
    }
    return render(request, 'unsettled_bill.html', context)

def view_unsettled_bills(request, id, year):
    years = []
    table = []
    uv = ConsumerInfo.objects.get(consumer_id=id)
    class view_utang():
        def __init__(self, month, reading, reading_date, usage, total_bill, total_amount_paid):
            self.month = month
            self.reading = reading
            self.reading_date = reading_date
            self.consumption = usage
            self.total_bill = total_bill
            self.total_amount_paid = total_amount_paid
    alltran = Transactions.objects.filter(acctID_id=id, transType='Billing')
    billing = Transactions.objects.filter(acctID_id=id, transType='Billing', year=year)
    payment = Transactions.objects.filter(acctID_id=id, transType='Payment', year=year)
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
    for i in range(1, 13):
        month = calendar.month_name[i]
        usage = 0
        reading = 0
        total_bill = 0
        reading_date = ''
        total_amount_paid = 0
        if c < pcount and pcount != 0:
            if i == payment[c].month:
                total_amount_paid = payment[c].payment
                c += 1
        if j < count and count != 0:
            if i == billing[j].month:
                usage = billing[j].usage
                reading = billing[j].meterReading
                reading_date = billing[j].date
                total_bill = billing[j].bill
                j += 1
                a = view_utang(month, reading, reading_date, usage,
                       total_bill, total_amount_paid)
        table.append(a)
    context = {'uv': uv,
               'years': years,
               'current': year,
               'table': table, }
    return render(request, 'view_unsettled_bills.html', context)


def discount(request):
    d = Discount.objects.all()
    form = addDiscount()
    discountidcount = len(Discount.objects.all())
    user = request.session.get(ReqParams.username)
    if request.method == "POST":
        form = addDiscount(request.POST)
        discount_rate = request.POST['discount_rate']
        if form.is_valid():
            addD = Discount()
            addD.discountcode = "D00"+str(discountidcount+1)
            addD.discount_rate = discount_rate
            addD.save()
    context = {
        'd': d,
        'form': form,
        'errors': form.errors,
        'user':user
    }
    return render(request, 'discount.html', context)


# @authenticated_user
def new_consumertype(request):
  
    c = ConsumerType.objects.all()
    form = ConscumertypecreationForm()
    contypecount = len(ConsumerType.objects.all())
    if request.method == "POST":
        form = ConscumertypecreationForm(request.POST)
        contype = request.POST['contype']
        minReading = request.POST['minReading']
        minReadingCharge = request.POST['minReadingCharge']
        rateAfterMin = request.POST['rateAfterMin']
        if form.is_valid():
            ct = ConsumerType()
            ct.contypeid = "C00"+str(contypecount+1)
            ct.contype = contype
            ct.minReading = minReading
            ct.minReadingCharge = minReadingCharge
            ct.rateAfterMin = rateAfterMin
            ct.added_by = None
            ct.save()
    context = {
        'c': c,
        'form': form,
        'errors': form.errors,
        'user' : request.session.get(ReqParams.username)
    }
    return render(request, 'new_consumertype.html', context)

@authenticated_user
def penalty(request):
    p = Penalty.objects.all()
    form = addPenalty
    penaltycounter = len(Penalty.objects.all())
    if request.method == "POST":
        form = addPenalty(request.POST)
        penalty_info = request.POST['penalty_info']
        penalty_rate = request.POST['penalty_rate']
        penalty_after = request.POST['penalty_after']
        daysappliedafter = request.POST['daysappliedafter']
        if form.is_valid():
            pen = Penalty()
            pen.penaltycode = "P00"+str(penaltycounter+1)
            pen.penalty_info = penalty_info
            pen.penalty_rate = penalty_rate
            pen.penalty_after = penalty_after
            pen.daysappliedafter = daysappliedafter
            pen.added_by = None
            pen.save()
        else:
            print("way ayo")
    context = {
        'p': p,
        'form': form,
        'errors': form.errors,
        'user' : request.session.get(ReqParams.username)
    }

    return render(request, 'penalty.html', context)


def bulkreading(request):
    consumers_list = []
    years = []
    my = BarangayRecord.objects.all()
    for i in my:
        if i.year not in years:
            years.append(i.year)
    if years[0]<years[len(years)-1]:
        years.reverse()
    class new_con():
        def __init__(self, con, prev, cur):
            self.con = con
            self.prev = prev
            self.cur = cur
    year = int(request.GET["year"])
    month = int(request.GET["month"])
    monthname = calendar.month_name[month]
    consumers = ConsumerInfo.objects.all()
    for i in years:
        if i > year:
            years.remove(i)
    for i in consumers:
        try:
            tran = Transactions.objects.get(acctID_id=i.consumer_id,month=month,year=year,transType = "Billing")
            cur = tran.meterReading
        except ObjectDoesNotExist: 
            cur = 0
        try:
            if month == 1:
                tran = Transactions.objects.get(acctID_id=i.consumer_id,month=12,year=year-1,transType = "Billing")
            else:    
                tran = Transactions.objects.get(acctID_id=i.consumer_id,month=month-1,year=year,transType = "Billing")
            prev = tran.meterReading
        except ObjectDoesNotExist:
            prev = 0
    
        consumers_list.append(new_con(i, prev, cur))
    context = {
        'year':year,
        'month':monthname,
        'consumers_list':consumers_list,
        'user':request.session[ReqParams.username]
    }
    return render(request,'bulkreading.html', context)

def save_bulk_reading(request):
    if request.method == "POST":
        print("asdjfhsf")
    return redirect('meterreading')
