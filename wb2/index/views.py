

import calendar
import math
from django.core.exceptions import *
import datetime
from .dataporter import *
from .decorators import *
from .forms import *
from .functions import * 
from .models import *
from .tokens import generate_token
from datetime import datetime, timedelta
from django import template
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import EmailMultiAlternatives, BadHeaderError
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.db.models import F, Sum, Q
from django.shortcuts import render, redirect
from django.utils import timezone
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.http import JsonResponse



is_seen_issues = Issues.objects.filter(is_seen=False)


def porter(request):
    porter_in()
    porter_out(sorted_tables)
    print("balance")
    balance()
    print("cummulative")
    cons = ConsumerInfo.objects.all()
    for i in cons:
        i.cummulative = get_cummulative(i.consumer_id)
        i.save()
    
    # for i in sorted_tables[6]:
    #     passAscii = base64.b64decode(i[1])
    #     p = passAscii.decode("ascii")
    #     print(f'username: {i[0]} | password: {p}')
    return redirect("login")


@unauthenticated_user
def lp(request):
    # !!!please ask previous developers before attempting to uncomment!!!
    # portfromcsv()
    sxz()
    enye_cons()
    enye_bars()
    camelize()
    set_first_tran()
    set_months_unpaid()
    if datetime.now().day == 1:
        set_overdue_months()
    # capitalize()
    return render(request, "landing.html")

@unauthenticated_user
def signin(request):
    if request.method == "POST":
        dump_database()
        u = request.POST['username']
        password = request.POST['password']
        auth = authenticate(username=u, password=password)
        if auth is not None:
            user = SystemUsers.objects.get(username=u)
            login_rec = LoginRec()
            request.user = user.username
            request.session["auth"] = True
            request.session.modified = True
            login_rec.username = user.username
            login_rec.token = gen_token()
            login_rec.last_access = timezone.now()
            login_rec.expiration = login_rec.last_access + timedelta(minutes=5)
            login_rec.save()
            login(request, auth)
            messages.success(request, "Logged In as " + user.username)
            return redirect('bills_list')
        else:
            messages.error(request, "Invalid Username or Password")
    return render(request, 'login.html')



@login_required(login_url='login')
def bills_list(request):
    global notif_viewers
    # balance()
    # get_consumers_yearly()
    # billing_errors_to_csv()
    # fix_billing_errors()
    # adjust_excess_only()
    template = ""
    LoginSession = request.user
    if LoginSession:
        if LoginSession.is_teller or LoginSession.is_supervisor:
            template = redirect('bills_list')
        else:
            if LoginSession.is_admin:
                template = redirect('sysuser')
            else:
                if LoginSession.is_reader:
                    template = redirect('meterreading')
            return template
    sidebar = request.GET.get("sidebar")
    if sidebar == 'False':
        hipos = True
    else:
        hipos = False
    search = request.GET.get("search", "")
    page = request.GET.get('page')
    isnum = search.isnumeric()
    if search:
        if isnum:
            bills = ConsumerInfo.objects.filter(Q(meternumber=search) | Q(consumer_id__icontains=search),deleteflag=0).order_by('lastname', 'firstname', 'middlename')
        else:
            bills = ConsumerInfo.objects.filter(Q(firstname__icontains=search) | Q(middlename__icontains=search) | Q(lastname__icontains=search)| Q(homeaddress__icontains=search),deleteflag=0).order_by('lastname', 'firstname', 'middlename')
    else:
        bills = ConsumerInfo.objects.filter(deleteflag=0).order_by('lastname', 'firstname', 'middlename')
    pages = int(request.GET.get('p', 10))
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
        'count':count,
        'bills_list': bills_list,
        'user': user,
        'hipos':hipos,
        'is_seen_issues': is_seen_issues,
        'notif_viewers': notif_viewers,
    }
    return render(request, 'billslist.html', context)


@login_required(login_url='login')
def signout(request):
    global notif_viewers
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
    global notif_viewers
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
        # authorizedapprover = request.POST['authorizedapprover']
        for i in form.fields:
            try:
                form.fields[i].widget.attrs['class'] += ' is-valid'
            except KeyError:
                pass
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
            # user.authorizedapprover = authorizedapprover
            user.save()
            messages.success(request, 'User created successfully')
            return redirect('sysuser')
        else:
            for i in form.errors.as_data():
                item = form.fields[i]
                item.widget.attrs['class'] += ' is-invalid'
            messages.error(request, 'User creation failed')
    context = {
        'form': form,
        'user': request.user,
        'is_seen_issues':is_seen_issues
    }
    return render(request, 'registration.html', context)

@login_required(login_url='login')
def ledger(request, id):
    global notif_viewers
    disp = request.GET.get('show','')
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
    monthnames = ['January','February','March','April','May','June','July','August','September','October','November','December']
    # get_balance(id)
    class ledgerclass():
        def __init__(self, transid, date, prev, reading, usage, bill, payment, pb, ornum, bal, rateid, style, disc_code, transtype, month, year, ispaid):
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
            self.disc_code = disc_code
            self.transtype = transtype
            self.month = month
            self.year = year
            self.ispaid = ispaid

        def id(self):
            return self.transid
    try:
        u = ConsumerInfo.objects.get(pk=id)
        if disp == '':
            trans = Transactions.objects.filter(acctID=u.consumer_id, is_issue=False)
        else:
            trans = Transactions.objects.filter(acctID=u.consumer_id, transType = disp, is_issue=False)
        asc_trans = trans.order_by('year', 'month','transType')
        bal = 0
        for i in range(len(asc_trans)):
            prev = 0
            ornum = ''
            connectionType = ''
            style = ''
            pb = ''
            dcode = ''
            usage = ''
            bill = ''
            prev = ''
            cur = ''
            ispaid = ''

            if asc_trans[i].transType == 'Billing':
                usage = asc_trans[i].usage
                pre = asc_trans[i].meterReading - usage
                bill = asc_trans[i].bill
                try:
                    connectionType = ConsumerType.objects.get(contypeid=asc_trans[i].contypeid).contype
                except ObjectDoesNotExist:
                    pass
                cur = asc_trans[i].meterReading
                prev = asc_trans[i].prevReading
                if asc_trans[i].processedBy is not None:
                    pb = asc_trans[i].processedBy
                bal += bill
                if asc_trans[i].is_billpaid:
                    ispaid = 'yeah'
            elif asc_trans[i].transType == 'Payment':
                style = 'table-success'
                ornum = asc_trans[i].or_number
                pb = ''
                bal = bal-asc_trans[i].payment
                try:
                    discount = Transactions.objects.get(transactionid=asc_trans[i].discountcode)
                    dcode = discount.discountcode
                except ObjectDoesNotExist:
                    pass
            elif asc_trans[i].transType == 'Penalty':
                bill = asc_trans[i].bill
                pen = asc_trans[i].penaltyCode
                style = 'table-danger'
                pb = asc_trans[i].processedBy
                bal += bill

            elif asc_trans[i].transType == 'Discount':
                style = 'table-primary'
                pb = asc_trans[i].processedBy
                bal = bal-asc_trans[i].payment

            elif asc_trans[i].transType == 'Reset Meter':
                bill = 0
                cur = asc_trans[i].meterReading
                style = 'table-warning'
                pb = asc_trans[i].processedBy
                bal += bill
            elif asc_trans[i].transType == 'Additional Fees':
                bill = asc_trans[i].bill
                style = 'table-info'
                bal += bill
                
                if asc_trans[i].processedBy is not None:
                    pb = asc_trans[i].processedBy
                if asc_trans[i].is_billpaid:
                    ispaid = 'yeah'
            date = asc_trans[i].date
            payment = asc_trans[i].payment
            transid = asc_trans[i].transactionid
            m = asc_trans[i].month
            y = asc_trans[i].year
            bal = math.ceil(bal*100)/100
            ttype = asc_trans[i].transType
            if asc_trans[i].transType != 'Received Amount':
                new_row = ledgerclass(transid, date, prev, cur, usage, bill, payment, pb, ornum, bal, connectionType, style,dcode, ttype, monthnames[m-1], y, ispaid)
                table.append(new_row)
        # if bal > 0:
        #     ispaid = False
        # else:
        #     ispaid = True
        ispaid = False
    except ObjectDoesNotExist:
        u = False
    context = {
        'disp':disp,
        'month': calendar.month_name[datetime.today().month-1],
        'date_today': datetime.today().strftime('%B %d, %Y - %I:%M %p'),
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
        'user': request.user,
        'prevmonth' : calendar.month_name[(datetime.today().month - 2) % 12 + 1],
        'ispaid':ispaid,
        'is_seen_issues': is_seen_issues,
        'notif_viewers': notif_viewers,
    }
    return render(request, 'ledger.html', context)

@unauthenticated_user
def forgetpassword(request):
    global notif_viewers
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

def undodelete(request):
    if request.method == 'POST':
        id = request.POST['id']
        con = ConsumerInfo.objects.get(consumer_id=id)
        con.deleteflag = False
        con.save()
    return redirect(request.META.get('HTTP_REFERER', '/'))

