

import calendar
import math
import datetime
from .dataporter import *
from .DBdb import *
from .decorators import *
from .forms import *
from .functions import *
from .models import *
from .tokens import generate_token
from datetime import datetime, timedelta
from django import template
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import EmailMultiAlternatives, send_mail, BadHeaderError, EmailMessage
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.db.models import F, Sum, Q
from django.db.models.functions import Greatest
from django.shortcuts import render, redirect
from django.utils import timezone
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.core.files.storage import FileSystemStorage



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


@unauthenticated_user
def lp(request):
    enye(ConsumerInfo.objects.all())
    camelize()
    # capitalize()
    return render(request, "landing.html")

@unauthenticated_user
def signin(request):
    if request.method == "POST":
        u = request.POST['username']
        password = request.POST['password']
        auth = authenticate(username=u, password=password)
        if auth is not None:
            user = SystemUsers.objects.get(username=u)
            login_rec = LoginRec()
            request.user = user.username
            request.session[ReqParams.auth] = True
            request.session.modified = True
            login_rec.username = user.username
            login_rec.token = gen_token()
            login_rec.last_access = timezone.now()
            login_rec.expiration = login_rec.last_access + timedelta(minutes=ReqParams.expiration_time)
            login_rec.save()
            login(request, auth)
            messages.success(request, "Logged In as " + user.username)
            return redirect('bills_list')
        else:
            messages.error(request, "Invalid Username or Password")
    context = {
        'ReqParams': ReqParams,
    }
    return render(request, 'login.html', context)

@login_required(login_url='login')
def bills_list(request):
    return redirect('bills_list_p', p=10)

@login_required(login_url='login')


def meterreading(request):
    return redirect('meterreading_p', p=10)

@login_required(login_url='login')
def bills_list_p(request, p):
    template = ""
    LoginSession = request.user
    if LoginSession:
        if LoginSession.is_teller or LoginSession.is_supervisor:
            template = redirect('bills_list_p', p=10)
        else:
            if LoginSession.is_admin:
                template = redirect('sysuser')
            else:
                if LoginSession.is_reader:
                    template = redirect('meterreading_p', p=10)
            return template

    search = request.GET.get("search", "")
    page = request.GET.get('page')
    isnum = search.isnumeric()
    if search:
        if isnum:
            bills = ConsumerInfo.objects.filter(Q(meternumber=search) | Q(consumer_id=search),deleteflag=0).order_by('lastname', 'firstname', 'middlename')
        else:
            bills = ConsumerInfo.objects.filter(Q(firstname__icontains=search) | Q(middlename__icontains=search) | Q(lastname__icontains=search),deleteflag=0).order_by('lastname', 'firstname', 'middlename')
    else:
        bills = ConsumerInfo.objects.filter(deleteflag=0).order_by('lastname', 'firstname', 'middlename')
    pages = int(p)
    user = request.user
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
        'search': search,
        'last': range(paginator.num_pages - 3, paginator.num_pages),
        'five': range(1, 6),
        'paginate_by': paginate_by,
        'bills_list': bills_list,
        'user': user,
    }
    return render(request, 'billslist.html', context)

@login_required(login_url='login')
def signout(request):
    try:
        lr = LoginRec.objects.get(username=request.user)
        lr.delete()
    except ObjectDoesNotExist:
        pass
    logout(request)
    messages.success(request, 'Logout successful')
    return redirect('login')

@login_required(login_url='login')
def user_creation(request):
    template = ""
    LoginSession = request.user
    if LoginSession:
        if LoginSession.is_admin:
            template = "registration.html"
        else:
            template = redirect('bills_list')
            return template

    form = SystemUserForm()
    if request.method == "POST":
        form = SystemUserForm(request.POST)
        username = request.POST['username']
        firstname = request.POST['first_name']
        midname = request.POST['mid_name']
        lastname = request.POST['last_name']
        mobilenum = request.POST['mobilenum']
        email = request.POST['email']
        password2 = request.POST['password2']
        is_teller = request.POST.get('is_teller','') == 'on'
        is_admin = request.POST.get('is_admin','') == 'on'
        is_supervisor = request.POST.get('is_supervisor','') == 'on'
        is_manager = request.POST.get('is_manager','') == 'on'
        is_reader = request.POST.get('is_reader','') == 'on'
        authorizedapprover = request.POST['authorizedapprover']
        if form.is_valid():
            user = SystemUsers()
            user.set_password(password2)
            user.username = username
            user.first_name = firstname
            user.mid_name = midname
            user.last_name = lastname
            user.mobilenum = mobilenum
            user.email = email
            user.is_admin = is_admin
            user.is_teller = is_teller
            user.is_supervisor = is_supervisor
            user.is_manager = is_manager
            user.is_reader = is_reader
            user.authorizedapprover = authorizedapprover
            user.save()
            messages.success(request, 'User created successfully')
        else:
            messages.error(request, 'User creation failed')
        return redirect('sysuser')
    context = {
        'form': form,
        'errors': form.errors,
        'user': request.user
    }
    return render(request, 'registration.html', context)

