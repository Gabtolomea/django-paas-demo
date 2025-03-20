

import calendar
import math
from django.core.exceptions import *
import datetime
from .dataporter import *
from .decorators import *
from .forms import *
from .functions import * 
from .tasks import * #added K. Bandajon 26_10_24 ID: Penalty123
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
    sys_info = SystemInfo.objects.all()
    if sys_info:
        sys_info = sys_info[0]
    else:
        sys_info = SystemInfo()
        sys_info.save()

    
    # !!!please ask previous developers before attempting to uncomment!!!
    # portfromcsv()
    sxz()
    # pay_saall()
    # enye_cons()
    # enye_bars()
    camelize()
    set_first_tran()
    # set_months_unpaid()
    if datetime.now().month != sys_info.current_month:
        set_currentreadings()
        add_additionalFees()
        sys_info.current_month = datetime.now().month
        sys_info.current_year = datetime.now().year
        sys_info.save()
    #     set_overdue_months()
    #     remove_duplicate_od_months()
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
    # add_additionalFees()
    # del_addfees()
    # unexcempt_account('1454')
    # balance()
    # get_consumers_yearly()
    # billing_errors_to_csv()
    # fix_billing_errors()
    # adjust_excess_only()
    # set_date_all_transactions()
    # set_prev_reading_all()
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

    is_issues = get_is_seen_issues(request)
    context = {
        'search': search,
        'last': range(paginator.num_pages - 3, paginator.num_pages),
        'five': range(1, 6),
        'paginate_by': paginate_by,
        'count':count,
        'bills_list': bills_list,
        'user': user,
        'hipos':hipos,
        'is_issues' : is_issues
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
    is_issues = get_is_seen_issues(request)
    context = {
        'form': form,
        'user': request.user,
        'is_issues':is_issues
    }
    return render(request, 'registration.html', context)

@login_required(login_url='login')
def ledger(request, id):
    disp = request.GET.get('show','')
    template = ""
    LoginSession = request.user
    if LoginSession:
        if LoginSession.is_teller or LoginSession.is_supervisor:
            template = "ledger.html"
        else:
            template = redirect('bills_list')
            return template
    unpaid = []
    table = []
    unpaid = []
    year = datetime.today().year
    usage = 0
    transid = 0
    connectionType = 0
    pre = 0
    cur = 0
    pen = 0
    bill = 0
    total_unpaid_amount = 0
    paytranid = 0 # added for payment transaction id  Enjambre 21/11/2024
    payment = 0  #  added for payment 21/11/2024
    monthnames = ['January','February','March','April','May','June','July','August','September','October','November','December']
    # get_balance(id)
    class ledgerclass():
        def __init__(self, transid, date, prev, reading, usage, bill, payment, paytranid,  pb, ornum, bal, rateid, style, disc_code, transtype, month, year, ispaid):#added paytranid Enjambre 21/11/2024
            self.transid = transid
            self.date = date
            self.prev = prev
            self.reading = reading
            self.usage = usage
            self.bill = bill
            self.payment = payment
            self.paytranid= paytranid
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

        def __str__(self) -> str:
            return self.transtype
    try:
        u = ConsumerInfo.objects.get(pk=id)
    except ObjectDoesNotExist:
        pass
    if disp == '':
        trans = Transactions.objects.filter(acctID=u.consumer_id, is_issue=False)
    else:
        trans = Transactions.objects.filter(acctID=u.consumer_id, transType = disp, is_issue=False)
    asc_trans = trans.order_by('year', 'month','transactionid')
    bal = 0
    
    currentaddfeecount = 1
    for tran in asc_trans:
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
        paytranid= ''# added for payment transaction id  Enjambre 21/11/2024


        if tran.transType == 'Payment':
            paytranid = tran.transactionid
            payment = tran.payment
            continue # added zel 26/11/2024

        # print(tran.transType)

        if tran.transType == 'Billing':
            usage = tran.usage
            pre = tran.meterReading - usage
            bill = tran.bill
            try:
                connectionType = ConsumerType.objects.get(contypeid=tran.contypeid).contype
            except ObjectDoesNotExist:
                pass
            cur = tran.meterReading
            prev = tran.prevReading
            if tran.processedBy is not None:
                pb = tran.processedBy
            bal += bill

            try:# starting point zel 26/11/2024
                paymentTrans = Transactions.objects.filter(
                    acctID=u.consumer_id,
                    transType='Payment',
                    month=tran.month,
                    year=tran.year
                ).first()  

                if paymentTrans:
                    paytranid = paymentTrans.transactionid  # Assign the payment transaction ID
                    payment = paymentTrans.payment  # Get the payment amount
            except ObjectDoesNotExist:
                paytranid = None
                payment = 0 #until here zel 26/11/2024


            if tran.is_billpaid:
                ispaid = 'Paid'
               

        #elif tran.transType == 'Payment':
            #style = 'table-orange' #ORIGINAL
            #ornum = tran.or_number
            #if tran.processedBy:
                #pb = tran.processedBy
            #else:
                #pb = ''
            #bal = bal-tran.payment
            #try:
                #discount = Transactions.objects.get(transactionid=tran.discountcode)
               # dcode = discount.discountcode
            #except ObjectDoesNotExist:
                #pass
        elif tran.transType == 'Penalty':
            bill = tran.bill
            pen = tran.penaltyCode
            style = 'table-red'
            pb = tran.processedBy
            bal += bill

        elif tran.transType == 'Discount':
            style = 'table-blue'
            pb = tran.processedBy
            bal = bal-tran.payment

        elif tran.transType == 'Reset Meter':
            bill = 0
            cur = tran.meterReading
            style = 'table-yellow'
            pb = tran.processedBy
            bal += bill
        elif tran.transType == 'Additional Fees':
            bill = tran.bill
            style = 'table-lightblue'
            bal += bill
            if tran.processedBy is not None:
                pb = tran.processedBy
            
            if tran.is_billpaid:
                ispaid = 'Paid'
            else:
                try:
                    # print(tran.transactionid)
                    addfee = AdditionalFees.objects.get(transactions=tran.transactionid)
                    ispaid = f'{currentaddfeecount}/{addfee.months}'
                except ObjectDoesNotExist:
                    pass
            
            currentaddfeecount += 1
        
    
        date = tran.date
        #payment = tran.payment removed 26/11/2024
        transid = tran.transactionid
        m = tran.month
        y = tran.year
        bal = math.ceil(bal * 100) / 100
        ttype = tran.transType

        #if tran.transType == 'Payment':  # We already skip this above, but let's be explicit here too
            #continue #zel 26/11/2024


        if tran.transType != 'Received Amount' and tran.transType != 'Payment':  # added tran.transType != 'Payment'  20/11/2024   
            new_row = ledgerclass(transid, date, prev, cur, usage, bill, payment, paytranid, pb, ornum, bal, connectionType, style, dcode, ttype, monthnames[m-1], y, ispaid) #paytranid is added  21/11/2024           
            table.append(new_row)
        

        if tran.transType == 'Billing' and not tran.is_billpaid:
            unpaid_month = monthnames[tran.month-1]
            unpaid_year = tran.year
            unpaid_amount = tran.bill
            usage = tran.usage
            unpaid_bill_info = {
                'month': unpaid_month,
                'year': unpaid_year,
                'amount': unpaid_amount,
                'usage' : usage
                }
            unpaid.append(unpaid_bill_info)
        total_unpaid_amount = sum(unpaid_bill_info['amount'] for unpaid_bill_info in unpaid)

        #if tran.transType == 'Billing' and not tran.is_billpaid:
        #        unpaid_month = monthnames[tran.month-1]
        #        unpaid_year = tran.year
        #        unpaid_amount = tran.bill
        #        usage = tran.usage
        #        unpaid_bill_info = {
        #            'month': unpaid_month,
        #            'year': unpaid_year,
        #            'amount': unpaid_amount,
        #            'usage' : usage
        #            }
        #        unpaid.append(unpaid_bill_info)
        #total_unpaid_amount = sum(unpaid_bill_info['amount'] for unpaid_bill_info in unpaid)

    #gbaguia 08/16/2024
    ispaid = False
    is_issues = get_is_seen_issues(request)

    context = {
        'disp': disp,
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
        'prevmonth': calendar.month_name[(datetime.today().month - 2) % 12 + 1],
        'ispaid': ispaid,
        'is_issues': is_issues,
        'up': unpaid,
        'tu': total_unpaid_amount
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

def undodelete(request):
    if request.method == 'POST':
        id = request.POST['id']
        con = ConsumerInfo.objects.get(consumer_id=id)
        con.deleteflag = False
        con.save()
    return redirect(request.META.get('HTTP_REFERER', '/'))

@login_required(login_url='login')
def meterreading(request):
    
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

    is_issues = get_is_seen_issues(request)
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
        'is_issues' : is_issues 
        
    }
    return render(request, 'meterreading.html', context)

@login_required(login_url='login')
def deletereading(request, id):
    reading = Transactions.objects.get(transactionid = id)
    consumer = ConsumerInfo.objects.get(consumer_id=reading.acctID_id)
    try:
        latest_reset = Transactions.objects.filter(acctID=consumer.consumer_id, transType='Reset Meter').order_by('-year', '-month')[0]
    except IndexError:
        latest_reset = None
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
    latesttrans = Transactions.objects.filter(acctID=con.consumer_id, transType = "Billing").order_by('-year', '-month')[0]
    con.current_reading = latesttrans.meterReading
    if latest_reset is not None:
        if latest_reset.month == reading.month and latest_reset.year == reading.year:
            con.current_reading = latest_reset.meterReading
    con.save()
    reading.delete()
    return redirect('inputreading', con.consumer_id, date.today().year)

@login_required(login_url='login')
def inputreading(request, id, year):
    table = []
    years = []
    class meterreaderclass():
        def __init__(self, transid, month, monthval, usage, prev, reading, next, style, is_issue):
            self.transid = transid
            self.month = month
            self.usage = usage
            self.prev = prev
            self.reading = reading
            self.next = next
            self.style = style
            self.monthval = monthval
            self.is_issue = is_issue
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
    alltrans = Transactions.objects.filter(acctID=consumer.consumer_id, transType='Billing') | Transactions.objects.filter(acctID=consumer.consumer_id, transType='Reset Meter')
    # print([i.transType for i in alltrans])
    trans = alltrans.filter(year=year)
    brec = BarangayRecord.objects.all().order_by('-year')
    try:
        latest_reset = alltrans.filter(transType='Reset Meter').order_by('-year', '-month')[0]
    except IndexError:
        latest_reset = None
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
            m = meterreaderclass(transid, month, i, '', lastreading, '', '', '', False)
            table.append(m)
    else:
        for i in range(1, 13):
            try:
                bill = Transactions.objects.get(acctID=consumer.consumer_id, transType='Billing', year=year, month=i)
                lastreading = bill.prevReading
                cur_reading = int(bill.meterReading)
                usage = bill.usage
                style = 'table-success'
                for y in years_forward:
                    for x in range(i, 13):
                        try:
                            next_bill = Transactions.objects.get(acctID=consumer.consumer_id, transType='Billing', year=y, month=x)
                            next_reading = next_bill.meterReading
                            break
                        except ObjectDoesNotExist:
                            pass
                    if next_reading:
                        break
                m = meterreaderclass(bill.transactionid, calendar.month_name[i], i, usage, lastreading, cur_reading, next_reading, style, False)
            except ObjectDoesNotExist:
                for y in years_backward:
                    for x in range(i, 0, -1):
                        try:
                            prev_bill = Transactions.objects.get(acctID=consumer.consumer_id, transType='Billing', year=y, month=x)
                            lastreading = prev_bill.meterReading
                            break
                        except ObjectDoesNotExist:
                            pass
                    if lastreading:
                        break
                if latest_reset is not None:
                    if latest_reset.month == i and latest_reset.year == year:
                        lastreading = latest_reset.meterReading
                lastid+=1
                transid = lastid
                month = calendar.month_name[i]
                m = meterreaderclass(transid, month, i, '', lastreading, '', '', '', False)
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
        # if excempted
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
                                prev = Transactions.objects.filter(acctID=consumer.consumer_id, transType__in=['Billing','Reset Meter'], year=y, month=x).order_by('-transactionid')[0]
                                lastreading = prev.meterReading
                                has_prev = True
                                break
                            except ObjectDoesNotExist:
                                pass
                        if has_prev:
                            break
                        mm = 12
                tran.usage = r - lastreading
                tran.meterReading = r
                tran.bill = 0
                tran.processedBy = request.user
                tran.date = datetime.today()
                tran.save()
                
            except:
                usage = r - consumer.current_reading
                tran = Transactions()
                tran.transType = 'Billing'
                tran.date = datetime.today()
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
        # not excempted
        else:
            if consumer.penaltycounter >= con_penalty.penalty_after and con_penalty.penalty_rate != 0:
                xy = con_penalty.penalty_rate * cummulative
                interest = xy/100
            
            # transaction exists
                
            try:
                print(year)
                billtran = Transactions.objects.get(acctID=consumer.consumer_id, transType='Billing', year=year, month=d)
                print(billtran)
                lastreading = billtran.prevReading

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
                                lastreading = prev.meterReading
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
                billtran.prevReading = lastreading
                billtran.usage = r - lastreading
                usage = billtran.usage
                rate = ConsumerType.objects.get(contypeid=billtran.contypeid)
                dif = billtran.bill
                
                #kbandajon 09262024
                #addition of new rates
                year = billtran.year
                month = billtran.month
                usage = billtran.usage
                #bill_computer = BillComputer()
                billtran.bill = bill_compute(year, month, usage, rate)
                #kbandajon 09262024
                #addition of new rates


                billtran.processedBy = str(request.user)
                billtran.save()
                # add the excess here <

                excessLog(year, month, id)
                
                #>

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
                        # consumer.excess = consumer.excess - dif
                        consumer.current_bal = consumer.current_bal - dif
                    paymentT.save()
                    consumer.save()
                    billtran.is_billpaid = True
                    billtran.save()
                except ObjectDoesNotExist:
                    pass


            except MultipleObjectsReturned:
                duplicates = Transactions.objects.filter(acctID=consumer.consumer_id, transType='Billing', year=year, month=d).order_by('-transactionid')
                duplicates[0].delete()
                
            # transaction does not exist
            except ObjectDoesNotExist:
                # finding next billing
                fm = d+1
                has_next = False
                for y in years_forward:
                    for x in range(fm, 13):
                        try:
                            next = Transactions.objects.get(acctID=consumer.consumer_id, transType='Billing', year=y, month=x)
                        except MultipleObjectsReturned:
                            duplicates = Transactions.objects.filter(acctID=consumer.consumer_id, transType='Billing', year=y, month=x).order_by('-transactionid')
                            duplicates[0].delete()
                        except ObjectDoesNotExist:
                            pass
                    if has_next:
                        break
                    fm = 1
                
                lastreading = last_reading(consumer.consumer_id, year, d)
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
                #added by K. Bandajon 09_23_2024 - 21-09_2024
                #This is the new rate implemented starting from October , 2024 and onwards
                rate = ConsumerType.objects.get(contypeid=billtran.contypeid)
                year = billtran.year
                month = billtran.month
                usage = billtran.usage
                #bc = BillComputer()
                #billtran.bill = bill_computer.bill_compute(year, month, usage, rate)
                billtran.bill = bill_compute(year,month, usage, rate)
                #added by K. Bandajon 09_23_2024 - 21-09_2024

                billtran.payment = 0
                billtran.processedBy = request.user
                billtran.save()

                # add the excess here <

                #>
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
            except MultipleObjectsReturned:
                duplicates = Transactions.objects.filter(acctID=consumer.consumer_id, transType='Billing', year=ye, month=mo).order_by('-transactionid')
                duplicates[0].delete()
            except ObjectDoesNotExist:
                pass

            # if consumer.excess > 0:
            #     unsettled = Transactions.objects.filter(acctID_id=consumer, transType="Billing", is_billpaid=False, is_issue=False).order_by('-year', '-month')
            #     if unsettled:
            #         for u in unsettled:
            #             if consumer.excess>=u.bill:
            #                 ex = consumer.excess - u.bill
            #                 pt = Transactions()
            #                 pt.acctID = consumer
            #                 pt.transType = "Payment"
            #                 pt.processedBy = request.user
            #                 pt.date = datetime.today()
            #                 pt.year = u.year
            #                 pt.month = u.month
            #                 pt.payment = u.bill
            #                 pt.save()
            #                 u.is_billpaid = True
            #                 u.save()
            #                 consumer.excess = ex
            #                 consumer.save()
            #             else:
            #                 consumer.save()
            #                 break

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
    
    is_issues = get_is_seen_issues(request)
    context = {
        'consumer': consumer,
        'table': table,
        'cur_year': year,
        'years': years,
        'user': request.user,
        'is_issues' : is_issues
        
    }
    return render(request, 'input-meter-reading.html', context)

@login_required(login_url='login')
def consumer_list(request):
    
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

    is_issues = get_is_seen_issues(request)
    context = {
        'search' :search,
        'last':range(paginator.num_pages - 3, paginator.num_pages),
        'five':range(1,6),
        'paginate_by': paginate_by,
        'count':count,
        'consumer_list': cons_list,
        'user': user,
        'is_issues' : is_issues
        
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

    is_issues = get_is_seen_issues(request)
    context = {
        'conid':id,
        'form': form,
        'errors': form.errors,
        'user': request.user,
        'create':True,
        'is_issues' : is_issues
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

    is_issues = get_is_seen_issues(request)

    context = {
        'pc':penaltyc,
        'conid':id,
        'isUpdate':True,
        'form': form,
        'user': request.user,
        'is_issues' : is_issues
        
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
            year = int(request.POST.get('year'))
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
            tran.year = year
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

    is_issues = get_is_seen_issues(request)

    context = {
        'search':search,
        'sys_list':sys_list,
        'last': range(paginator.num_pages - 3, paginator.num_pages),
        'five': range(1, 6),
        'paginate_by': paginate_by,
        'count': count,
        'table': table,
        'user': request.user,
        'is_issues' : is_issues
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
    
    is_issues = get_is_seen_issues(request)

    context = {
        'sys': sys,
        'form': form,
        'user': request.user,
        'is_issues' : is_issues
        
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
                #gbaguia 08/16/2024
                #DO NOT USE this FACILITY when making monthly payments
                #unsettled = Transactions.objects.filter(acctID_id=consumer, transType="Billing", is_billpaid=False, is_issue=False).order_by('year', 'month')
                '''if unsettled:
                    for i in unsettled:
                        if consumer.excess>=i.bill:
                            ex = consumer.excess - i.bill
                            pt = Transactions()
                            pt.acctID = consumer
                            pt.transType = "Payment"
                            pt.processedBy = request.user
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
                        '''
                aftrans = Transactions.objects.filter(transType="Additional Fees", acctID_id=consumer)
                
                for af in aftrans:
                    if not af.is_billpaid:
                        #changed 24_09_2024
                        try:
                            addfee = AdditionalFees.objects.get(transactions__transactionid=af.transactionid)
                        except:
                            pass
                        if consumer.excess>=af.bill:
                            ex = consumer.excess - af.bill
                            pt = Transactions()
                            pt.acctID = consumer
                            pt.transType = "Payment"
                            pt.processedBy = request.user
                            pt.date = datetime.today()
                            pt.year = af.year
                            pt.month = af.month
                            pt.payment = af.bill
                            amount -= af.bill
                            pt.save()
                            af.is_billpaid = True
                            af.save()
                            consumer.excess = ex
                            #print("hey, one")
                            #k. Bandajon 08_10_2024
                            # addfee object not available
                            try:
                                addfee.month_counter += 1 
                                addfee.save()
                            except:
                                pass
                        else:
                            break
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

        # added by Kathrina D. Bandajon || December 12, 2024 || ID : Excess098
        # added by Kathrina D. Bandajon || December 12, 2024 || ID : Partial123

        year = ted.year
        print(year)
        month = ted.month
        print(month)
        month_ted = Transactions.objects.filter(year=year, month=month, transType="Billing").first()
        print(month_ted)
        try:
            thismonth_bill = month_ted.bill
        except ObjectDoesNotExist as e:
            print(f"Error retrieving bill transaction: {e}")
        nowDate = datetime.now()

        # Excess Logic
        if amount > thismonth_bill:
            excess = amount - thismonth_bill
            con_bal = (con.current_bal - excess) * 1
            excess_save = ExcessLog(
                excessID = ted,
                accountID = con,
                year = year,
                month = month,
                excessamt = excess,
                dateAdded = nowDate,
                is_used = False
            )
            con.excess = excess
            con.current_bal = con_bal
            try:
                excess_save.save()
                con.save()
            except Exception as e:
                print(f"Error saving Excess transaction: {e}")

        # Partial Logic
        elif amount < thismonth_bill:
            partial = amount - thismonth_bill
            #partial = dif if dif >= 0 else dif * -1
            former_bill = thismonth_bill
            bill = thismonth_bill - partial
            transactionType = ted.transType
            to_update = Transactions.objects.filter(acctID=month_ted.acctID, month=month, year=year, transType=transactionType).update(previousBill=former_bill, bill=bill, is_billpaid=False)
            con.excess = 0
            con.current_bal += bill
            partialLog_save = PartialLog(
                partialID = ted,
                accntID = con,
                year = year,
                month = month,
                partialamt = partial,
                datepaid = nowDate,
            )
            try:
                partialLog_save.save()  # Corrected this line
                to_update.save()
                con.save()
            except Exception as e:
                print(f"Error saving Partial transaction: {e}")

        # No excess or partial: Update the transaction
        else:
            update_trans = Transactions.objects.filter(acctID=con, month=month, year=year, transType=transactionType).update(previousBill=thismonth_bill, is_billpaid=True)
            con_bal = con.current_bal - amount
            con.current_bal = con_bal
            con.save()
            try:
                # No need to call save() on `update_trans`, as `update()` directly saves the changes
                pass
            except Exception as e:
                print(f"Error saving None transaction: {e}")

        get_balance(ted.acctID.consumer_id)


        #original
        '''if con.excess < 0:
            con.current_bal += (con.excess*-1)
            con.excess = 0
            con.save()'''
        return redirect('payment_history', ted.acctID.consumer_id,ted.year)
    

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

    is_issues = get_is_seen_issues(request)
    context = {
        'br': br,
        'cur_year': year,
        'years': years,
        'fr': fr,
        'user': request.user,
        'is_br':True,
        'is_issues' : is_issues
        
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


    is_issues = get_is_seen_issues(request)

    context = {
        'bang': bang,
        'is_issues' : is_issues
        
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
    
    is_issues = get_is_seen_issues(request)

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
        'is_issues' : is_issues
        
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

    is_issues = get_is_seen_issues(request)

    context = {
        'my': my,
        'rev_col': rev_col,
        'rev_rec': filt,
        'cur_year': year,
        'years': years,
        'col': col,
        'rec': rec,
        'is_rr':True,
        'is_issues' : is_issues
        
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
    
    is_issues = get_is_seen_issues(request)

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
        'is_issues' : is_issues
        
   
     
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
    
    is_issues = get_is_seen_issues(request)

    context = {
        'uv': uv,
        'years': years,
        'current': year,
        'table': table, 
        'is_issues' : is_issues
        
    }
    return render(request, 'view_unsettled_bills.html', context)


def discount(request):
    
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
    
    is_issues = get_is_seen_issues(request)

    context = {
        'dc': dc,
        'user': user,
        'is_discount':True,
        'is_issues' : is_issues 
        
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
    
    cont = ConsumerType.objects.all().order_by
    form = ConscumertypecreationForm()
    contypecount = int(ConsumerType.objects.all().order_by('-contypeid')[0].contypeid.split('C')[::-1][0])
    if request.method == "POST":
        contype = request.POST['contype']
        minReading = request.POST['minReading']

        #added by K. Bandajon 19_09_24
        #maxReading = request.POST['maxReading']
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

        #added by K. Bandajon 19_09_24 (maxReading)
        #ct.maxReading = maxReading
        ct.minReadingCharge = minReadingCharge
        ct.rateAfterMin = rateAfterMin
        ct.added_by = request.user
        ct.date_added = date.today()
        ct.save()
        messages.success(request, 'Consumer Type has been added')
        return redirect('new_consumertype')

    is_issues = get_is_seen_issues(request)

    context = {
        'cont': cont,
        'form': form,
        'errors': form.errors,
        'user': request.user,
        'is_contype':True,
        'is_issues' : is_issues
        
    }
    return render(request, 'new_consumertype.html', context)

def editcontype(request, id):
    con = ConsumerType.objects.get(contypeid=id)
    if request.method == 'POST':
        contype = request.POST['contype']
        minReading = request.POST['minReading']        
        #maxReading = request.POST['maxReading'] #added by K. Bandajon 19_09_24
        minReadingCharge = request.POST['minReadingCharge']
        rateAfterMin = request.POST['rateAfterMin']
        
        con.contype = contype
        con.minReading = minReading
        #con.maxReading = maxReading #added by K. Bandajon 19_09_24
        con.minReadingCharge = minReadingCharge
        con.rateAfterMin = rateAfterMin
        con.save()
        messages.success(request, 'Code has been updated')
        
    return redirect('new_consumertype')


@login_required(login_url='login')
def penalty(request):
    
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
    
    is_issues = get_is_seen_issues(request)

    context = {
        'penalty': penalty,
        'form1': form,
        'errors': form.errors,
        'user': request.user,
        'is_penalty':True,
        'is_issues' : is_issues
        
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
                    #added by K. Bandajon 09_23_2024 - 21-09_2024
                    #This is the new rate implemented starting from October , 2024 and onwards
                    if t.month > 9 and t.year >=2024:
                        if  t.usage >= 1 and t.usage <= 5 :
                            t.bill = t.usage * 5
                        elif  t.usage >= 6 and t.usage <= 10 :
                            t.bill = ((t.usage - 5) * 6) + 25
                        elif t.usage >= 11 and t.usage <= 20:
                            t.bill = ((t.usage - 5) * 7) + 25
                        elif t.usage >= 21 and t.usage <= 35 :
                            t.bill = ((t.usage - 5) * 8) + 25
                        elif t.usage >= 36 and t.usage <= 50:
                            t.bill = ((t.usage - 5) * 9) + 25
                        elif t.usage >= 51:
                            t.bill = ((t.usage - 5) * 10) + 25
                    else:
                    #original
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
                                pt.processedBy = request.user
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

    is_issues = get_is_seen_issues(request)
    context= {
        'user':user,
        'role':role,
        'is_profile':True,
        'is_issues' : is_issues 
        
    }
    return render(request, 'viewprof.html', context)

@login_required(login_url='login')
def userprof(request):
    
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
    
    is_issues = get_is_seen_issues(request)

    context= {
        'user':user,
        'form':form,
        'is_issues' : is_issues
        
    }
    return render(request, 'userprof.html', context)

def monthly_summary (request, id, year):
    table = []
    years = []
    class montly_sum():
        #def __init__(self, month, monthval, reading, reading_date, usage, total_bill, prev_bal, additional_fees, total_due, payid):
        def __init__(self, month, monthval, reading, reading_date, usage, total_bill, prev_bal, additional_fees, total_due, total_amount_paid, payid, transType):
            self.month = month
            self.monthval = monthval
            self.reading = reading
            self.reading_date = reading_date
            self.usage = usage
            self.total_bill = total_bill
            self.prev_bal = prev_bal
            self.additional_fees = additional_fees
            self.total_due = total_due
            self.total_amount_paid = total_amount_paid
            self.payid = payid
            self.transType = transType  
            

    consumer = ConsumerInfo.objects.get(consumer_id=id)
    alltran = Transactions.objects.filter(acctID_id=id, transType='Billing', is_issue=False)
    

    for i in alltran:
        if i.year not in years:
            years.append(i.year)
    if datetime.today().year not in years:
        years.append(datetime.today().year)

    for i in range(1, 13):
        month = calendar.month_name[i]
        try:
            bill = Transactions.objects.get(acctID_id=id, transType='Billing', year=year, month=i, is_issue=False)
            transtype = bill.transType
        except ObjectDoesNotExist:
            #gbaguia 09112024 Added total_amount_paid container
            # a = montly_sum(month, i, 0, '', 0, 0, 0,0, 0, 0)
            a = montly_sum(month, i, 0, '', 0, 0, 0, 0, 0, 0, 0, transtype)
            table.append(a)
            continue
        usage = bill.usage
        reading = bill.meterReading
        reading_date = bill.date
        total_bill = bill.bill
        prev_bal = 0
        additional_fees = 0  # zel added 26/11/2024
        try:
            add_fee = Transactions.objects.get(acctID_id=id, transType='Additional Fees', year=year, month=i, is_issue=False)
            additional_fees = add_fee.bill
            #addfee_transType = add_fee.transType #zel 26/11/2024
        except ObjectDoesNotExist:
            pass #zel added 26/11/2024
            
        total_due = total_bill + consumer.current_bal + additional_fees

        # gbaguia 08162024
        # if bill.is_billpaid:
        # let us check if a payment has been maid
        payid = 0
        total_amount_paid = 0

        if bill.is_billpaid:
            try:
                payments = Transactions.objects.filter(acctID_id=id, transType='Payment', year=year, month=i, is_issue=False)
                try:
                    payment = payments[0]
                    try:
                        add_fee = Transactions.objects.get(acctID_id=id, transType='Additional Fees', year=year, month=i, is_issue=False)
                        for p in payments:
                            if p.payment == add_fee.bill:
                                payment = p
                                break
                    except ObjectDoesNotExist:
                        pass

                    payid = payment.transactionid
                    total_amount_paid = payment.payment
                except IndexError:
                    total_amount_paid = 0
                    payid = 0
            except ObjectDoesNotExist:
                total_amount_paid = 0
                payid = 0 #zel added 26/11/2024
        
        

        #gbaguia 09112024
        #a = montly_sum(month, i, reading, reading_date, usage, total_bill, prev_bal, additional_fees,total_due, payid)
        a = montly_sum(month, i, reading, reading_date, usage, total_bill, prev_bal, additional_fees, total_due, total_amount_paid, payid, transtype) 
        table.append(a)

        

        if additional_fees > 0: #Enjambre  trial section added for additional fees 22/11/2024
            add_fee_paid = False
            try:
                fee_payment = Transactions.objects.get(acctID_id=id, transType='Payment', year=year, month=i, is_issue=False)
                add_fee_paid = fee_payment.payment == additional_fees #zel added 29/11/2024

                if add_fee_paid:
                    total_amount_paid = fee_payment.payment
                    payid = fee_payment.transactionid
                else:
                    total_amount_paid = 0
                    payid = 0
            except ObjectDoesNotExist:
                add_fee_paid = False
                total_amount_paid = 0
                payid = 0
                additional_fee = Transactions.objects.filter(acctID_id=id, transType='Additional Fees', year=year, month=i).first()
                #total_bill = additional_fee.bill

                if additional_fee:
                    total_bill = additional_fee.bill
                else:
                    total_bill = additional_fees

            # Add additional fee row to the table
                a_additional_fee = montly_sum(month, i, 0, '', 0, total_bill, 0, additional_fees, total_due, total_amount_paid, payid, 'Additional Fee')
                table.append(a_additional_fee)

    
    is_issues = get_is_seen_issues(request)

    context = {
        'table': table,
        'u': consumer,
        'year': year,
        'years': years,
        'is_issues': is_issues
    }
    return render(request, 'conmon_summary.html', context)




def monthlypayment(request):
    
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
            #gbaguia 08/16/2024
            #We must check the Billing if Paid or not
            #tr = Transactions.objects.get(acctID_id = conid, transType = "Payment", month = month, year = year)
            billtran = Transactions.objects.get(acctID_id = conid, transType = "Billing", month = month, year = year)
            #print(tr)

            if not billtran.is_billpaid:
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
                    #add_excess extraction here
                    #Excess Extraction || ID: ExcessKB || Added by: Kathrina Bandajon December 2, 2024
                    #Excess
                    '''if payment > billtran.bill:
                        rcvdamt = Transactions.objects.filter(month=month, year=year, acctID=id, transType='Received Amount').first()
                        paymentAmt = rcvdamt.receivedamt
                        bill = billtran.bill
                        excessamount = paymentAmt - bill

                        excess_logs = ExcessLog(
                            year = month,
                            month = year,
                            accountID = id,
                            excessamt = excessamount,
                            excessID = rcvdamt.transactionid
                        )
                        excess_logs.save()

                        #original
                        billtran.is_billpaid = True
                        billtran.save()
                    #Partial
                    elif payment < billtran.bill:
                        billtran.previousBill = billtran.bill
                        billtran.bill = billtran.bill - payment
                        billtran.save()
                    else:
                    #add_excess extraction here
                    #Excess Extraction || ID: ExcessKB || Added by: Kathrina Bandajon December 2, 2024
                        billtran.is_billpaid = True
                        billtran.save()
                        '''
                except ObjectDoesNotExist:
                    pass

                # trial section for additional fee 10/12/2024 Enjambre
                try:
                    add_fee = Transactions.objects.get(acctID_id=conid, transType='Additional Fees', year=year, month=month, is_issue=False)
                except ObjectDoesNotExist:
                    add_fee = None

                if add_fee:
                    if payment >= add_fee.bill:
                        add_fee.is_billpaid = True
                        add_fee.save()
                        excessamount = payment - add_fee.bill
                        if excessamount > 0:
                            excess_logs = ExcessLog(
                                year=month,
                                month=year,
                                accountID=conid,
                                excessamt=excessamount,
                                excessID=add_fee.transactionid
                            )
                            excess_logs.save()

                    else:
                        add_fee.previousBill = add_fee.bill
                        add_fee.bill -= payment
                        add_fee.save()

                #until here 10/12/2024
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

        except ObjectDoesNotExist:
            #gbaguia 08/16/2024
            #not billed yet
            pass
        
    return redirect('monthly_summary', id=conid, year=year)

def makepayment(conid, consumer, month, year, user, or_num, con_b_rec):
    paytran = Transactions()
    paytran.payment = payment
    paytran.date = date.today()
    paytran.acctID = consumer
    paytran.month = month
    paytran.year = year
    paytran.transType = "Payment"
    #paytran.processedBy = request.user
    paytran.processedBy = user
    paytran.save()
    recT = Transactions()
    recT.receivedamt = payment
    recT.date = date.today()
    recT.acctID = consumer
    recT.month = month
    recT.year = year
    recT.transType = "Received Amount"
    recT.processedBy = user
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
    

def payment_history (request, id, year):
    
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


    is_issues = get_is_seen_issues(request)

    context = {
        'u' : consumer,
        'alltrans' : alltran,
        'years'    : years,
        'year'     : year,
        'is_issues' : is_issues
        
    }

    return render(request,'payment_history.html', context)

def mark_unpaid (request, id): # Enjambre & Sobrian 26/11/2024 for unpaid in payment history trial
    if request.method =="POST":
        #transaction_id = request.POST.get ('transaction_id')
        consumer_id = request.POST.get ('consumer_id')
        #monthval = request.POST.get('month') #added
       # year = request.POST.get('year')  #added
        #payment = request.POST.get('payment')  #added
        remarks = request.POST.get ('remarks')

        

        try:
            transaction =Transactions.objects.get(transactionid=id, acctID =consumer_id ) #, acctID_id=consumer_id
           

            transaction.is_billpaid = False
            transaction.remarks = remarks
            transaction.save()
            

            #messages.success(request,f"Transaction {transaction_id}marked as unpaid.")
            return redirect ('conmon_summary', id= consumer_id, year=transaction.year) #year=transaction.year
        
        except Transactions.DoesNotExist:
            #messages.error(request, "Transaction not found.")

            #print(f"Transaction with ID {transaction_id} not found.")

            #print(f"Transaction with ID {ransaction_id} not found.")

            #print(f"Transaction with ID {ransaction_id} not found.")

            return HttpResponse( "Transaction not found.", status =404)
        
    #return HttpResponse("Invalid request.", status=400)
    return redirect('payment_history', id = consumer_id) #  year=transaction.year  
    

def consumption(request, year):
    
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
    is_issues = get_is_seen_issues(request)

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
        'is_issues' : is_issues
    }
    return render(request,'consumption.html', context)


def exemptiont(request):
    
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




def add_issue(request, id, year):
    
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
        i.save()
        
        messages.error(request, 'Issue has been added.')

    return redirect(request.META.get('HTTP_REFERER', '/')) 


def issues_view(request):
    
    last_message = None
    try:
        for issue in issues:
            last_message = Messages.objects.filter(issue_id=issue).order_by('-time').first()
            if last_message:
                issue.last_comment = last_message.message
                issue.save()
    except NameError:
        pass

    is_issues = get_is_seen_issues(request)

    #paginate and search all issues code
    search = request.GET.get("search", "")
    page = request.GET.get('page')
    isnum = search.isnumeric()

    if isnum:
        issues = Issues.objects.filter(
            Q(transactionid__acctID__consumer_id__icontains=search) |
            Q(transactionid__acctID__meternumber__icontains=search)
        ).order_by('-date')
    else:
        issues = Issues.objects.filter(
            Q(issue__icontains=search)  |
            Q(transactionid__acctID__firstname__icontains=search) |
            Q(transactionid__acctID__middlename__icontains=search) |
            Q(transactionid__acctID__lastname__icontains=search)
        ).order_by('-date')

    pages = int(request.GET.get('p', 10))
    count = issues.count()
    if pages == 0:
        paginate_by = request.GET.get('paginate_by', count)
    else:
        paginate_by = request.GET.get('paginate_by', pages)
    
    paginator = Paginator(issues,paginate_by)
    
    try:
        issue_list = paginator.page(page)
    except PageNotAnInteger:
        issue_list = paginator.page(1)
    except EmptyPage:
        issue_list = paginator.page(paginator.num_pages)
           

    context = {
        'issue_list': issue_list,
        'is_issues' : is_issues,
        'last': range(paginator.num_pages - 3, paginator.num_pages),
        'five': range(1, 6),
        'paginate_by': paginate_by,
        'count':count,
        'last_message': last_message,
        'search' : search,
    }
    return render(request, 'issues.html', context)

def issue_details(request, id):
    
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

    is_issues = get_is_seen_issues(request)

    context = {
        
        'isdel': issue,
        'con': con,
        'tran': tran,
        'monthval': monthval,
        'comments': comments,
        'is_issues' : is_issues
    }
    return render(request, 'issue_details.html', context)



def additional_fee(request, id):
    
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
        addFee.save()
        addFee.transactions.add(tran)
        addFee.save()
        consumer_id.current_bal += addFee.amount
        consumer_id.save()


    return redirect(request.META.get('HTTP_REFERER', '/'))

def submit_comment(request, id):
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
            mc.to_user = SystemUsers.objects.get(username = hotissue.issued_by)

        mc.issue_id = hotissue
        mc.save()

    return redirect(request.META.get('HTTP_REFERER', '/'))

def resolve_issue(request):
    
    if request.method == 'POST':
        id = request.POST.get('id')
        issue = Issues.objects.get(issueid=id)
        tran = issue.transactionid
        consumer = ConsumerInfo.objects.get(consumer_id=tran.acctID_id)
        alltrans = Transactions.objects.filter(acctID_id=consumer.consumer_id ).order_by('-year', '-month')
        try:
            index_of_tran = list(alltrans).index(tran)
            
            # Get the transaction after `tran`
            if index_of_tran < len(alltrans) - 1:
                prev_tran = alltrans[index_of_tran + 1]
                # Now, `prev_tran` contains the transaction after `tran`
            else:
                # `tran` is the last transaction in the queryset, so there is no transaction after it
                prev_tran = None
        except ValueError:
            # `tran` was not found in the queryset
            prev_tran = None
        if prev_tran:
            consumer.current_reading = prev_tran.meterReading

        
        tran.delete()
        issue.delete()
        return redirect('issues')



def get_is_seen_issues(request):
    user = request.user
    
   
    is_supervisor = user.is_supervisor 
    if is_supervisor:
        issues = Issues.objects.filter(status__in=['Pending'])
    else:
        issues = Issues.objects.filter(issued_by=user.username)
    
    is_issues = issues.exists()
    
    
    return is_issues


#added by K. Bandajon October 29, 2024 The new penalty rate-.- ID: NewPenaltyOct2024
def new_penalty(request):
    #schedule_monthlyTask()
    return HttpResponse("Task is Ongoing")


#added by Kathrina D. Bandajon November 26, 2024
from datetime import datetime
from django.shortcuts import render
from .models import ConsumerInfo, Transactions, Barangays

@login_required(login_url='login')
def allPaid(request): 
    disp = request.GET.get('show', '')
    filter_by = request.GET.get('p', 'all') 
    selected_year = request.GET.get('fyear', str(datetime.year))
    selected_month = request.GET.get('fmonth', str(datetime.month))
    paidtable = []

    current_date = datetime.today()
    current_year = current_date.year
    years = []

    monthnames = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']

    allConsumer = ConsumerInfo.objects.all()
    allBarangays = Barangays.objects.all()

    yer = Transactions.objects.filter(acctID_id=id, transType='Received Amount', is_issue=False)

    for i in yer:
        if i.year not in years:
            years.append(i.year)
    if datetime.today().year not in years:
        years.append(datetime.today().year)
    if int(year) in years:
        years.remove(int(year)) 

    class allwhoPaid:
        def __init__(self, name, consumerid, transactionid, date, month, year, payment, processedby, brgy):
            self.name = name
            self.consumerid = consumerid
            self.transactionid = transactionid
            self.date = date
            self.month = month
            self.year = year
            self.payment = payment  # Amount paid
            self.processedby = processedby
            self.brgy = brgy

    for consumer in allConsumer:
        consumerid = consumer.consumer_id
        name = consumer.firstname + " " + consumer.lastname
        inst_add = consumer.installation_address

        if filter_by == 'all':
            thisConsumerPaid = Transactions.objects.filter(
                acctID=consumerid,
                transType="Payment",
            )
        elif filter_by == 'barangay':
            barangay = request.GET.get('barangay', '')  # Get the selected barangay from the request
            thisConsumerPaid = Transactions.objects.filter(
                acctID=consumerid,
                transType="Payment",
                barangay__name__icontains=barangay  # Assuming Barangay has a 'name' field
            )
        else:
            thisConsumerPaid = Transactions.objects.filter(
                acctID=consumerid,
                transType="Payment"
            )
        for paid in thisConsumerPaid:
            transactionid = paid.transactionid
            date = paid.date
            month = paid.month
            year = paid.year
            payment = paid.payment
            processedby = paid.processedBy
            row = allwhoPaid(name, consumerid, transactionid, date, month, year, payment, processedby, inst_add)
            paidtable.append(row)

    is_issues = get_is_seen_issues(request)

    context = {
        'disp': disp,
        'month': monthnames[current_date.month-1],  # Current month name
        'date_today': current_date.strftime('%B %d, %Y - %I:%M %p'),  # Current date and time
        'paidtable': paidtable,  # Transactions data to be displayed
        'user': request.user,
        'is_issues': is_issues,
        'filter_by': filter_by,
        'selected_year': selected_year,
        'selected_month': selected_month,
        'current_year': current_year,
        'years': years,
        'allBarangays': allBarangays,  # Add Barangays to the context
    }

    return render(request, 'allpaid.html', context)

#def unpaid_method(request):
    #if request.method == "POST":

def month_name_to_int(month_name):
    try:
        month = datetime.strptime(month_name, '%B').month
        return month
    except ValueError:
        # Handle invalid month name
        return None

@login_required(login_url='login')
#added KDB
def record_list(request):
    print("===== Entering record_list view =====")

    selected_year = request.GET.get('fyear', datetime.today().year)
    selected_brgy = request.GET.get('fbar', 1)
    selected_month = request.GET.get('fmonth', 'January')
    page = request.GET.get('page')

    print(f"Received GET params -> Year: {selected_year}, Barangay: {selected_brgy}, Month: {selected_month}, Page: {page}")

    try:
        selected_year = int(selected_year)
        selected_brgy = int(selected_brgy)
    except ValueError:
        print("Invalid year or barangay received")
        return render(request, 'recordList.html', {'error': 'Invalid year or barangay selected'})

    def month_name_to_int(month_name):
        try:
            return list(calendar.month_name).index(month_name)
        except ValueError:
            return 1  # Default to January if invalid

    month_number = month_name_to_int(selected_month)
    print(f"Converted month name '{selected_month}' to month number {month_number}")

    class RecordListClass:
        def __init__(self, consumer_id, meternumber, name, paid_amount, date_paid, transtype, transID):
            self.consumer_id = consumer_id
            self.meternumber = meternumber
            self.name = name
            self.paid_amount = paid_amount
            self.date_paid = date_paid
            self.transtype = transtype
            self.transID = transID

    # Fetch distinct years
    years = Transactions.objects.filter(transType='Received Amount', is_issue=False).values_list('year', flat=True).distinct()
    years = list(set(years))
    if datetime.today().year not in years:
        years.append(datetime.today().year)

    print(f"Available years: {years}")

    # Fetch distinct months
    months = Transactions.objects.filter(transType='Received Amount', is_issue=False).values_list('month', flat=True).distinct()
    months = sorted(set(months))
    month_names = [calendar.month_name[month] for month in months]
    print(f"Available months: {month_names}")

    # Fetch Barangays
    bars = Barangays.objects.all()
    print(f"Total Barangays found: {bars.count()}")

    # Fetch ConsumerInfo records based on Barangay filter
    reclist = []

    barangay = Barangays.objects.get(id=selected_brgy)

    try:
        conlistofBarangay = ConsumerInfo.objects.filter(installation_address=selected_brgy)
        print(f"Found {conlistofBarangay.count()} consumers for Barangay {selected_brgy}")

        for consumer in conlistofBarangay:
            meternumber = consumer.meternumber
            consumer_id = consumer.consumer_id
            fname = consumer.firstname
            lname = consumer.lastname if hasattr(consumer, 'lastname') else ""

            name = f"{lname} {fname}".strip()  
            print(f"Processing consumer: {consumer_id}, Name: {name}, Meter: {meternumber}")

            rec = Transactions.objects.filter(
                year=selected_year, acctID=consumer_id, month=month_number, transType="Received Amount"
            ).first()

            if rec:
                print(f"Transaction found for {consumer_id} -> Amount: {rec.receivedamt}, Date: {rec.date}, ID: {rec.transactionid}")
                reclist.append(RecordListClass(consumer_id, meternumber, name, rec.receivedamt, rec.date, rec.transType, rec.transactionid))
            else:
                print(f"No transaction found for {consumer_id}")

    except Exception as e:
        print(f"Error processing transactions: {str(e)}")

    print(f"Total records collected: {len(reclist)}")

    # Pagination
    paginate_bypages = int(request.GET.get('p', 10))  # Default to 10 if not provided
    try:
        paginate_by = int(request.GET.get('paginate_by', paginate_bypages))  # Convert to int
    except ValueError:
        paginate_by = 10  # Default to 10 if conversion fails

    print(f"Paginate by: {paginate_by}")

    paginator = Paginator(reclist, paginate_by)

    try:
        page = int(page) if page else 1  # Convert page to integer
        record_list = paginator.page(page)
    except ValueError:
        print("Invalid page number, defaulting to page 1")
        record_list = paginator.page(1)
    except PageNotAnInteger:
        print("Page is not an integer, defaulting to page 1")
        record_list = paginator.page(1)
    except EmptyPage:
        print("Page is empty, showing last page")
        record_list = paginator.page(paginator.num_pages)

    print("===== Rendering Template =====")

    context = {
        'last': range(paginator.num_pages - 3, paginator.num_pages),
        'five': range(1, 6),
        'paginate_by': paginate_by,
        'month_names': month_names,
        'months': months,
        'years': years,
        'selected_year': selected_year,
        'selected_month': selected_month,
        'selected_brgy': selected_brgy,
        'barangay' : barangay,
        'bars': bars,
        'count': len(reclist),
        'record_list': record_list,
        'user': request.user,
    }

    return render(request, 'recordList.html', context)

'''@login_required(login_url='login')
#added KDB_17_03_2025
def monthly_collections(request, year):
    selected_year = request.GET.get('fyear', datetime.today().year)
    class MonthlyCollection:
        def __init__(self, month, collection, transTotal):
            self.month = month
            self.collection = collection
            self.transTotal = transTotal

    # Fetch distinct years
    years = Transactions.objects.filter(transType='Received Amount', is_issue=False).values_list('year', flat=True).distinct()
    years = list(set(years))
    if datetime.today().year not in years:
        years.append(datetime.today().year)

    # Fetch distinct months
    months = Transactions.objects.filter(transType='Received Amount', is_issue=False).values_list('month', flat=True).distinct()
    months = sorted(set(months))
    month_names = [calendar.month_name[month] for month in months]
    print(f"Available months: {month_names}")

    print(f"Available years: {years}")

    col_monthly = []
    for month in months:
        monthly_trans = Transactions.objects.filter(
            transType='Received Amount',
            date__year=selected_year,  # Extract year from date field
            date__month=month  # Extract month from date field
        ).aggregate(total_amount=Sum('receivedamt'))

        num_of_trans = monthly_trans.count()

        # Ensure None values are replaced with 0
        amount_col = monthly_trans['total_amount'] or 0  
        col_monthly.append(amount_col)
        table = MonthlyCollection.append(month, amount_col, num_of_trans)

    context = {
        #'table': table,
        'years': years,
    }
    
    return render(request, 'monthly_collection.html', context)'''



@login_required(login_url='login')
def monthly_collections(request, year=None):
    if year is None:  # Use the current year if no year is provided
        year = datetime.today().year
    else:
        year = int(year)  # Convert to integer

    selected_year = int(request.GET.get('fyear', year))  # Allow selection from GET

    class MonthlyCollection:
        def __init__(self, month, collection, transTotal):
            self.month_col = calendar.month_name[month]  # Convert month number to name
            self.all_payments = collection
            self.number_of_transactions = transTotal

    # Fetch distinct years
    years = Transactions.objects.filter(
        transType='Received Amount', is_issue=False
    ).dates('date', 'year').values_list('year', flat=True)

    years = list(set(years))  # Ensure uniqueness
    if datetime.today().year not in years:
        years.append(datetime.today().year)

    # Fetch distinct months
    months = Transactions.objects.filter(
        transType='Received Amount', is_issue=False,
        date__year=selected_year  # Filter months based on selected year
    ).dates('date', 'month').values_list('month', flat=True)

    months = sorted(set(months))

    table = []  # List to store data for the table

    for month in months:
        monthly_trans = Transactions.objects.filter(
            transType='Received Amount',
            date__year=selected_year,
            date__month=month
        ).aggregate(total_amount=Sum('receivedamt'))

        num_of_trans = Transactions.objects.filter(
            transType='Received Amount',
            date__year=selected_year,
            date__month=month
        ).count()

        amount_col = monthly_trans['total_amount'] or 0
        table.append(MonthlyCollection(month, amount_col, num_of_trans))

    context = {
        'table': table,
        'years': years,
        'is_mc': True,
        'cur_year': selected_year,
    }

    return render(request, 'monthly_collection.html', context)



def calculate_month_bounds(year):
    month_bounds = {}
    for month in range(1, 13):  # Loop over all months from 1 to 12
        start = date(year, month, 1)
        max_days_in_month = calendar.monthrange(year, month)[1]
        end = date(year, month, max_days_in_month)
        
        month_bounds[calendar.month_name[month]] = (start, end)

    return month_bounds

#added by Kathrina 20/03/2025
'''@login_required(login_url='login')
def gen_sheets_monthlyrec(request):
    years = list(range(2019, datetime.now().year + 1))  
    month_names = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]

    # Get filter values from the request
    start_month = request.GET.get("start_month")
    start_year = request.GET.get("start_year")
    end_month = request.GET.get("end_month")
    end_year = request.GET.get("end_year")

    # Convert to date format
    if start_month and start_year:
        start_date = datetime.strptime(f"1 {start_month} {start_year}", "%d %B %Y")
    else:
        start_date = None

    if end_month and end_year:
        end_date = datetime.strptime(f"1 {end_month} {end_year}", "%d %B %Y")
    else:
        end_date = None

    # Query database based on filter values
    records = ConsumerInfo.objects.all()
    for record in records:
        id = record.consumer_id
        all_bills = Transactions.objects.filter(acctID=id, transType = 'Billing')
        for bill in all_bills:
            if bill.month >= start_month and bill.year >= start_year and bill.month <= end_month and bill.year <= end_year:
                #append transaction in consumer class
        
        


    context = {
        "years": years,
        "month_names": month_names,
        "selected_start_month": start_month,
        "selected_start_year": start_year,
        "selected_end_month": end_month,
        "selected_end_year": end_year,
        "records": records,  # Filtered records
    }

    return render(request, 'billreportcopy.html', context)'''

from collections import defaultdict
import calendar
from datetime import datetime
import openpyxl
from openpyxl.styles import Font
from django.shortcuts import render
from django.http import HttpResponse
from .models import ConsumerInfo, Transactions

def monthly_billing_report(request):
    # Get date range from request (or default values)
    start_month = int(request.GET.get("start_month", 4))  # Default: April
    start_year = int(request.GET.get("start_year", 2024))  # Default: 2024
    end_month = int(request.GET.get("end_month", 2))  # Default: February
    end_year = int(request.GET.get("end_year", 2025))  # Default: 2025

    # Dictionary to store data
    consumer_data = defaultdict(lambda: defaultdict(float))  # Use float to ensure decimal precision
    months_list = []

    # Fetch all consumer records
    records = ConsumerInfo.objects.all()

    for record in records:
        consumer_name = f"{record.lastname}, {record.firstname}".strip()  # Format: Last, First
        all_bills = Transactions.objects.filter(acctID=record.consumer_id, transType='Billing')

        for bill in all_bills:
            bill_date = datetime(bill.year, bill.month, 1)
            start_date = datetime(start_year, start_month, 1)
            end_date = datetime(end_year, end_month, 1)

            if start_date <= bill_date <= end_date:
                month_year = f"{calendar.month_abbr[bill.month]} - {str(bill.year)[-2:]}"  # "Apr - 24"
                
                # Ensure the bill amount is rounded to two decimal places
                consumer_data[consumer_name][month_year] += round(float(bill.bill or 0), 2)

                if month_year not in months_list:
                    months_list.append(month_year)

    # Sort months for correct order
    months_list.sort(key=lambda x: datetime.strptime(x, "%b - %y"))

    # Prepare data for HTML template (sorted alphabetically by last name)
    sorted_consumers = sorted(consumer_data.keys())  # Sort consumers by name
    table_data = [
        [consumer] + [f"₱{consumer_data[consumer].get(month, 0):,.2f}" for month in months_list]
        for consumer in sorted_consumers
    ]

    # Calculate totals
    total_row = ["Total"] + [f"₱{sum(consumer_data[c][month] for c in consumer_data):,.2f}" for month in months_list]

    # Check if user requested an Excel file
    if "export" in request.GET:
        return generate_excel(months_list, table_data, total_row)

    return render(request, "billreportcopy.html", {"months_list": months_list, "table_data": table_data, "total_row": total_row})

def generate_excel(months_list, table_data, total_row):
    """Generate and return an Excel file."""
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Billing Report"

    # Add headers
    header = ["Consumer Names"] + months_list
    ws.append(header)
    for col in range(1, len(header) + 1):
        ws.cell(row=1, column=col).font = Font(bold=True)

    # Add consumer data
    for row in table_data:
        ws.append([row[0]] + [float(row[i][1:].replace(",", "")) for i in range(1, len(row))])  # Convert ₱ back to number

    # Add total row
    ws.append([total_row[0]] + [float(total_row[i][1:].replace(",", "")) for i in range(1, len(total_row))])

    # Format as currency in Excel
    peso_format = '"₱"#,##0.00'  # Peso format for Excel
    for row in ws.iter_rows(min_row=2, min_col=2, max_col=len(months_list) + 1, max_row=ws.max_row):
        for cell in row:
            cell.number_format = peso_format

    # Prepare response
    response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response["Content-Disposition"] = 'attachment; filename="Billing_Report.xlsx"'
    wb.save(response)
    return response