@login_required(login_url='login')
def meterreading(request):
    global notif_viewers
    template = ""
    LoginSession = request.user
    if LoginSession:
        if LoginSession.is_teller or LoginSession.is_reader or LoginSession.is_supervisor:
            template = redirect('meterreading')
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

    pages = int(request.GET.get('p', 10))

    user = request.user

    search = request.GET.get("search", "")
    page = request.GET.get('page')
    isnum = search.isnumeric()
    if search:
        if isnum:
            meterred = ConsumerInfo.objects.filter(Q(meternumber=search) | Q(consumer_id__icontains=search), deleteflag=0, disconnectionflag=0).order_by('lastname', 'firstname', 'middlename')
        else:
            meterred = ConsumerInfo.objects.filter(Q(firstname__icontains=search) | Q(middlename__icontains=search) | Q(lastname__icontains=search)| Q(homeaddress__icontains=search), deleteflag=0, disconnectionflag=0).order_by('lastname', 'firstname', 'middlename')
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
        'count':count,
        'year': datetime.today().year,
        'months': months,
        'years': years,
        'is_seen_issues': is_seen_issues,
        'notif_viewers': notif_viewers,
    }
    return render(request, 'meterreading.html', context)

@login_required(login_url='login')
def deletereading(request, id):
    reading = Transactions.objects.get(transactionid = id)
    con = reading.acctID
    con.current_bal -= reading.bill
    if con.current_bal < 0:
        con.excess += (con.current_bal*1)
        con.current_bal = 0
    try:
        payment = Transactions.objects.get(acctID_id=con.consumer_id, month=reading.month, year=reading.year, transType="Payment")
        con.current_bal += payment.payment
        payment.delete()
    except ObjectDoesNotExist:
        pass
    con.save()
    reading.delete()
    return redirect('inputreading', con.consumer_id, date.today().year)

@login_required(login_url='login')
def inputreading(request, id, year):
    global notif_viewers
    table = []
    years = []
    class meterreaderclass():
        def __init__(self, transid, month, monthval, usage, prev, reading, next, style):
            self.transid = transid
            self.month = month
            self.usage = usage
            self.prev = prev
            self.reading = reading
            self.next = next
            self.style = style
            self.monthval = monthval
    consumer = ConsumerInfo.objects.get(consumer_id=id)
    yt = Transactions.objects.filter(acctID=consumer.consumer_id, is_issue=False).values_list('year', flat=True)
    years_backward = []
    for i in yt:
        if i not in years_backward and i <= year:
            years_backward.append(i)
    years_backward.sort(reverse=True)
    years_forward = []
    for i in yt:
        if i not in years_forward and i >= year:
            years_forward.append(i)
    years_forward.sort()
    lastreading = consumer.current_reading
    lastid = Transactions.objects.latest('transactionid').transactionid
    alltrans = Transactions.objects.filter(acctID=consumer.consumer_id, transType='Billing', is_issue=False) | Transactions.objects.filter(acctID=consumer.consumer_id, transType='Reset Meter', is_issue=False)
    trans = alltrans.filter(year=year)
    brec = BarangayRecord.objects.all().order_by('-year')
    for i in brec:
        if i.year not in years:
            years.append(i.year)
    if datetime.today().year not in years:
        years.append(datetime.today().year)
    if not trans:
        for i in range(1, 13):
            month = calendar.month_name[i]
            lastid+=1
            transid = lastid
            m = meterreaderclass(transid, month, i, '', lastreading, '', '', '')
            table.append(m)
    else:
        asc_trans = trans.order_by('month')
        count = len(asc_trans)
        j = 0
        for i in range(1, 13):
            month = calendar.month_name[i]
            lastid +=1
            transid = lastid
            usage = 0
            prev = lastreading
            reading = 0
            style = ''
            try:
                next = asc_trans[j].meterReading
            except IndexError:
                next = False
            if j < count and count != 0:
                if i == asc_trans[j].month:
                    if asc_trans[j].transType == "Billing":
                        transid = asc_trans[j].transactionid
                        usage = asc_trans[j].usage
                        reading = asc_trans[j].meterReading
                        prev = asc_trans[j].prevReading
                        try:
                            next = asc_trans[j+1].meterReading
                        except IndexError:
                            next = False
                        lastreading = reading
                        style = 'table-success'
                    else:
                        prev = 0
                        try:
                            transid = asc_trans[j+1].transactionid
                            usage = asc_trans[j+1].usage
                            reading = asc_trans[j+1].meterReading
                            try:
                                next = asc_trans[j+2].meterReading
                            except IndexError:
                                next = False
                            lastreading = reading
                            style = 'table-success'
                            j+=1
                        except IndexError:
                            pass
                    j += 1

            m = meterreaderclass(transid, month, i, usage, prev, reading, next, style)
            table.append(m)
            
    if consumer.penaltycode is None:
        con_penalty = Penalty.objects.get(penaltycode='P001')
    else:
        con_penalty = Penalty.objects.get(penaltycode=consumer.penaltycode)
    cummulative = get_cummulative(id)
    interest = 0
    usage = 0
    if request.method == "POST":
        try:
            con_b_rec = BarangayRecord.objects.get(barangaycode_id=consumer.installation_address_id, year=year)
        except ObjectDoesNotExist:
            con_b_rec = create_brec(consumer.installation_address_id, year)
            
        for i in range(12):
            if request.POST.get('reading-'+calendar.month_name[i+1]):
                d = i+1
                r = int(request.POST.get('reading-'+calendar.month_name[i+1]))
                break
        bill = 0
        if consumer.excep_accnt:
            try:
                tran = Transactions.objects.get(acctID=consumer.consumer_id, transType='Billing', year=year, month=d)
                mm = d+1
                has_next = False
                for y in years_forward:
                    for x in range(mm, 13):
                        try:
                            next = Transactions.objects.get(acctID=consumer.consumer_id, transType='Billing', year=y, month=x)
                            next.prevReading = r
                            next.usage = next.meterReading - r
                            next.save()
                            has_next = True
                            break
                        except ObjectDoesNotExist:
                            pass
                    if has_next:
                        break
                    mm = 1
                if has_next:
                    mm = d-1
                    has_prev = False
                    for y in years_backward:
                        for x in range(mm, 0, -1):
                            try:
                                prev = Transactions.objects.get(acctID=consumer.consumer_id, transType='Billing', year=y, month=x)
                                last_reading = prev.meterReading
                                has_prev = True
                                break
                            except ObjectDoesNotExist:
                                pass
                        if has_prev:
                            break
                        mm = 12
                tran.usage = r - last_reading
                tran.meterReading = r
                tran.bill = 0
                tran.processedBy = request.user
                tran.save()
                
            except:
                usage = r - consumer.current_reading
                tran = Transactions()
                tran.transType = 'Billing'
                tran.meterReading = r
                tran.usage = usage
                tran.bill = 0
                tran.processedBy = request.user
                tran.year = year
                tran.month = d
                tran.contypeid = consumer.contypeid_id
                tran.acctID = consumer
                consumer.current_reading = r 
                tran.save()
                consumer.save()
        else:
            if consumer.penaltycounter >= con_penalty.penalty_after and con_penalty.penalty_rate != 0:
                xy = con_penalty.penalty_rate * cummulative
                interest = xy/100
            
            try:
                billtran = Transactions.objects.get(acctID=consumer.consumer_id, transType='Billing', year=year, month=d)
                last_reading = billtran.prevReading

                # finding next billing
                mm = d+1
                has_next = False
                for y in years_forward:
                    for x in range(mm, 13):
                        try:
                            next = Transactions.objects.get(acctID=consumer.consumer_id, transType='Billing', year=y, month=x)
                            next.prevReading = r
                            next.usage = next.meterReading - r
                            next.save()
                            has_next = True
                            break
                        except ObjectDoesNotExist:
                            pass
                    if has_next:
                        break
                    mm = 1
                
                # finding previous billing
                if has_next:
                    mm = d-1
                    has_prev = False
                    for y in years_backward:
                        for x in range(mm, 0, -1):
                            try:
                                prev = Transactions.objects.get(acctID=consumer.consumer_id, transType='Billing', year=y, month=x)
                                last_reading = prev.meterReading
                                has_prev = True
                                # if not prev.is_billpaid:
                                #     prev.months_not_paid += 1
                                #     prev.save()
                                break
                            except ObjectDoesNotExist:
                                pass
                        if has_prev:
                            break
                        mm = 12
                billtran.meterReading = r
                billtran.date = datetime.today()
                billtran.prevReading = last_reading
                billtran.usage = r - last_reading
                usage = billtran.usage
                rate = ConsumerType.objects.get(contypeid=billtran.contypeid)
                dif = billtran.bill
                if billtran.usage <= rate.minReading or billtran.usage < 0:
                    billtran.bill = rate.minReadingCharge
                else:
                    billtran.bill = ((billtran.usage - rate.minReading) * rate.rateAfterMin) + rate.minReadingCharge
                billtran.processedBy = str(request.user)
                billtran.save()
                dif = billtran.bill - dif
                if interest:
                    p = Transactions()
                    p.acctID = consumer
                    p.transType = 'Penalty'
                    p.date = datetime.today()
                    p.month = d
                    p.year = year
                    p.bill = interest
                    p.payment = 0
                    p.processedBy = request.user
                    p.save()
                try:
                    paymentT = Transactions.objects.get(acctID_id=consumer.consumer_id, transType='Payment', year=year, month=d)
                    if dif:
                        paymentT.payment = paymentT.payment + dif
                        consumer.excess = consumer.excess - dif
                        consumer.current_bal = consumer.current_bal - dif
                    paymentT.save()
                    consumer.save()
                except ObjectDoesNotExist:
                    pass
            except ObjectDoesNotExist:
                
                # finding next billing
                fm = d+1
                has_next = False
                for y in years_forward:
                    for x in range(fm, 13):
                        try:
                            next = Transactions.objects.get(acctID=consumer.consumer_id, transType='Billing', year=y, month=x)
                            
                            # finding previous billing
                            bm = d-1
                            has_prev = False
                            for y in years_backward:
                                for x in range(bm, 0, -1):
                                    try:
                                        prev = Transactions.objects.get(acctID=consumer.consumer_id, transType='Billing', year=y, month=x)
                                        last_reading = prev.meterReading
                                        # if not prev.is_billpaid:
                                        #     prev.months_not_paid += 1
                                        #     prev.save()
                                        break
                                    except ObjectDoesNotExist:
                                        pass
                                if has_prev:
                                    break
                                bm = 12
                            break
                        except ObjectDoesNotExist:
                            pass
                    if has_next:
                        break
                    fm = 1
                
                bill = 0
                billtran = Transactions()
                billtran.acctID = consumer
                billtran.transType = 'Billing'
                billtran.date = datetime.today()
                billtran.month = d
                if billtran.month == 0:
                    billtran.month = 12
                billtran.year = year
                billtran.meterReading = r
                billtran.prevReading = lastreading
                billtran.usage = r - lastreading
                usage = billtran.usage
                billtran.contypeid = consumer.contypeid_id
                rate = ConsumerType.objects.get(contypeid=consumer.contypeid_id)
                if billtran.usage <= rate.minReading:
                    billtran.bill = rate.minReadingCharge
                else:
                    bill = ((billtran.usage - rate.minReading) * rate.rateAfterMin) + rate.minReadingCharge
                    billtran.bill = bill
                billtran.payment = 0
                billtran.processedBy = request.user
                billtran.save()
                if interest:
                    p = Transactions()
                    p.acctID = consumer
                    p.transType = 'Penalty'
                    p.date = datetime.today()
                    p.month = d
                    p.year = year
                    p.bill = interest
                    bill += interest
                    p.payment = 0
                    p.processedBy = request.user
                    p.save()
                
                try:
                    mo = d + 1
                    ye = year
                    if d == 12:
                        mo = 1
                        ye += 1
                    next = Transactions.objects.get(acctID=consumer.consumer_id, transType='Billing', year=ye, month=mo)
                    next.usage = next.meterReading - r
                    next.save()
                except ObjectDoesNotExist:
                    pass
            try:
                mo = d - 1
                ye = year
                if d == 1:
                    mo = 12
                    ye -= 1
                prev_bill = Transactions.objects.get(acctID=consumer.consumer_id, transType='Billing', year=ye, month=mo)
                if not prev_bill.is_billpaid:
                    consumer.penaltycounter += 1
            except ObjectDoesNotExist:
                pass

            if consumer.excess > 0:
                unsettled = Transactions.objects.filter(acctID_id=consumer, transType="Billing", is_billpaid=False, is_issue=False).order_by('-year', '-month')
                if unsettled:
                    for u in unsettled:
                        if consumer.excess>=u.bill:
                            ex = consumer.excess - u.bill
                            pt = Transactions()
                            pt.acctID = consumer
                            pt.transType = "Payment"
                            pt.date = datetime.today()
                            pt.year = u.year
                            pt.month = u.month
                            pt.payment = u.bill
                            pt.save()
                            u.is_billpaid = True
                            u.save()
                            consumer.excess = ex
                            consumer.save()
                        else:
                            consumer.save()
                            break

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
        if consumer.excep_accnt:
            get_bal_exempt(id)
        else:
            get_balance(id)
        return redirect('inputreading', id=id , year=year)
    
    context = {
        'consumer': consumer,
        'table': table,
        'cur_year': year,
        'years': years,
        'user': request.user,
        'is_seen_issues': is_seen_issues,
        'notif_viewers': notif_viewers,
    }
    return render(request, 'input-meter-reading.html', context)