@login_required(login_url='login')
def ledger(request, id):
    template = ""
    LoginSession = request.user
    if LoginSession:
        if LoginSession.is_teller or LoginSession.is_supervisor:
            template = "ledger.html"
        else:
            template = redirect('bills_list')
            return template

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
                bill = asc_trans[i].bill
                try:
                    connectionType = ConsumerType.objects.get(contypeid=asc_trans[i].contypeid).contype
                except ObjectDoesNotExist:
                    connectionType = ''
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
                style = 'table-success'
                pb = asc_trans[i].processedBy
                bal = bal-asc_trans[i].payment
            elif asc_trans[i].transType == 'Penalty':
                usage = ''
                bill = asc_trans[i].bill
                pen = asc_trans[i].penaltyCode
                connectionType = ''
                prev = ''
                cur = ''
                style = 'table-danger'
                pb = asc_trans[i].processedBy
                bal += bill
            elif asc_trans[i].transType == 'Discount':
                usage = ''
                bill = ''
                connectionType = ''
                prev = ''
                cur = ''
                style = 'table-primary'
                pb = asc_trans[i].processedBy
                bal = bal-asc_trans[i].payment
            elif asc_trans[i].transType == 'Reset Meter':
                usage = ''
                bill = 0
                connectionType = ''
                prev = ''
                cur = asc_trans[i].meterReading
                style = 'table-warning'
                pb = asc_trans[i].processedBy
                bal += bill
            date = asc_trans[i].date
            payment = asc_trans[i].payment
            ornum = asc_trans[i].or_number
            transid = asc_trans[i].transactionid
            bal = math.ceil(bal*100)/100
            new_row = ledgerclass(transid, date, prev, cur, usage, bill, payment, pb, ornum, bal, connectionType, style)
            table.append(new_row)
            if i < len(asc_trans)-1:
                if asc_trans[i+1].transType == 'Payment' or asc_trans[i+1].transType == 'Discount':
                    p = cur
                else:
                    p = p + current
            prev = p

    context = {
        'month': calendar.month_name[datetime.today().month-1],
        'date_today': datetime.today(),
        'u': u,
        'table': table,
        'year': year,
        'usage': usage,
        'transid': transid,
        'contype': connectionType,
        'pre': pre,
        'cur': cur,
        'pen': pen,
        'bal': bal,
        'bill': bill,
        'user': request.user
    }
    return render(request, 'ledger.html', context)

@unauthenticated_user
def forgetpassword(request):
    if request.method == "POST":
        u_email = request.POST['email']
        if SystemUsers.objects.filter(email=u_email).exists():
            user = SystemUsers.objects.get(email=u_email)
            current_site = get_current_site(request)
            email_subject = "Confirm your Email"
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
    
            plaintext = template.loader.get_template('email_verif.txt')
            htmltemp = template.loader.get_template('email_verif.html')
            message = {
                'name': user.first_name,
                'domain': current_site.domain,
                'uid': uid,
                'token': token
            }
            print(f"http://{current_site.domain}/reset/{uid}/{token}")
            
            text_content = plaintext.render(message)
            html_content = htmltemp.render(message)
            try:
                msg = EmailMultiAlternatives(email_subject, text_content, 'Website <admin@example.com>', [user.email], headers = {'Reply-To': 'admin@example.com'})
                msg.attach_alternative(html_content, "text/html")
                msg.send()
            except BadHeaderError:
                return HttpResponse('Invalid header found.')
            messages.success(request, 'Please verify your account by clicking the link in your email: '+str(u_email))
            return redirect('login')
        else:
            messages.error(request, 'Are you sure that is your email?')
    return render(request, 'forgetpassword.html')

@unauthenticated_user
def resetpassword(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = SystemUsers.objects.get(username=uid)
        form = PasswordChangeForm(user)
    except (TypeError,ValueError,OverflowError,SystemUsers.DoesNotExist):
        user = None
    if request.method == 'POST':
        if user is not None and generate_token.check_token(user,token):
            pass1 = request.POST['password1']
            pass2 = request.POST['password2']
            if pass1 == pass2:
                user.first_name = pass1
                user.set_password(pass1)
                user.save()
                messages.success(request, 'Password reset successfully')
                return redirect('login')
            else:
                messages.error(request, 'Passwords do not match')
        else:
            messages.error(request, 'Password reset Failed')
            redirect('login')
     
    context = {
        'form': form,
        'uidb64':uidb64,
        'token':token,
    }
    return render(request, 'password_reset_form.html', context)

@login_required(login_url='login')
def meterreading_p(request, p):
    template = ""
    LoginSession = request.user
    if LoginSession:
        if LoginSession.is_teller or LoginSession.is_reader or LoginSession.is_supervisor:
            template = redirect('meterreading_p', p=10)
        else:
            template = redirect('bills_list')
            return template
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
    user = request.user

    search = request.GET.get("search", "")
    page = request.GET.get('page')
    isnum = search.isnumeric()
    if search:
        if isnum:
            meterred = ConsumerInfo.objects.filter(Q(meternumber=search) | Q(consumer_id=search), deleteflag=0, disconnectionflag=0).order_by('lastname', 'firstname', 'middlename')
        else:
            meterred = ConsumerInfo.objects.filter(Q(firstname__icontains=search) | Q(middlename__icontains=search) | Q(lastname__icontains=search), deleteflag=0, disconnectionflag=0).order_by('lastname', 'firstname', 'middlename')
    else:
        meterred = ConsumerInfo.objects.filter(deleteflag=0, disconnectionflag=0).order_by('lastname', 'firstname', 'middlename')   
    
    count = meterred.count()

    my = BarangayRecord.objects.all()
    for i in my:
        if i.year not in years:
            years.append(i.year)
    if datetime.today().year not in years:
        years.append(datetime.today().year)
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
        'search':search,
        'last':range(paginator.num_pages - 3, paginator.num_pages),
        'five':range(1,6),
        'paginate_by': paginate_by,
        'meterred': m,
        'user': user,
        'year': datetime.today().year,
        'months': months,
        'years': years
    }
    return render(request, 'meterreading.html', context)