@login_required(login_url='login')
def consumer_list(request):
    global notif_viewers
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
            cons = ConsumerInfo.objects.filter(Q(meternumber=search) | Q(consumer_id__icontains=search), deleteflag=0).order_by('lastname', 'firstname', 'middlename')
        else:
            cons = ConsumerInfo.objects.filter(Q(firstname__icontains=search) | Q(middlename__icontains=search) | Q(lastname__icontains=search)| Q(homeaddress__icontains=search), deleteflag=0).order_by('lastname', 'firstname', 'middlename')
    else:
        cons = ConsumerInfo.objects.filter(deleteflag=0).order_by('lastname', 'firstname', 'middlename')   
    
    
    pages = int(request.GET.get('p', 10))
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
        'count':count,
        'consumer_list': cons_list,
        'user': user,
        'is_seen_issues': is_seen_issues,
        'notif_viewers': notif_viewers,
    }
    return render(request, 'conlist.html', context)

@login_required(login_url='login')
def consumercreation(request):
    global notif_viewers
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
    id = cons[0].consumer_id
    last = int(cons[0].consumer_id.split('-')[0])
    if request.method == "POST":
        form = ConsumerForm(request.POST)
        isUpdate = request.POST['isUpdate']
        conid = request.POST['conid']
        firstname = request.POST['firstname']
        middlename = request.POST['middlename']
        lastname = request.POST['lastname']
        mobilenum = request.POST['mobilenum']
        email = request.POST['email']
        birthdate = request.POST['birthdate']
        sex = request.POST['sex']
        sitio = request.POST['sitio']
        homeaddress = request.POST['homeaddress']
        meternumber = request.POST['meternumber']
        initialmeterreading = request.POST['initialmeterreading']
        installation_address = request.POST['installation_address']
        contypeid = request.POST['contypeid']
        penaltycode = request.POST.get('penaltycode')
        if penaltycode == '':
            penaltycode = 'P001'
        if form.is_valid():
            if isUpdate:
                c = ConsumerInfo.objects.get(consumer_id=conid)
            else:
                accstr = ""
                c = ConsumerInfo()
                c.status = 1
                c.stopmeterflag = 0
                c.deleteflag = 0
                c.penaltycounter = 0
                lastid_len = len(str(last + 1))
                len_zeros = 10 - lastid_len
                for x in range(0, len_zeros):
                    accstr += "0"
                accstr += str(last + 1)
                c.consumer_id = accstr + "-01"
            c.firstname = firstname
            c.middlename = middlename
            c.lastname = lastname
            c.mobilenum = mobilenum
            c.email = email
            c.birthdate = birthdate
            if c.birthdate == '':
                c.birthdate = datetime.today()
            c.sex = sex
            c.penaltycode = Penalty.objects.get(penaltycode=penaltycode) 
            c.sitio = sitio
            c.homeaddress = homeaddress
            c.meternumber = meternumber
            c.initialmeterreading = initialmeterreading
            c.installation_address = Barangays.objects.get(id=installation_address) 
            c.contypeid = ConsumerType.objects.get(contypeid=contypeid) 
            c.disconnectionflag = False
            c.date_added = datetime.today()
            c.save()
            return redirect('consumer_list')
    context = {
        'conid':id,
        'form': form,
        'errors': form.errors,
        'user': request.user,
        'create':True,
        'is_seen_issues': is_seen_issues,
        'notif_viewers': notif_viewers,
    }
    return render(request, 'consumercreation.html', context)

@login_required(login_url='login')
def consumerupdate(request, id):
    global notif_viewers
    template = ""
    LoginSession = request.user
    if LoginSession:
        if LoginSession.is_teller or LoginSession.is_supervisor:
            template = "consumercreation.html"
        else:
            template = redirect('bills_list')
            return template 
    try:
        con = ConsumerInfo.objects.get(consumer_id=id)
        form = ConsumerForm(instance=con) 
        penaltyc = con.penaltycounter
    except ValidationError:
        pass
    context = {
        'pc':penaltyc,
        'conid':id,
        'isUpdate':True,
        'form': form,
        'user': request.user,
        'is_seen_issues': is_seen_issues,
        'notif_viewers': notif_viewers,
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
            lasttranid = Transactions.objects.all().order_by('-transactionid').filter(is_issue=False)[0].transactionid
            meternum = request.POST.get('meternum')
            consumer.meternumber = meternum
            initialreading = int(request.POST.get('initialreading'))
            month = int(request.POST.get('month'))
            tran = Transactions()
            tran.transactionid = lasttranid + 1
            tran.date = date.today()
            tran.acctID = consumer
            tran.transType = 'Reset Meter'
            tran.meterReading = initialreading
            consumer.current_reading = initialreading
            tran.usage = 0
            tran.bill = 0
            tran.month = month
            if tran.month == 12:
                tran.year = date.today().year-1
            else:
                tran.year = date.today().year
            tran.processedBy = str(request.user)
            tran.or_number = "N/A"
            tran.save()
            # billtran = Transactions()
            # billtran.transactionid = lasttranid + 2
            # billtran.date = date.today()
            # billtran.acctID = consumer
            # billtran.transType = 'Billing'
            # billtran.meterReading = initialreading
            # billtran.prevReading = initialreading
            # billtran.usage = 0
            # rate = ConsumerType.objects.get(contypeid=consumer.contypeid.contypeid)
            # billtran.bill = rate.minReadingCharge
            # billtran.month = date.today().month-1
            # if billtran.month == 12:
            #     billtran.year = date.today().year-1
            # else:
            #     billtran.year = date.today().year
            # billtran.processedBy = str(request.user)
            # billtran.or_number = ""
            # billtran.save()
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
    search = request.GET.get("search", "")
    page = request.GET.get('page')
    if search:
        sys = SystemUsers.objects.filter(Q(username__icontains=search)|Q(first_name__icontains=search) | Q(mid_name__icontains=search) | Q(last_name__icontains=search)| Q(email__icontains=search)).order_by('username')
    else:
        sys = SystemUsers.objects.all().order_by('username')
    p = int(request.GET.get('p', 10))
    user = request.user
    count = sys.count()
    if p == 0:
        paginate_by = request.GET.get('paginate_by', count)
    else:
        paginate_by = request.GET.get('paginate_by', p)

    paginator = Paginator(sys, paginate_by)
    try:
        sys_list = paginator.page(page)
    except PageNotAnInteger:
        sys_list = paginator.page(1)
    except EmptyPage:
        sys_list = paginator.page(paginator.num_pages)

    class sysuserclass():
        def __init__(self, first_name, last_name, mid_name, username, email, role):
            self.email = email
            self.first_name = first_name
            self.mid_name = mid_name
            self.last_name = last_name
            self.username = username
            self.role = role
    for s in sys_list:
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
        'search':search,
        'sys_list':sys_list,
        'last': range(paginator.num_pages - 3, paginator.num_pages),
        'five': range(1, 6),
        'paginate_by': paginate_by,
        'count': count,
        'table': table,
        'user': request.user
    }
    return render(request, 'sysuser.html', context)


@login_required(login_url='login')
def user_edit(request, id):
    global notif_viewers
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
        for i in form.fields:
            try:
                form.fields[i].widget.attrs['class'] += ' is-valid'
            except KeyError:
                pass
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
                sys.profilepic = 'profile12.png'
            sys.save()
        else:
            for i in form.errors.as_data():
                item = form.fields[i]
                item.widget.attrs['class'] += ' is-invalid'
            messages.error(request, 'User creation failed')
        return redirect('sysuser')
    context = {
        'sys': sys,
        'form': form,
        'user': request.user,
        'is_seen_issues': is_seen_issues,
        'notif_viewers': notif_viewers,
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
        amount = float(request.POST.get('amount'))
        or_num = request.POST['or_num']
        dis_code = request.POST.get('dis_code')
        if amount != 0:
            month = datetime.today().month
            consumer = ConsumerInfo.objects.get(consumer_id=id)
            
            con_bar = consumer.installation_address
            year = datetime.today().year
            try:
                con_b_rec = BarangayRecord.objects.get(barangaycode_id=con_bar, year=year)
            except ObjectDoesNotExist:
                con_b_rec = create_brec(consumer.installation_address_id, year)
            rt = Transactions()
            rt.receivedamt = amount
            rt.acctID = consumer
            rt.transType = "Received Amount"
            rt.date = datetime.today()
            rt.year = year
            rt.month = month
            rt.processedBy = request.user
            rt.or_number = or_num
            rt.save()
            consumer.excess += amount
            consumer.save()
            if consumer.excess > 0:
                unsettled = Transactions.objects.filter(acctID_id=consumer, transType="Billing", is_billpaid=False, is_issue=False).order_by('-year', '-month')
                if unsettled:
                    for i in unsettled:
                        if consumer.excess>=i.bill:
                            ex = consumer.excess - i.bill
                            pt = Transactions()
                            pt.acctID = consumer
                            pt.transType = "Payment"
                            pt.date = datetime.today()
                            pt.year = i.year
                            pt.month = i.month
                            pt.payment = i.bill
                            amount -= i.bill
                            pt.save()
                            i.is_billpaid = True
                            i.save()
                            consumer.excess = ex
                        else:
                            break
                    consumer.save()
                add_fees = AdditionalFees.objects.filter(consumer_id=consumer)
                for af in add_fees:
                    aftran = Transactions.objects.get(transactionid=af.current_tran)
                    
                    if af.months == 0:
                        af_amount = af.remainder
                    else:
                        af_amount = af.amount
                    if not aftran.is_billpaid and amount >= af_amount:
                        aftran.is_billpaid = True
                        aftran.save()
                        p_aftran = Transactions()
                        p_aftran.payment = af_amount
                        consumer.excess-=af_amount
                        p_aftran.acctID = consumer
                        p_aftran.transType = "Payment"
                        p_aftran.date = datetime.today()
                        p_aftran.year = aftran.year
                        p_aftran.month = aftran.month
                        p_aftran.processedBy = request.user
                        p_aftran.save()
                        af.months -= 1

                        # libog pa kaayo ni tarunga nya ni
                        if af.months > 0:
                            new_aftran = Transactions()
                            new_aftran.acctID = consumer
                            new_aftran.transType = "Additional Fees"
                            new_aftran.date = datetime.today()
                            if aftran.month == 12:
                                new_aftran.month = 1
                                new_aftran.year = aftran.year+1
                            else:
                                new_aftran.month = aftran.month+1
                                new_aftran.year = aftran.year
                            new_aftran.processedBy = request.user
                            if af.months == 1 and af.remainder != 0:
                                new_aftran.bill = af.remainder
                            else:
                                consumer.current_bal += af.amount
                                new_aftran.bill = af.amount
                            new_aftran.save()
                            consumer.current_bal += new_aftran.bill
                            af.current_tran = new_aftran.transactionid
                        af.save()
                        consumer.save()
            try:
                discount = Discount.objects.get(discountcode=dis_code)
            except ObjectDoesNotExist:
                pass
            else:
                dt = Transactions()
                dt.acctID = consumer
                dt.transType = "Discount"
                dt.date = datetime.today()
                dt.year = year
                dt.month = month
                dt.processedBy = request.user
                dt.discountcode = discount.discountcode
                dt.payment = amount*(discount.discount_rate/100)
                amount -= amount*(discount.discount_rate/100)
                dt.save()
                rt.discountcode = dt.transactionid
                rt.processedBy = request.user.username
                rt.save()
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
def editpayment(request, id):
    if request.method =='POST':
        ted = Transactions.objects.get(transactionid=id)
        prevpayment = ted.receivedamt
        con = ted.acctID
        amount = float(request.POST['amount'])
        or_num = request.POST['or_num']
        dis_code = request.POST.get('dis_code')
        dif = amount - prevpayment
        con.excess += dif
        con.save()
        ted.receivedamt = amount
        ted.or_number = or_num
        ted.save()
        try:
            dt = Transactions.objects.get(transactionid=ted.discountcode)
        except ObjectDoesNotExist:
            dt = None
        if dis_code == '':
            if dt:
                dt.delete()
        else:
            if dt:
                try:
                    dcode = Discount.objects.get(discountcode=dis_code)
                except ObjectDoesNotExist:
                    dcode = None
                if dcode:
                    dt.acctID = ted.acctID
                    dt.transType = "Discount"
                    dt.date = datetime.today()
                    dt.year = ted.year
                    dt.month = ted.month
                    dt.processedBy = request.user.username
                    dt.discountcode = dcode.discountcode
                    dt.payment = amount*(dcode.discount_rate/100)
                    amount -= amount*(dcode.discount_rate/100)
                    dt.save()
                    ted.discountcode = dt.transactionid
                    ted.save()
            else:
                try:
                    dcode = Discount.objects.get(discountcode=dis_code)
                except ObjectDoesNotExist:
                    dcode = None
                if dcode:
                    dt = Transactions()
                    dt.acctID = ted.acctID
                    dt.transType = "Discount"
                    dt.date = datetime.today()
                    dt.year = ted.year
                    dt.month = ted.month
                    dt.processedBy = request.user.username
                    dt.or_number = or_num
                    dt.discountcode = dcode.discountcode
                    dt.payment = amount*(dcode.discount_rate/100)
                    amount -= amount*(dcode.discount_rate/100)
                    dt.save()
                    ted.discountcode = dt.transactionid
                    ted.save()
            brec = BarangayRecord.objects.get(year=ted.year, barangaycode=ted.acctID.installation_address)
            brec.__dict__[f"total_paid_{months[ted.month-1]}"] -= prevpayment
            brec.__dict__[f"total_paid_{months[ted.month-1]}"] += ted.payment
            brec.save()

        get_balance(ted.acctID.consumer_id)
        
        if con.excess < 0:
            con.current_bal += (con.excess*-1)
            con.excess = 0
            con.save()
        return redirect('payment_history', ted.acctID.consumer_id,ted.year)

def reports(request):
    cur_year =  datetime.today().year
    cur_month = datetime.today().month
    if cur_month == 1:
        cur_year-=1
    return redirect('barangayreport', cur_year)

@login_required(login_url='login')
def barangayreport(request, year):
    global notif_viewers
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
            print(years)
    years.sort(reverse=True)
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
        'is_br':True,
        'is_seen_issues': is_seen_issues,
        'notif_viewers': notif_viewers,
    }
    return render(request, 'waterusage.html', context)