@login_required(login_url='login')
def inputreading(request, id, year):
    template = ""
    LoginSession = request.user
    if LoginSession:
        if LoginSession.is_teller or LoginSession.is_reader or LoginSession.is_supervisor:
            template = "input-meter-reading.html"
        else:
            template = redirect('bills_list')
            return template

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
    consumer = ConsumerInfo.objects.get(consumer_id=id)
    lastid = Transactions.objects.latest('transactionid').transactionid
    alltrans = Transactions.objects.filter(acctID=consumer.consumer_id, transType='Billing') | Transactions.objects.filter(acctID=consumer.consumer_id, transType='Reset Meter')
    trans = alltrans.filter(year=year)
    lastreading = last_reading(id, year, 12)
    for i in alltrans:
        if i.date.year not in years:
            years.append(i.date.year)
    if int(year) in years:
        years.remove(int(year))
    if not trans:
        for i in range(1, 13):
            month = calendar.month_name[i]
            lastid+=1
            transid = lastid
            m = meterreaderclass(transid, month, '', lastreading, '', '', '')
            table.append(m)
    else:
        asc_trans = trans.order_by('month')
        count = len(asc_trans)
        j = 0
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
        readings = []
        try:
            con_b_rec = BarangayRecord.objects.get(barangaycode_id=consumer.installation_address_id, year=year)
        except ObjectDoesNotExist:
            con_b_rec = create_brec(consumer.installation_address_id, year)
            
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
                try:
                    t = Transactions.objects.get(acctID=consumer, transType='Billing', year=year, month=d)
                except ObjectDoesNotExist:
                    bill = 0
                    t = Transactions()
                    t.acctID = consumer
                    t.transType = 'Billing'
                    t.date = datetime.today()
                    t.month = d
                    if t.month == 0:
                        t.month = 12
                    t.year = year
                    t.meterReading = i
                    t.usage = i - lastreading
                    usage = t.usage
                    t.contypeid = consumer.contypeid_id
                    rate = ConsumerType.objects.get(contypeid=consumer.contypeid_id)
                    if t.usage <= rate.minReading:
                        t.bill = rate.minReadingCharge
                    else:
                        bill = ((t.usage - rate.minReading) * rate.rateAfterMin) + rate.minReadingCharge
                        t.bill = bill
                    t.payment = 0
                    t.processedBy = request.user
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
                        t.processedBy = request.user
                        t.save()
                else:
                    t = Transactions.objects.get(acctID=consumer.consumer_id, transType='Billing', year=year, month=d)
                    lastreading = last_reading(id, year, d)
                    print(lastreading)
                    try:
                        mo = d + 1
                        ye = year
                        if d == 12:
                            mo = 1
                            ye += 1
                        next = Transactions.objects.get(acctID=consumer.consumer_id, transType='Billing', year=ye, month=mo)
                        next.usage = next.meterReading - i
                        next.save()
                    except ObjectDoesNotExist:
                        print("asdf")
                    t.meterReading = i
                    t.date = datetime.today()
                    t.usage = i - lastreading
                    usage = t.usage
                    rate = ConsumerType.objects.get(contypeid=t.contypeid)
                    if t.usage <= rate.minReading:
                        t.bill = rate.minReadingCharge
                    else:
                        t.bill = ((t.usage - rate.minReading) * rate.rateAfterMin) + rate.minReadingCharge
                    t.processedBy = str(request.user)
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
                        t.processedBy = request.user
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
            bill = 0
            usage = 0
            con_b_rec.save()
            d += 1
        return redirect('inputreading', id=id , year=year)
    context = {
        'consumer': consumer,
        'table': table,
        'cur_year': year,
        'years': years,
        'user': request.user
    }
    return render(request, 'input-meter-reading.html', context)


@login_required(login_url='login')
def consumer_list(request):
    return redirect('consumer_list_p', p=10)


def consumer_list_p(request, p):
    template = ""
    LoginSession = request.user
    if LoginSession:
        if LoginSession.is_teller or LoginSession.is_supervisor:
            template = "conlist.html"
        else:
            template = redirect('bills_list')
            return template

    search = request.GET.get("search", "")
    page = request.GET.get('page')
    isnum = search.isnumeric()
    if search:
        if isnum:
            cons = ConsumerInfo.objects.filter(Q(meternumber=search) | Q(consumer_id=search), deleteflag=0).order_by('lastname', 'firstname', 'middlename')
        else:
            cons = ConsumerInfo.objects.filter(Q(firstname__icontains=search) | Q(middlename__icontains=search) | Q(lastname__icontains=search), deleteflag=0).order_by('lastname', 'firstname', 'middlename')
    else:
        cons = ConsumerInfo.objects.filter(deleteflag=0).order_by('lastname', 'firstname', 'middlename')   
    
    
    pages = int(p)
    user = request.user
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
        'search' :search,
        'last':range(paginator.num_pages - 3, paginator.num_pages),
        'five':range(1,6),
        'paginate_by': paginate_by,
        'consumer_list': cons_list,
        'user': user,
    }
    return render(request, 'conlist.html', context)