def view_barangay(request, id):
    global notif_viewers
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
        'is_seen_issues': is_seen_issues,
        'notif_viewers': notif_viewers,
    }
    return render(request, 'view_barangay.html', context)

def usage_report_data(request, year):
    global notif_viewers

    template = ""
    LoginSession = request.user
    if LoginSession:
        if LoginSession.is_teller or LoginSession.is_supervisor:
            template = "usage_report_data.html"
        else:
            template = redirect('bills_list')
            return template


    years = []
    bars = Barangays.objects.all()
    mybars = []
    mymonths = []
    my = BarangayRecord.objects.all()
    for i in my:
        if i.year not in years:
            years.append(i.year)
    years.sort()
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
    tu_bills = BarangayRecord.objects.filter(year=year).aggregate(
        jan=Sum('total_due_jan'),
        feb=Sum('total_due_feb'),
        mar=Sum('total_due_mar'),
        apr=Sum('total_due_apr'),
        may=Sum('total_due_may'),
        jun=Sum('total_due_jun'),
        jul=Sum('total_due_jul'),
        aug=Sum('total_due_aug'),
        sept=Sum('total_due_sept'),
        oct=Sum('total_due_oct'),
        nov=Sum('total_due_nov'),
        dec=Sum('total_due_dec'),
    )
    # By Barangay total Usage
    tu_bay = BarangayRecord.objects.filter(year=year,).annotate(
        sums=Sum(F('total_usage_jan') + F('total_usage_feb') + F('total_usage_mar') + F('total_usage_apr') + F('total_usage_may') + F('total_usage_jun') + F('total_usage_jul') + F('total_usage_aug') + F('total_usage_sept') + F('total_usage_oct') + F('total_usage_nov') + F('total_usage_dec'))).annotate(
        sum=(F('sums'))
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

    total_unb = []
    class total_usages_and_billing:
        def __init__(self, month, usage, bill) -> None:
            self.month = month
            self.usage = usage
            self.bill = bill
    for i, m in enumerate(months):
        total_unb.append(total_usages_and_billing(m,tu_mon[m],tu_bills[m]))
    context = {
        'mybars':mybars,
        'tu_mon': tu_mon,
        'tu_bay': tu_bay,
        'cur_year': year,
        'years': years,
        'my': my,
        'user': request.user,
        'is_ur':True,
        'total_unb':total_unb,
        'is_seen_issues': is_seen_issues,
        'notif_viewers': notif_viewers,
    }
    return render(request, 'usage_report_data.html', context)


def revenue_report(request, year):
    global notif_viewers
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
    years.sort()
    # Total Collection\-
    if BarangayRecord.objects.filter(year=year):
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
    else:
        rev_col = {'jan': 0, 'feb': 0, 'mar': 0, 'apr': 0, 'may': 0, 'jun': 0, 'jul': 0, 'aug': 0, 'sept': 0, 'oct': 0, 'nov': 0, 'dec': 0}
        filt = {}
        col = 0
        rec = 0
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
        'is_seen_issues': is_seen_issues,
        'notif_viewers': notif_viewers,
    }
    return render(request, 'revenue_report.html',  context)


def deleteconsumer(request):
    template = ""
    LoginSession = request.user 
    if LoginSession:
        if LoginSession.is_teller or LoginSession.is_supervisor:
            template = "consumercreation.html"
        else:
            template = redirect('bills_list')
            return template
    if request.method == 'POST':
        id = request.POST['id']
        search = request.POST['search']
        page = request.POST['page']
        p = request.POST['p']
        con = ConsumerInfo.objects.get(consumer_id=id)
        con.deleteflag = True
        con.save()
    return redirect(f'/consumer_list/?page={page}&search={search}&p={p}')



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
    global notif_viewers
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
            ubs = ConsumerInfo.objects.filter(Q(meternumber=search) | Q(consumer_id__icontains=search), current_bal__gt = 0).order_by('lastname','firstname','middlename')
        else:
            ubs = ConsumerInfo.objects.filter(Q(firstname__icontains=search) | Q(middlename__icontains=search) | Q(lastname__icontains=search), current_bal__gt = 0).order_by('lastname','firstname','middlename')
    else:
        ubs = ConsumerInfo.objects.filter(current_bal__gt=0).order_by('lastname','firstname','middlename')


    #Sort code to sort fields
    sort_field = request.GET.get("sort_field", "consumer_id")
    sort_order = request.GET.get("sort_order","asc")
    if sort_order == "desc":
        sort_field = "-" + sort_field
    
    ubs = ubs.order_by(sort_field)
    pages = int(request.GET.get('p', 10))
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
        alltran = Transactions.objects.filter(acctID_id=j.consumer_id, transType='Billing', is_issue=False).order_by('-year')
        if alltran:
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
        'count':count,
        'user': request.user,
        'sort_field' : sort_field,
        'sort_order' : sort_order,
        'is_seen_issues': is_seen_issues,
        'notif_viewers': notif_viewers,
   
     
    }
    return render(request, 'unsettled_bill.html', context)


def view_unsettled_bills(request, id, year):
    global notif_viewers
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
    alltran = Transactions.objects.filter(acctID_id=id, transType='Billing', is_issue=False)
    billing = Transactions.objects.filter(
        acctID_id=id, transType='Billing', year=year, is_issue=False)
    payment = Transactions.objects.filter(
        acctID_id=id, transType='Payment', year=year, is_issue=False)
    pcount = len(payment)
    count = len(billing)
    j = 0
    try:
        if billing[0].date.month == 1:
          j = 1
    except IndexError:
        pass
    for i in alltran:
        if i.year not in years:
            years.append(i.year)

    years.sort()
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
        'is_seen_issues': is_seen_issues,
        'notif_viewers': notif_viewers,
    }
    return render(request, 'view_unsettled_bills.html', context)


def discount(request):
    global notif_viewers
    dc = Discount.objects.all()
    try:
        lastdisc_id = int(Discount.objects.all().order_by('-discountcode')[0].discountcode.split('D')[::-1][0])
    except IndexError:
        lastdisc_id = 0
    user = request.user
    if request.method == "POST":
        discount_rate = request.POST['discount_rate']
        addD = Discount()
        strlen = len(str(lastdisc_id+1))
        zeroes = ''
        for i in range(3-strlen):
            zeroes+="0"
        addD.discountcode = "D"+zeroes+str(lastdisc_id+1)
        addD.discount_rate = discount_rate
        addD.added_by = user
        addD.date_added = datetime.today()
        addD.save()
        messages.success(request, 'Discount has been added')
        return redirect('discount')
    context = {
        'dc': dc,
        'user': user,
        'is_discount':True,
        'is_seen_issues': is_seen_issues,
        'notif_viewers': notif_viewers,
    }
    return render(request, 'discount.html', context)

def editdiscount(request, id):
    dis = Discount.objects.get(discountcode=id)
    if request.method == 'POST':
        discount_rate = request.POST['discount_rate']
        dis.discount_rate = discount_rate
        dis.save()
        messages.success(request, 'Code has been updated')
        
    return redirect('discount')

def deletediscount(request,id):

    try:
        dis = Discount.objects.get(discountcode=id)
        dis.delete()
        messages.success(request, 'Code has been deleted')
    except Penalty.DoesNotExist:
        messages.error(request, 'Code does not exist')
    return redirect('discount')



@login_required(login_url='login')
def new_consumertype(request):
    global notif_viewers
    cont = ConsumerType.objects.all().order_by
    form = ConscumertypecreationForm()
    contypecount = int(ConsumerType.objects.all().order_by('-contypeid')[0].contypeid.split('C')[::-1][0])
    if request.method == "POST":
        contype = request.POST['contype']
        minReading = request.POST['minReading']
        minReadingCharge = request.POST['minReadingCharge']
        rateAfterMin = request.POST['rateAfterMin']
        ct = ConsumerType()
        strlen = len(str(contypecount+1))
        zeroes = ''
        for i in range(3-strlen):
            zeroes+="0"
        ct.contypeid = "C"+zeroes+str(contypecount+1)
        ct.contype = contype
        ct.minReading = minReading
        ct.minReadingCharge = minReadingCharge
        ct.rateAfterMin = rateAfterMin
        ct.added_by = request.user
        ct.date_added = date.today()
        ct.save()
        messages.success(request, 'Consumer Type has been added')
        return redirect('new_consumertype')
    context = {
        'cont': cont,
        'form': form,
        'errors': form.errors,
        'user': request.user,
        'is_contype':True,
        'is_seen_issues': is_seen_issues,
        'notif_viewers': notif_viewers,
    }
    return render(request, 'new_consumertype.html', context)