@login_required(login_url='login')
def consumercreation(request):
    template = ""
    LoginSession = request.user
    if LoginSession:
        if LoginSession.is_teller or LoginSession.is_supervisor:
            template = "consumercreation.html"
        else:
            template = redirect('bills_list')
            return template

    form = ConsumerForm()
    cons = ConsumerInfo.objects.all().order_by("-consumer_id")
    last = cons[0].consumer_id
    if request.method == "POST":
        isUpdate = request.POST['isUpdate']
        conid = request.POST['conid']
        form = ConsumerForm(request.POST)
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
        contypeid = request.POST['contypeid']
        penaltycode = request.POST['penaltycode']
        if form.is_valid():
            if isUpdate:
                c = ConsumerInfo.objects.get(consumer_id=conid)
            else:
                c = ConsumerInfo()
                c.status = 1
                c.stopmeterflag = 0
                c.deleteflag = 0
                c.penaltycounter = 0
                c.consumer_id = conid
            c.firstname = firstname
            c.middlename = middlename
            c.lastname = lastname
            c.mobilenum = mobilenum
            c.email = email
            c.birthdate = birthdate
            c.sex = sex
            c.penaltycode = Penalty.objects.get(penaltycode=penaltycode) 
            c.sitio = sitio
            c.homeaddress = homeaddress
            c.picture = picture
            c.meternumber = meternumber
            c.initialmeterreading = initialmeterreading
            c.installation_address = Barangays.objects.get(id=installation_address) 
            c.contypeid = ConsumerType.objects.get(contypeid=contypeid) 
            c.disconnectionflag = False
            c.save()
            return redirect('consumer_list')
    context = {
        'conid':last,
        'form': form,
        'errors': form.errors,
        'user': request.user
    }
    return render(request, 'consumercreation.html', context)

@login_required(login_url='login')
def consumerupdate(request, id):
    template = ""
    LoginSession = request.user
    if LoginSession:
        if LoginSession.is_teller or LoginSession.is_supervisor:
            template = "consumercreation.html"
        else:
            template = redirect('bills_list')
            return template

    con = ConsumerInfo.objects.get(consumer_id=id)
    form = ConsumerForm(instance=con)
    penaltyc = con.penaltycounter
    context = {
        'pc':penaltyc,
        'conid':id,
        'isUpdate':True,
        'form': form,
        'user': request.user
    }
    return render(request, 'consumercreation.html', context)

@login_required(login_url='login')
def stopmeter(request, id):
    template = ""
    LoginSession = request.user
    if LoginSession:
        if LoginSession.is_teller or LoginSession.is_reader or LoginSession.is_supervisor:
            template = redirect('inputreading', id=id, year=datetime.today().year)
        else:
            template = redirect('bills_list')
            return template


    if request.method == 'POST':
        consumer = ConsumerInfo.objects.get(consumer_id=id)
        consumer.stopmeterflag = not consumer.stopmeterflag
        consumer.save()
    return redirect('inputreading', id=id, year=datetime.today().year)

@login_required(login_url='login')
def enablemeter(request, id):

    template = ""
    LoginSession = request.user
    if LoginSession:
        if LoginSession.is_teller or LoginSession.is_reader or LoginSession.is_supervisor:
            template = redirect('inputreading', id=id, year=datetime.today().year)
        else:
            template = redirect('bills_list')
            return template

    if request.method == 'POST':
        is_new = request.POST.get('newmeter','off')=='on'
        consumer = ConsumerInfo.objects.get(consumer_id=id)
        consumer.stopmeterflag = not consumer.stopmeterflag
        if is_new:
            lasttranid = Transactions.objects.all().order_by('-transactionid')[0].transactionid
            meternum = int(request.POST.get('meternum'))
            consumer.meternumber = meternum
            initialreading = int(request.POST.get('initialreading'))
            tran = Transactions()
            tran.transactionid = lasttranid + 1
            tran.date = date.today()
            tran.acctID = consumer
            tran.transType = 'Reset Meter'
            print(initialreading)
            tran.meterReading = initialreading
            tran.usage = 0
            tran.bill = 0
            tran.month = date.today().month-1
            if tran.month == 12:
                tran.year = date.today().year-1
            else:
                tran.year = date.today().year
            tran.processedBy = str(request.user)
            tran.or_number = "N/A"
            tran.save()
        consumer.save()
    return redirect('inputreading', id=id, year=datetime.today().year)

@login_required(login_url='login')
def sysuser(request):
    template = ""
    LoginSession = request.user
    if LoginSession:
        if LoginSession.is_admin:
            template = "sysuser.html"
        else:
            template = redirect('bills_list')
            return template

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
        'user': request.user
    }
    return render(request, 'sysuser.html', context)


@login_required(login_url='login')
def user_edit(request, id):
    sys = SystemUsers.objects.get(username=id)
    form = sysup(instance=sys)
    if request.method == 'POST':
        username = request.POST['username']
        firstname = request.POST['first_name']
        midname = request.POST['mid_name']
        lastname = request.POST['last_name']
        mobilenum = request.POST['mobilenum']
        email = request.POST['email']
        profilepic = request.FILES.get('profilepic', None)
        is_teller = request.POST.get('is_teller','') == 'on'
        is_admin = request.POST.get('is_admin','') == 'on'
        is_supervisor = request.POST.get('is_supervisor','') == 'on'
        is_manager = request.POST.get('is_manager','') == 'on'
        is_reader = request.POST.get('is_reader','') == 'on'
        form = sysup(request.POST, instance=sys)
        if form.is_valid():
            sys.username = username
            sys.first_name = firstname
            sys.mid_name = midname
            sys.last_name = lastname
            sys.mobilenum = mobilenum
            sys.email = email
            sys.is_admin = is_admin
            sys.is_teller = is_teller
            sys.is_supervisor = is_supervisor
            sys.is_manager = is_manager
            sys.is_reader = is_reader
            if profilepic is not None:
                sys.profilepic = profilepic
            else:
                sys.profilepic = 'jazzy.jpg'
            sys.save()
        return redirect('sysuser')
    context = {
        'sys': sys,
        'form': form,
        'user': request.user
    }
    return render(request, 'user_edit.html', context)


def deleteUser(request, id):
    template = ""
    LoginSession = request.user
    if LoginSession:
        if LoginSession.is_admin:
            template = redirect('sysuser')
        else:
            template = redirect('bills_list')
            return template
    try:
        sys = SystemUsers.objects.get(username=id)
        sys.delete()
        messages.success(request, 'User has been deleted')
    except SystemUsers.DoesNotExist:
        messages.error(request, 'SystemUser does not exist')
    return redirect('sysuser')


def about(request):
    return render(request, 'about.html')

def payment(request, id):
    if request.method == 'POST':
        amount = int(request.POST['amount'])
        or_num = request.POST['or_num']
        dis_code = request.POST.get('dis_code')
        month = datetime.today().month
        consumer = ConsumerInfo.objects.get(consumer_id=id)
        con_bar = consumer.installation_address
        year = datetime.today().year
        try:
            con_b_rec = BarangayRecord.objects.get(barangaycode_id=con_bar, year=year)
        except ObjectDoesNotExist:
            con_b_rec = create_brec(consumer.installation_address_id, year)
        t = Transactions()
        t.acctID = consumer
        t.transType = "Payment"
        t.date = datetime.today()
        t.year = year
        t.month = month
        t.payment = amount
        t.processedBy = request.user
        t.or_number = or_num
        t.save()
        try:
            discount = Discount.objects.get(discountcode=dis_code)
        except ObjectDoesNotExist:
            print("")
        else:
            t = Transactions()
            t.acctID = consumer
            t.transType = "Discount"
            t.date = datetime.today()
            t.year = year
            t.month = month
            t.processedBy = request.user
            t.or_number = or_num
            t.payment = 0
            t.payment = amount-(amount*(discount.discount_rate/100))
            amount -= amount*(discount.discount_rate/100)
            t.save()
        get_balance(id)
        match month:
            case 1:
                con_b_rec.total_paid_jan += amount
            case 2:
                con_b_rec.total_paid_feb += amount
            case 3:
                con_b_rec.total_paid_mar += amount
            case 4:
                con_b_rec.total_paid_apr += amount
            case 5:
                con_b_rec.total_paid_may += amount
            case 6:
                con_b_rec.total_paid_jun += amount
            case 7:
                con_b_rec.total_paid_jul += amount
            case 8:
                con_b_rec.total_paid_aug += amount
            case 9:
                con_b_rec.total_paid_sept += amount
            case 10:
                con_b_rec.total_paid_oct += amount
            case 11:
                con_b_rec.total_paid_nov += amount
            case 12:
                con_b_rec.total_paid_dec += amount
        con_b_rec.save()
    return redirect('ledger', id=id)


def reports(request):
    cur_year =  datetime.today().year
    cur_month = datetime.today().month
    if cur_month == 1:
        cur_year-=1
    return redirect('barangayreport', cur_year)

@login_required(login_url='login')
def barangayreport(request, year):
    template = ""
    LoginSession = request.user
    if LoginSession:
        if LoginSession.is_teller or LoginSession.is_supervisor:
            template = "waterusage.html"
        else:
            template = redirect('bills_list')
            return template

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
        F('total_paid_oct') + F('total_paid_nov') + F('total_paid_dec'),
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
        F('total_paid_oct') + F('total_paid_nov') + F('total_paid_dec'),
        total_rec=F('total_due') - F('total_paid')
    ).aggregate(
        tu=Sum('total_usage'),
        tp=Sum('total_paid'),
        tr=Sum('total_due')
    )
    context = {
        'br': br,
        'cur_year': year,
        'years': years,
        'fr': fr,
        'user': request.user,
        'is_br':True
    }
    return render(request, 'waterusage.html', context)