def editcontype(request, id):
    con = ConsumerType.objects.get(contypeid=id)
    if request.method == 'POST':
        contype = request.POST['contype']
        minReading = request.POST['minReading']
        minReadingCharge = request.POST['minReadingCharge']
        rateAfterMin = request.POST['rateAfterMin']
        
        con.contype = contype
        con.minReading = minReading
        con.minReadingCharge = minReadingCharge
        con.rateAfterMin = rateAfterMin
        con.save()
        messages.success(request, 'Code has been updated')
        
    return redirect('new_consumertype')


@login_required(login_url='login')
def penalty(request):
    global notif_viewers
    penalty = Penalty.objects.all()
    form = addPenalty
    penaltycounter = int(Penalty.objects.all().order_by('-penaltycode')[0].penaltycode.split('P')[::-1][0])
    if request.method == "POST" and 'btnform1' in request.POST:
        penalty_info = request.POST['penalty_info']
        penalty_rate = request.POST['penalty_rate']
        penalty_after = request.POST['penalty_after']
        daysappliedafter = request.POST['daysappliedafter']
        pen = Penalty()
        strlen = len(str(penaltycounter+1))
        zeroes = ''
        for i in range(3-strlen):
            zeroes+="0"
        pen.penaltycode = "P"+zeroes+str(penaltycounter+1)
        pen.penalty_info = penalty_info
        pen.penalty_rate = penalty_rate
        pen.penalty_after = penalty_after
        pen.daysappliedafter = daysappliedafter
        pen.added_by = request.user
        pen.save()
        messages.success(request, 'Penalty has been added')
        return redirect('penalty')
    context = {
        'penalty': penalty,
        'form1': form,
        'errors': form.errors,
        'user': request.user,
        'is_penalty':True,
        'is_seen_issues': is_seen_issues,
        'notif_viewers': notif_viewers,
    }

    return render(request, 'penalty.html', context)


def editpenalty(request, id):
    pen = Penalty.objects.get(penaltycode=id)
    if request.method == 'POST':
        penalty_info = request.POST['penalty_info']
        penalty_rate = request.POST['penalty_rate']
        penalty_after = request.POST['penalty_after']
        daysappliedafter = request.POST['daysappliedafter']
       
        pen.penalty_info = penalty_info
        pen.penalty_rate = penalty_rate
        pen.penalty_after = penalty_after
        pen.daysappliedafter = daysappliedafter
        pen.save()
        messages.success(request, 'Code has been updated')
        return redirect('penalty')

def bulkreading(request):
    global notif_viewers
    template = ""
    year = int(request.GET.get('fyear', datetime.today().year))
    month = int(request.GET.get('fmonth', datetime.today().month))
    search = request.GET.get("search", "")
    page = request.GET.get('page')
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
    isnum = search.isnumeric()
    if search:
        if isnum:
            consumers = ConsumerInfo.objects.filter(Q(meternumber=search) | Q(consumer_id__icontains=search),stopmeterflag=0, deleteflag=0, disconnectionflag=0).order_by('lastname', 'firstname', 'middlename')
        else:
            consumers = ConsumerInfo.objects.filter(Q(firstname__icontains=search) | Q(middlename__icontains=search) | Q(lastname__icontains=search)| Q(homeaddress__icontains=search),stopmeterflag=0, deleteflag=0, disconnectionflag=0).order_by('lastname', 'firstname', 'middlename')
    else:
        consumers = ConsumerInfo.objects.filter(stopmeterflag=0, deleteflag=0, disconnectionflag=0).order_by('lastname', 'firstname', 'middlename')
    
    pages = int(request.GET.get('p', 10))

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
            tran = Transactions.objects.get(acctID_id=i.consumer_id, month=month, year=year, transType="Billing")
            cur = tran.meterReading
            latest = False
        except ObjectDoesNotExist:
            cur = 0
            latest = True
        try:
            if latest:
                prev = i.current_reading
            else:
                if month == 1:
                    tran = Transactions.objects.get(acctID_id=i.consumer_id, month=12, year=year-1, transType="Billing")
                else:
                    tran = Transactions.objects.get(acctID_id=i.consumer_id, month=month-1, year=year, transType="Billing")
                prev = tran.meterReading
        except ObjectDoesNotExist:
            prev = 0
        # prev = last_reading(i.consumer_id, year, month)
        consumers_list.append(new_con(i, prev, cur))
    if request.method == "POST":
        
        con_list = []
        psearch = request.POST.get('psearch')
        isnum = psearch.isnumeric()
        pp = request.POST.get('pp')
        if psearch:
            if isnum:
                consumers = ConsumerInfo.objects.filter(Q(meternumber=psearch) | Q(consumer_id__icontains=psearch),stopmeterflag=0, deleteflag=0, disconnectionflag=0).order_by('lastname', 'firstname', 'middlename')
            else:
                consumers = ConsumerInfo.objects.filter(Q(firstname__icontains=psearch) | Q(middlename__icontains=psearch) | Q(lastname__icontains=psearch)| Q(homeaddress__icontains=psearch),stopmeterflag=0, deleteflag=0, disconnectionflag=0).order_by('lastname', 'firstname', 'middlename')
        else:
            consumers = ConsumerInfo.objects.filter(stopmeterflag=0, deleteflag=0, disconnectionflag=0).order_by('lastname', 'firstname', 'middlename')

        count = len(consumers)
        if pp == 0:
            paginate_by = request.GET.get('paginate_by', count)
        else:
            paginate_by = request.GET.get('paginate_by', pp)
        page = request.GET.get('page')
        paginator = Paginator(consumers,paginate_by)
        try:
            ub = paginator.page(page)
        except PageNotAnInteger:
            ub = paginator.page(1)
        except EmptyPage:
            ub = paginator.page(paginator.num_pages)
        for i in ub:
            try:
                tran = Transactions.objects.get(acctID_id=i.consumer_id, month=month, year=year, transType="Billing")
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
            con_list.append(new_con(i, prev, cur))
        interest = 0
        pmonth = int(request.POST.get('pmonth'))
        pyear = int(request.POST.get('pyear'))
        for j in con_list:
            c = ConsumerInfo.objects.get(consumer_id=j.con.consumer_id)
            yt = Transactions.objects.filter(acctID=c.consumer_id, is_issue=False).values_list('year', flat=True)
            years_backward = []
            for i in yt:
                if i not in years_backward and i <= pyear:
                    years_backward.append(i)
            years_backward.sort(reverse=True)
            years_forward = []
            for i in yt:
                if i not in years_forward and i >= pyear:
                    years_forward.append(i)
            years_forward.sort()
            a = request.POST.get(f"con{c.consumer_id}", None)
            if a is not None:
                try:
                    con_b_rec = BarangayRecord.objects.get(barangaycode_id=c.installation_address_id, year=pyear)
                except ObjectDoesNotExist:
                    con_b_rec = create_brec(c.installation_address_id, pyear)
                bill = 0
                usage = 0
                a = int(a)
                try:
                    tran = Transactions.objects.get(acctID_id=c.consumer_id,month=pmonth,year=pyear,transType = "Billing")
                    lastreading = tran.prevReading
                    # finding next billing
                    mm = pmonth+1
                    has_next = False
                    for y in years_forward:
                        for x in range(mm, 13):
                            try:
                                next = Transactions.objects.get(acctID=c.consumer_id, transType='Billing', year=y, month=x)
                                next.prevReading = a
                                next.usage = next.meterReading - a
                                next.save()
                                has_next = True
                                break
                            except ObjectDoesNotExist:
                                pass
                        if has_next:
                            break
                        mm = 1
                    
                    # finding previous billing
                    if has_next:
                        mm = pmonth-1
                        has_prev = False
                        for y in years_backward:
                            for x in range(mm, 0, -1):
                                try:
                                    prev = Transactions.objects.get(acctID=c.consumer_id, transType='Billing', year=y, month=x)
                                    lastreading = prev.meterReading
                                    has_prev = True
                                    break
                                except ObjectDoesNotExist:
                                    pass
                            if has_prev:
                                break
                            mm = 12

                    tran.meterReading = a
                    tran.usage = a - lastreading
                    tran.save()
                except ObjectDoesNotExist:
                    t = Transactions()
                    try:
                        if pmonth == 1:
                            tran = Transactions.objects.get(acctID_id=c.consumer_id,month=12,year=pyear-1,transType = "Billing")
                        else:    
                            tran = Transactions.objects.get(acctID_id=c.consumer_id,month=pmonth-1,year=pyear,transType = "Billing")
                        prev = tran.meterReading
                    except ObjectDoesNotExist:
                        prev = 0
                    cummulative = get_cummulative(c.consumer_id)
                    try:
                        con_penalty = Penalty.objects.get(penaltycode=c.penaltycode)
                        if c.penaltycounter >= con_penalty.penalty_after and con_penalty.penalty_rate != 0:
                            xy = con_penalty.penalty_rate * cummulative
                            interest = xy/100
                    except ObjectDoesNotExist:
                        interest = 0
                    t.acctID = c
                    t.transType = 'Billing'
                    t.date = datetime.today()
                    t.month = pmonth
                    t.year = pyear
                    t.meterReading = a
                    t.prevReading = prev
                    t.usage = a - prev
                    usage = a - prev
                    t.contypeid = c.contypeid_id
                    rate = ConsumerType.objects.get(contypeid=c.contypeid_id)
                    if t.usage <= rate.minReading or t.usage < 0:
                        t.bill = rate.minReadingCharge
                    else:
                        bill = ((t.usage - rate.minReading) * rate.rateAfterMin) + rate.minReadingCharge
                        t.bill = bill
                    t.payment = 0
                    t.processedBy = request.user
                    t.save()
                    
                    try:
                        mo = pmonth - 1
                        ye = year
                        if pmonth == 1:
                            mo = 12
                            ye -= 1
                        prev_bill = Transactions.objects.get(acctID=c.consumer_id, transType='Billing', year=ye, month=mo)
                        if not prev_bill.is_billpaid:
                            c.penaltycounter += 1
                    except ObjectDoesNotExist:
                        pass
                    if interest:
                        p = Transactions()
                        p.acctID = c
                        p.transType = 'Penalty'
                        p.date = datetime.today()
                        p.month = pmonth
                        p.year = pyear
                        p.bill = interest
                        bill += interest
                        p.payment = 0
                        p.processedBy = request.user
                        p.save()
                con_b_rec.__dict__[f"total_due_{months[pmonth-1]}"] += bill
                con_b_rec.__dict__[f"total_usage_{months[pmonth-1]}"] += usage
                
                con_b_rec.save()
                if c.excess > 0:
                    unsettled = Transactions.objects.filter(acctID_id=c, transType="Billing", is_billpaid=False, is_issue=False).order_by('-year', '-month')
                    if unsettled:
                        for u in unsettled:
                            if c.excess>=u.bill:
                                ex = c.excess - u.bill
                                pt = Transactions()
                                pt.acctID = c
                                pt.transType = "Payment"
                                pt.date = datetime.today()
                                pt.year = u.year
                                pt.month = u.month
                                pt.payment = u.bill
                                pt.save()
                                u.is_billpaid = True
                                u.save()
                                c.excess = ex
                                c.save()
                            else:
                                c.save()
                                break  
                get_balance(c.consumer_id)
        return redirect(f'/meterreading/bulkreading?page={page}&fyear={pyear}&fmonth={pmonth}&search={psearch}&p={pp}')
    else:
        context = {
            'bulky':True,
            'search':search,
            'year':year,
            'month':mname,
            'years':years,
            'months':months,
            'monthval':month,
            'consumers_list':consumers_list,
            'ub':ub,
            'count':count,
            'paginate_by': paginate_by,
            'last' : range(paginator.num_pages-3, paginator.num_pages),
            'five' : range(1,6),
            'user':request.user,
            'is_seen_issues': is_seen_issues,
            'notif_viewers': notif_viewers,
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
        'is_profile':True,
        'is_seen_issues': is_seen_issues,
        'notif_viewers': notif_viewers,
    }
    return render(request, 'viewprof.html', context)

@login_required(login_url='login')
def userprof(request):
    global notif_viewers
    user = SystemUsers.objects.get(username=str(request.user))
    form = ProfileForm(instance=user)
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=user)
        profilepic = request.FILES.get('profilepic', False)
        if form.is_valid():
            if profilepic:
                user.profilepic = profilepic
            else:
                user.profilepic = user.profilepic
            user.save()
            messages.success(
                    request, 'Your Profile Updated Successfully')
            return redirect('settings')
    context= {
        'user':user,
        'form':form,
        'is_seen_issues': is_seen_issues,
        'notif_viewers': notif_viewers,
    }
    return render(request, 'userprof.html', context)

def monthly_summary (request, id, year):
    global notif_viewers
    table = []
    years = []
    class montly_sum():
        def __init__(self, month, monthval, reading, reading_date, usage, total_bill, total_amount_paid, payid):
            self.month = month
            self.monthval = monthval
            self.reading = reading
            self.reading_date = reading_date
            self.usage = usage
            self.total_bill = total_bill
            self.total_amount_paid = total_amount_paid
            self.payid = payid

    consumer = ConsumerInfo.objects.get(consumer_id=id)
    alltran = Transactions.objects.filter(acctID_id=id, transType='Billing', is_issue=False)
    billing = Transactions.objects.filter(acctID_id=id, transType='Billing', year=year, is_issue=False).order_by('month')
    payment = Transactions.objects.filter(acctID_id=id, transType='Payment', year=year, is_issue=False).order_by('month')
    
    lastid = Transactions.objects.latest('transactionid').transactionid
    pcount = len(payment)
    count = len(billing)
    j = 0
    try:
        if billing[0].date.month == 1:
            j = 1
    except IndexError:
        j=0

    for i in alltran:
        if i.year not in years:
            years.append(i.year)
            print(years)
    if datetime.today().year not in years:
        years.append(datetime.today().year)

    # --------------------------#

    j = 0
    c = 0
    for i in range(1, 13):
        lastid+=1
        payid = lastid
        month = calendar.month_name[i]
        usage = 0
        reading = 0
        total_bill = 0
        reading_date = ''
        total_amount_paid = 0
        if c < pcount and pcount != 0:
            if i == payment[c].month:
                total_amount_paid = payment[c].payment
                payid = payment[c].transactionid
                c += 1
        if j < count and count != 0:
            if i == billing[j].month:
                usage = billing[j].usage
                reading = billing[j].meterReading
                reading_date = billing[j].date
                total_bill = billing[j].bill
                j += 1
        a = montly_sum(month, i, reading, reading_date, usage, total_bill, total_amount_paid, payid)
        table.append(a)
    context = {
        'table': table,
        'u': consumer,
        'year' : year,
        'years': years,
        'is_seen_issues': is_seen_issues,
        'notif_viewers': notif_viewers,
        

    }
    return render(request,'conmon_summary.html', context)

def monthlypayment(request):
    global notif_viewers
    if request.method == "POST":
        month = int(request.POST.get(f'month', 0))
        year = int(request.POST.get(f'year', 0))
        payment = float(request.POST.get(f'payment', 0))
        conid = request.POST.get(f'conid', 0)
        or_num = request.POST.get(f'or_num', 0)
        consumer = ConsumerInfo.objects.get(consumer_id = conid)
        try:
            con_b_rec = BarangayRecord.objects.get(barangaycode_id=consumer.installation_address_id, year=year)
        except ObjectDoesNotExist:
            con_b_rec = create_brec(consumer.installation_address_id, year)
        try:
            Transactions.objects.get(acctID_id = conid, transType = "Payment", month = month, year = year)
        except ObjectDoesNotExist:
            paytran = Transactions()
            paytran.payment = payment
            paytran.date = date.today()
            paytran.acctID = consumer
            paytran.month = month
            paytran.year = year
            paytran.transType = "Payment"
            paytran.processedBy = request.user
            paytran.save()
            recT = Transactions()
            recT.receivedamt = payment
            recT.date = date.today()
            recT.acctID = consumer
            recT.month = month
            recT.year = year
            recT.transType = "Received Amount"
            recT.processedBy = request.user
            recT.or_number = or_num
            recT.save()
            try:
                billtran = Transactions.objects.get(acctID_id = conid, transType = "Billing", month = month, year = year)
                billtran.is_billpaid = True
                billtran.save()
            except ObjectDoesNotExist:
                pass
            get_balance(consumer.consumer_id)
            match month:
                case 1:
                    con_b_rec.total_paid_jan += payment
                case 2:
                    con_b_rec.total_paid_feb += payment
                case 3:
                    con_b_rec.total_paid_mar += payment
                case 4:
                    con_b_rec.total_paid_apr += payment
                case 5:
                    con_b_rec.total_paid_may += payment
                case 6:
                    con_b_rec.total_paid_jun += payment
                case 7:
                    con_b_rec.total_paid_jul += payment
                case 8:
                    con_b_rec.total_paid_aug += payment
                case 9:
                    con_b_rec.total_paid_sept += payment
                case 10:
                    con_b_rec.total_paid_oct += payment
                case 11:
                    con_b_rec.total_paid_nov += payment
                case 12:
                    con_b_rec.total_paid_dec += payment
            con_b_rec.save()
            
    return redirect('monthly_summary', id=conid, year=year)

def payment_history (request, id, year):
    global notif_viewers
    years = []
    
    consumer = ConsumerInfo.objects.get(consumer_id = id)
    yer = Transactions.objects.filter(acctID_id=id, transType='Received Amount', is_issue=False)
    alltran = Transactions.objects.filter(acctID_id=id, transType='Received Amount', year=year, is_issue=False)


    for i in yer:
        if i.year not in years:
            years.append(i.year)
    if datetime.today().year not in years:
        years.append(datetime.today().year)
    if int(year) in years:
        years.remove(int(year))
        
    context = {
        'u' : consumer,
        'alltrans' : alltran,
        'years'    : years,
        'year'     : year,
        'is_seen_issues': is_seen_issues,
        'notif_viewers': notif_viewers,
    }

    return render(request,'payment_history.html', context)