def view_barangay(request, id):
    template = ""
    LoginSession = request.user
    if LoginSession:
        if LoginSession.is_teller or LoginSession.is_supervisor:
            template = "view_barangay.html"
        else:
            template = redirect('bills_list')
            return template

    bang = BarangayRecord.objects.get(barangayrec_id=id)

    context = {
        'bang': bang,
    }
    return render(request, 'view_barangay.html', context)

def usage_report_data(request, year):

    template = ""
    LoginSession = request.user
    if LoginSession:
        if LoginSession.is_teller or LoginSession.is_supervisor:
            template = "usage_report_data.html"
        else:
            template = redirect('bills_list')
            return template


    years = []
    months = [
        'jan',
        'feb',
        'mar',
        'apr',
        'may',
        'jun',
        'jul',
        'aug',
        'sept',
        'oct',
        'nov',
        'dec'
    ]
    bars = Barangays.objects.all()
    mybars = []
    mymonths = []
    my = BarangayRecord.objects.all()
    for i in my:
        if i.year not in years:
            years.append(i.year)
    if int(year) in years:
        years.remove(int(year))
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
    tu_bay = BarangayRecord.objects.filter(year=year,).annotate(
        sums=Sum(F('total_usage_jan') + F('total_usage_feb') + F('total_usage_mar') + F('total_usage_apr') + F('total_usage_may') + F('total_usage_jun') + F('total_usage_jul') + F('total_usage_aug') + F('total_usage_sept') + F('total_usage_oct') + F('total_usage_nov') + F('total_usage_dec'))).annotate(
        sum=Greatest(F('sums'), 0)
    )
    class br():
        def __init__(self, name, months):
            self.name = name
            self.months = months
    # bitch this is something long muhahaha
    # but now dis is samting short MUHAHAHAHAHA!!!!
    for b in bars:
        try:
            brec = BarangayRecord.objects.get(barangayrec_id=f"{b.id}-{year}")
        except ObjectDoesNotExist:
            brec = None
        for m in months:
            try:
                mymonths.append(brec.__dict__[f"total_usage_{m}"])
            except AttributeError:
                pass
        n = br(b.barangay, mymonths)
        mymonths = []
        mybars.append(n)
    
    context = {
        'mybars':mybars,
        'tu_mon': tu_mon,
        'tu_bay': tu_bay,
        'cur_year': year,
        'years': years,
        'my': my,
        'user': request.user,
        'is_ur':True,
    }
    return render(request, 'usage_report_data.html', context)


def revenue_report(request, year):
    template = ""
    LoginSession = request.user
    if LoginSession:
        if LoginSession.is_teller or LoginSession.is_supervisor:
            template = "revenue_report.html"
        else:
            template = redirect('bills_list')
            return template

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
        'rec': rec,
        'is_rr':True,
    }
    return render(request, 'revenue_report.html',  context)


def deleteconsumer(request, id):
    template = ""
    LoginSession = request.user 
    if LoginSession:
        if LoginSession.is_teller or LoginSession.is_supervisor:
            template = "consumercreation.html"
        else:
            template = redirect('bills_list')
            return template

    con = ConsumerInfo.objects.get(consumer_id=id)
    con.deleted_flag = True
    con.save()
    return redirect('consumer_list')
def disconnectconsumer(request, id):
    template = ""
    LoginSession = request.user
    if LoginSession:
        if LoginSession.is_teller or LoginSession.is_supervisor:
            template = "consumercreation.html"
        else:
            template = redirect('bills_list')
            return template

    con = ConsumerInfo.objects.get(consumer_id=id)
    con.disconnectionflag = True
    con.save()
    return redirect('consumer_list')

def reconnectconsumer(request, id):
    template = ""
    LoginSession = request.user
    if LoginSession:
        if LoginSession.is_teller or LoginSession.is_supervisor:
            template = "consumercreation.html"
        else:
            template = redirect('bills_list')
            return template

    con = ConsumerInfo.objects.get(consumer_id=id)
    con.disconnectionflag = False
    con.save()
    return redirect('consumer_list')


def unsettled_bills(request):

    template = ""
    LoginSession = request.user
    if LoginSession:
        if LoginSession.is_teller or LoginSession.is_supervisor:
            template = redirect('unsettled_bills_p', p=10)
        else:
            template = redirect('bills_list')
            return template

    return redirect('unsettled_bills_p', p=10)