def consumption(request, year):
    global notif_viewers
    cons = ConsumerInfo.objects.all()
    cons_len = len(cons)
    latest_bills = []
    count_ranges = {
        '<=5' : 0,
        '<=10': 0,
        '<=15': 0,
        '<=20': 0,
        '<=25': 0,
        '<=30': 0,
        '<=35': 0,
        '<=40': 0,
        '<=45': 0,
        '<=50': 0,
        '>50': 0,
    }
    years = []
    top_10 = []
    top_10_del_amount = []
    top_10_del_month = []
    class delinquent_amount:
        def __init__(self, name, balance) -> None:
            self.name = name
            self.balance = balance
    class delinquent_month:
        def __init__(self, name, months) -> None:
            self.name = name
            self.months = months
    class consumption:
        def __init__(self, name, usage) -> None:
            self.name = name
            self.usage = usage
    for i in cons:
        try:
            bill = Transactions.objects.filter(acctID_id=i.consumer_id, year=year, transType="Billing", is_issue=False,).order_by('-transactionid')[0]
            latest_bills.append(bill)
            for k, v in count_ranges.items():
                range_max = int(k[2:])  # extract the minimum value from the key (e.g. 'l10' -> 10)
                if bill.usage < range_max:
                    count_ranges[k] += 1
                    break
            else:
                count_ranges['>50'] += 1 
        except IndexError:
            pass
    bill_len = sum(count_ranges.values())
    count_ranges['<=5']+=(cons_len-bill_len)
    top10 = sorted(latest_bills, key=lambda c: c.usage, reverse=True)[:10]
    for i in top10:
        con = consumption(f"{i.acctID.firstname} {i.acctID.lastname}", i.usage)
        top_10.append(con)

    del_amount = sorted(cons, key=lambda c: c.current_bal, reverse=True)[:10]
    for i in del_amount:
        top_10_del_amount.append(delinquent_amount(f"{i.firstname} {i.lastname}", i.current_bal))

    del_month = sorted(cons, key=lambda c: c.penaltycounter, reverse=True)[:10]
    for i in del_month:
        if i.penaltycounter > 0:
            top_10_del_month.append(delinquent_month(f"{i.firstname} {i.lastname}", i.penaltycounter))
    
    condemn = ConsumerInfo.objects.filter(deleteflag=True).order_by('-current_bal')

    # find total stopped meters
    sm_arr = cons.filter(stopmeterflag=True)
    stopped_meters = sm_arr.count()
    
    # Total of Consumers
    consumtots = cons.count()
 

    # Year selection
    my = BarangayRecord.objects.all()
    for i in my:
        if i.year not in years:
            years.append(i.year)
    tyc = []
    class yeartots:
        def __init__(self, year, total) -> None:
            self.year = year
            self.total = total
    years.sort()
    for y in years:
        tyc.append(yeartots(y, len(cons.filter(first_tran__lt=y))))


    # Total Yearly Consumers 

    context = {
        'condemn':condemn,
        'consumtots':consumtots,
        'count_ranges':count_ranges,
        'top_10':top_10,
        'top_10_del_amount':top_10_del_amount,
        'top_10_del_month':top_10_del_month,
        'tsm':stopped_meters,
        'cur_year': year,
        'years': years,
        'tyc' : tyc,
        'is_cc':True,
        'sm_arr':sm_arr,
        'is_seen_issues': is_seen_issues,
        'notif_viewers': notif_viewers,
    }
    return render(request,'consumption.html', context)


def exemptiont(request):
    global notif_viewers
    exempt_cons = ConsumerInfo.objects.filter(excep_accnt=True)
    context = {
    'cons':exempt_cons,
    'is_exemption':True
    }
    return render(request, 'exemption.html', context)

def addexemption(request, id):

    try:    
        # Retrieve the ConsumerInfo object
        consumer_info = ConsumerInfo.objects.get(consumer_id=id)
    except ConsumerInfo.DoesNotExist:
        return HttpResponse("ConsumerInfo not found.", status=404)

    # Toggle the value of excep_accnt
    consumer_info.excep_accnt = not consumer_info.excep_accnt

    # Save the updated object
    consumer_info.save()
    exempt_accounts(consumer_info)
    get_bal_exempt(consumer_info.consumer_id)

    # Redirect to a different URL or render a template as needed
    return redirect(request.META.get('HTTP_REFERER', '/'))


notif_viewers = ["Klabuh"]

def add_issue(request, id, year):
    global notif_viewers
    consumer = ConsumerInfo.objects.get(consumer_id=id)
    if request.method == 'POST':
        for i in range(12):
            if request.POST.get(f'reading-{calendar.month_name[i+1]}'):
                d = i+1
                val = request.POST.get(f'reading-{calendar.month_name[d]}')
                break
        try:
            tran = Transactions.objects.get(acctID_id=id, month=d, year=year, is_issue=True)
        except ObjectDoesNotExist:
            tran = Transactions()
        tran.meterReading = val
        tran.prevReading = request.POST.get(f'prev-{calendar.month_name[d]}')
        tran.acctID = consumer
        tran.date = date.today()
        tran.month = d
        tran.year = year
        tran.transType = 'Billing'
        tran.is_issue = True
        tran.processedBy = request.user.username
        tran.contypeid = consumer.contypeid.contypeid
        tran.save()

        i = Issues()
        i.date = date.today()
        i.transactionid = tran
        i.issue = "Reading"
        i.issued_by = request.user
        notif_viewers.append(request.user.username)
        i.save()

    return redirect(request.META.get('HTTP_REFERER', '/')) 


def issues_view(request):
    global notif_viewers
    issues = Issues.objects.all()
    last_message = None
    try:
        for issue in issues:
            last_message = Messages.objects.filter(issue_id=issue).order_by('-time').first()
            if last_message:
                issue.last_comment = last_message.message
                issue.save()
    except NameError:
        pass

    
    context = {
        'issues': issues,
        'is_seen_issues': is_seen_issues,
        'notif_viewers': notif_viewers,
        'last_message': last_message,
    }
    return render(request, 'issues.html', context)

def issue_details(request, id):
    global notif_viewers
    issue = Issues.objects.get(issueid=id)
    if not issue.is_seen:
        issue.is_seen = True
        issue.save()
    try:
        tran = issue.transactionid
        month = tran.month
        monthval = calendar.month_name[month]
        con = tran.acctID
    except ObjectDoesNotExist:
        issue.delete()
        return redirect('issues')
    comments = Messages.objects.filter(issue_id=issue)
    for comment in comments:
        if comment.from_user != request.user:
            comment.is_read = True

        comment.save()

    context = {
        'is_seen_issues':is_seen_issues,
        'isdel': issue,
        'con': con,
        'tran': tran,
        'monthval': monthval,
        'comments': comments,
        'is_resolved':issue.status == "Resolved"

    }
    return render(request, 'issue_details.html', context)



def additional_fee(request, id):
    global notif_viewers
    if request.method == "POST":
        total_amount = float(request.POST.get('totalAmount', 0.00))
        months = int(request.POST['monthfee'])
        consumer_id = ConsumerInfo.objects.get(consumer_id=id)
        fee_names = request.POST['additionalfee_names']
        addFee = AdditionalFees()
        addFee.fee_name = fee_names
        addFee.remainder = total_amount%months
        addFee.amount = (total_amount-addFee.remainder)/months
        addFee.months = months
        addFee.consumer_id = consumer_id
        tran = Transactions()
        tran.acctID = consumer_id
        tran.date = date.today()
        tran.month = date.today().month
        tran.year = date.today().year
        tran.transType = 'Additional Fees'
        tran.processedBy = request.user
        tran.bill = addFee.amount
        tran.save()
        addFee.current_tran = tran.transactionid
        addFee.save()
        consumer_id.current_bal += addFee.amount
        consumer_id.save()


    return redirect(request.META.get('HTTP_REFERER', '/'))

def submit_comment(request, id):
    global notif_viewers
    hotissue = Issues.objects.get(issueid=id)

    if request.method == 'POST':
        message = request.POST.get('message')

        mc = Messages()
        mc.message = message
        mc.from_user = request.user

        if hotissue.issued_by == request.user:
            last_message = Messages.objects.filter(issue_id=hotissue).order_by('-message_id').first()
            if last_message:
                mc.to_user = last_message.from_user
        else:
            mc.to_user = hotissue.issued_by

        mc.issue_id = hotissue
        mc.save()

    return redirect(request.META.get('HTTP_REFERER', '/'))


def resolve_issue(request):
    global notif_viewers
    if request.method == 'POST':
        id = request.POST.get('id')
        issue = Issues.objects.get(issueid=id)
        tran = issue.transactionid
        tran.delete()
        issue.delete()
        return redirect('issues')