def unsettled_bills_p(request, p):
    template = ""
    LoginSession = request.user
    if LoginSession:
        if LoginSession.is_teller or LoginSession.is_supervisor:
            template = "unsettled_bill.html"
        else:
            template = redirect('bills_list')
            return template

    class ub_year:
        def __init__(self, y, u):
            self.y = y
            self.u = u
    search = request.GET.get("search", "")
    page = request.GET.get('page')
    tb = ConsumerInfo.objects.filter(current_bal__gt=0).aggregate(tots = Sum('current_bal'))
    isnum = search.isnumeric()
    if search:
        if isnum:
            ubs = ConsumerInfo.objects.filter(Q(meternumber=search) | Q(consumer_id=search), current_bal__gt = 0).order_by('lastname', 'firstname', 'middlename')
        else:
            ubs = ConsumerInfo.objects.filter(Q(firstname__icontains=search) | Q(middlename__icontains=search) | Q(lastname__icontains=search), current_bal__gt = 0).order_by('lastname', 'firstname', 'middlename')
    else:
        ubs = ConsumerInfo.objects.filter(current_bal__gt=0).order_by('lastname', 'firstname', 'middlename')
    pages = int(p)
    table = []
    count = len(ubs)
    if pages == 0:
        paginate_by = request.GET.get('paginate_by', count)
    else:
        paginate_by = request.GET.get('paginate_by', pages)
    page = request.GET.get('page')

    paginator = Paginator (ubs,paginate_by)
    try:
        ub = paginator.page(page)
    except PageNotAnInteger:
        ub = paginator.page(1)
    except EmptyPage:
        ub = paginator.page(paginator.num_pages)
    for j in ub:
        alltran = Transactions.objects.filter(acctID_id=j.consumer_id, transType='Billing').order_by('-year')
        if not alltran:
            print("")
        else:
            if alltran[0].year is not None:
                a = alltran[0].year
            else:
                a = 0
        yeah = ub_year(a,j)
        table.append(yeah)    
    context = {
        'search': search,
        'ub': ub,
        'table':table,
        'paginate_by': paginate_by,
        'last': range(paginator.num_pages-3, paginator.num_pages),
        'five': range(1, 6),
        'tb': tb,
        'user': request.user,
    }
    return render(request, 'unsettled_bill.html', context)


def view_unsettled_bills(request, id, year):
    template = ""
    LoginSession = request.user
    if LoginSession:
        if LoginSession.is_teller or LoginSession.is_supervisor:
            template = "view_unsettled_bills.html"
        else:
            template = redirect('bills_list')
            return template

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
    billing = Transactions.objects.filter(
        acctID_id=id, transType='Billing', year=year)
    payment = Transactions.objects.filter(
        acctID_id=id, transType='Payment', year=year)
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
                a = view_utang(month, reading, reading_date, usage,total_bill, total_amount_paid)
                table.append(a)
    context = {
        'uv': uv,
        'years': years,
        'current': year,
        'table': table, 
    }
    return render(request, 'view_unsettled_bills.html', context)


def discount(request):
    d = Discount.objects.all()
    form = addDiscount()
    discountidcount = len(Discount.objects.all())
    user = request.user
    if request.method == "POST":
        form = addDiscount(request.POST)
        discount_rate = request.POST['discount_rate']
        if form.is_valid():
            addD = Discount()
            addD.discountcode = "D00"+str(discountidcount+1)
            addD.discount_rate = discount_rate
            addD.added_by = user
            addD.save()
    context = {
        'd': d,
        'form': form,
        'errors': form.errors,
        'user': user,
        'is_discount':True,
    }
    return render(request, 'discount.html', context)


@login_required(login_url='login')
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
            ct.added_by = request.user
            ct.save()
    context = {
        'c': c,
        'form': form,
        'errors': form.errors,
        'user': request.user,
        'is_contype':True,
    }
    return render(request, 'new_consumertype.html', context)


@login_required(login_url='login')
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
            pen.added_by = request.user
            pen.save()
        else:
            print("way ayo")
    context = {
        'p': p,
        'form': form,
        'errors': form.errors,
        'user': request.user,
        'is_penalty':True,
    }

    return render(request, 'penalty.html', context)


def bulkreading(request, year, month, p):
    template = ""
    LoginSession = request.user
    if LoginSession:
        if LoginSession.is_teller or LoginSession.is_reader:
            pass
        else:
            template = redirect('bills_list')
            return template
    months = []
    years = []
    class monthname():
        def __init__(self, name, num):
            self.name = name
            self.num = num
    for i in range(1, 13):
        m = calendar.month_name[i]
        months.append(monthname(m, i))
    consumers_list = []
    my = BarangayRecord.objects.all()
    for i in my:
        if i.year not in years:
            years.append(i.year)
    if datetime.today().year not in years:
        years.append(datetime.today().year)
    if years[0] < years[len(years)-1]:
        years.reverse()
    class new_con():
        def __init__(self, con, prev, cur):
            self.con = con
            self.prev = prev
            self.cur = cur
    mname = calendar.month_name[month]
    search = request.GET.get("search", "")
    page = request.GET.get('page')
    isnum = search.isnumeric()
    if search:
        if isnum:
            consumers = ConsumerInfo.objects.filter(Q(meternumber=search) | Q(consumer_id=search),stopmeterflag=0, deleteflag=0, disconnectionflag=0).order_by('lastname', 'firstname', 'middlename')
        else:
            consumers = ConsumerInfo.objects.filter(Q(firstname__icontains=search) | Q(middlename__icontains=search) | Q(lastname__icontains=search),stopmeterflag=0, deleteflag=0, disconnectionflag=0).order_by('lastname', 'firstname', 'middlename')
    else:
        consumers = ConsumerInfo.objects.filter(stopmeterflag=0, deleteflag=0, disconnectionflag=0).order_by('lastname', 'firstname', 'middlename')
    
    pages = int(p)
    count = len(consumers)
    if pages == 0:
        paginate_by = request.GET.get('paginate_by', count)
    else:
        paginate_by = request.GET.get('paginate_by', pages)
    page = request.GET.get('page')

    paginator = Paginator (consumers,paginate_by)
    try:
        ub = paginator.page(page)
    except PageNotAnInteger:
        ub = paginator.page(1)
    except EmptyPage:
        ub = paginator.page(paginator.num_pages)

    for i in ub:
        try:
            tran = Transactions.objects.get(
                acctID_id=i.consumer_id, month=month, year=year, transType="Billing")
            cur = tran.meterReading
        except ObjectDoesNotExist:
            cur = 0
        try:
            if month == 1:
                tran = Transactions.objects.get(
                    acctID_id=i.consumer_id, month=12, year=year-1, transType="Billing")
            else:
                tran = Transactions.objects.get(
                    acctID_id=i.consumer_id, month=month-1, year=year, transType="Billing")
            prev = tran.meterReading
        except ObjectDoesNotExist:
            prev = 0
        # prev = last_reading(i.consumer_id, year, month)
        consumers_list.append(new_con(i, prev, cur))
    
    if request.method == "POST":
        cons = ub
        interest = 0
        for c in cons:
            a = request.POST.get(f"con{c.consumer_id}", None)
            if a is not None:
                try:
                    con_b_rec = BarangayRecord.objects.get(barangaycode_id=c.installation_address_id, year=year)
                except ObjectDoesNotExist:
                    con_b_rec = create_brec(c.installation_address_id, year)
                bill = 0
                usage = 0
                a = int(a)
                try:
                    tran = Transactions.objects.get(acctID_id=c.consumer_id,month=month,year=year,transType = "Billing")
                    tran.meterReading = a
                    tran.save()
                except ObjectDoesNotExist:
                    t = Transactions()
                    try:
                        if month == 1:
                            tran = Transactions.objects.get(acctID_id=c.consumer_id,month=12,year=year-1,transType = "Billing")
                        else:    
                            tran = Transactions.objects.get(acctID_id=c.consumer_id,month=month-1,year=year,transType = "Billing")
                        prev = tran.meterReading
                    except ObjectDoesNotExist:
                        prev = 0
                    cummulative = get_cummulative(c.consumer_id)
                    con_penalty = Penalty.objects.get(penaltycode=c.penaltycode)
                    if c.penaltycounter >= con_penalty.penalty_after and con_penalty.penalty_rate != 0:
                        xy = con_penalty.penalty_rate * cummulative
                        interest = xy/100
                    t.acctID = c
                    t.transType = 'Billing'
                    t.date = datetime.today()
                    t.month = month
                    t.year = year
                    t.meterReading = a
                    t.usage = a - prev
                    usage = a - prev
                    t.contypeid = c.contypeid_id
                    rate = ConsumerType.objects.get(contypeid=c.contypeid_id)
                    if t.usage <= rate.minReading:
                        t.bill = rate.minReadingCharge
                    else:
                        bill = ((t.usage - rate.minReading) * rate.rateAfterMin) + rate.minReadingCharge
                        t.bill = bill
                    t.payment = 0
                    t.processedBy = request.user
                    t.save()
                    if interest:
                        t = Transactions()
                        t.acctID = c
                        t.transType = 'Penalty'
                        t.date = datetime.today()
                        t.month = month
                        t.year = year
                        t.bill = interest
                        bill += interest
                        t.payment = 0
                        t.processedBy = request.user
                        t.save()
                    if c.discountcode is not None:
                        discount = c.discountcode
                        t = Transactions()
                        t.acctID = c
                        t.transType = 'Discount'
                        t.date = datetime.today()
                        t.month = month
                        t.year = year
                        t.bill = 0
                        t.payment = bill-(bill*(discount.discount_rate/100))
                        bill -= bill*(discount.discount_rate/100)
                        t.processedBy = request.user
                        t.save()
                match month:
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
            get_balance(c.consumer_id)
    context = {
        'search':search,
        'year':year,
        'month':mname,
        'years':years,
        'months':months,
        'monthval':month,
        'consumers_list':consumers_list,
        'ub':ub,
        'paginate_by': paginate_by,
        'last' : range(paginator.num_pages-3, paginator.num_pages),
        'five' : range(1,6),
        'user':request.user
    }
    return render(request,'bulkreading.html', context)

@login_required(login_url='login')
def viewprof(request):
    user = SystemUsers.objects.get(username=str(request.user))
    role = ""
    if user.is_admin:
        role = role + "Admin "
    if user.is_teller:
        role = role + "Teller "
    if user.is_supervisor:
        role = role + "Supervisor "
    if user.is_manager:
        role = role + "Manager "
    if user.is_reader:
        role = role + "Reader "
    context= {
        'user':user,
        'role':role,
        'is_profile':True
    }
    return render(request, 'viewprof.html', context)

@login_required(login_url='login')
def userprof(request):
    user = SystemUsers.objects.get(username=str(request.user))
    form = ProfileForm(instance=user)
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=user)
        profilepic = request.FILES.get('profilepic', False)
        print(profilepic)
        if form.is_valid():
            if profilepic:
                user.profilepic = profilepic
            else:
                user.profilepic = user.profilepic
            user.save()
            messages.success(
                    request, 'Your Profile Updated Successfully')
            return redirect('settings')
    print(user.username)
    context= {
        'user':user,
        'form':form
    }
    return render(request, 'userprof.html', context)
