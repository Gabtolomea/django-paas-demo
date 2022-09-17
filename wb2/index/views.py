
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
def lp(request):
    porter()
    return render(request, "home.html")

def signin(request):

def rearrange(var):
    arr = []
    mycursor.execute("SELECT count(*) FROM information_schema.columns WHERE TABLE_NAME = '"+var+"';")
    cols = mycursor.fetchone()[0]
    mycursor.execute("SELECT count(*) FROM "+var+";")
    rows = mycursor.fetchone()[0]
    for r in range(rows):
        inner = []
        for c in range(cols):
            inner.append(globals()[var][c][r])
        arr.append(inner)

    return arr

def porter_out(table):
    b_rec = BarangayRecord()
    for i in table:
        b_rec.barangay_val = i[0]
        b_rec.year = i[2]
        b_rec.total_due_jan = i[6]
        b_rec.total_paid_jan = i[7]
        b_rec.total_usage_jan = i[8]
        b_rec.total_due_feb = i[9]
        b_rec.total_paid_feb = i[10]
        b_rec.total_usage_feb = i[11]
        b_rec.total_due_mar = i[12]
        b_rec.total_paid_mar = i[13]
        b_rec.total_usage_mar = i[14]
        b_rec.total_due_apr = i[15]
        b_rec.total_paid_apr = i[16]
        b_rec.total_usage_apr = i[17]
        b_rec.total_due_may = i[18]
        b_rec.total_paid_may = i[19]
        b_rec.total_usage_may = i[20]
        b_rec.total_due_jun = i[21]
        b_rec.total_paid_jun = i[22]
        b_rec.total_usage_jun = i[23]
        b_rec.total_due_jul = i[24]
        b_rec.total_paid_jul = i[25]
        b_rec.total_usage_jul = i[26]
        b_rec.total_due_aug = i[27]
        b_rec.total_paid_aug = i[28]
        b_rec.total_usage_aug = i[29]
        b_rec.total_due_sept = i[30]
        b_rec.total_paid_sept = i[31]
        b_rec.total_usage_sept = i[32]
        b_rec.total_due_oct = i[33]
        b_rec.total_paid_oct = i[34]
        b_rec.total_usage_oct = i[35]
        b_rec.total_due_nov = i[36]
        b_rec.total_paid_nov = i[37]
        b_rec.total_usage_nov = i[38]
        b_rec.total_due_dec = i[39]
        b_rec.total_paid_dec = i[40]
        b_rec.total_usage_dec = i[41]
        b_rec.save()


#------------------JAZZY<3----------------------#

mycursor = mydb.cursor()
def porter_in(request):
    col = 0
    for t in range(len(tablenames)):
        mycursor.execute("SELECT count(*) FROM information_schema.columns WHERE TABLE_NAME = '"+tablenames[t]+"';")
        for c in range(mycursor.fetchone()[0]):
            mycursor.execute("SELECT " + columnnames[col] + " FROM "+tablenames[t]+";")
            result=mycursor.fetchall()
            for x in result:
                alltables[t][c].append(x[0])
            col+=1
    
    current_table = rearrange('ratestable')#change string parameter to desired table name reference in tablenames above
    porter_out(current_table)
    return render(request, "home.html")

def rearrange(var):
    arr = []
    mycursor.execute("SELECT count(*) FROM information_schema.columns WHERE TABLE_NAME = '"+var+"';")
    cols = mycursor.fetchone()[0]
    mycursor.execute("SELECT count(*) FROM "+var+";")
    rows = mycursor.fetchone()[0]
    for r in range(rows):
        inner = []
        for c in range(cols):
            inner.append(globals()[var][c][r])
        arr.append(inner)

    return arr

    
def porter_out(table):
    rt = Rates()
    for i in table:
        rt.minReading = i[0]
        rt.minReadingCharge = i[2]
        rt.rateAfterMin = i[3]
        rt.ratePenalty = i[4]
        rt.ratePenaltyFreq = i[5]
        rt.save()


#-----------------------------------#

    



def login(request):
>>>>>>> Stashed changes
    if request.method == "POST":
        u = request.POST['username']
        password = request.POST['password']

        user = SystemUsers.objects.get(username = u)
        passAscii = password.encode("ascii")
        p = base64.b64encode(passAscii)
        print(p)
        if user is not None:
            if user.password == p:
                login(request,user)
                messages.success(request, 'Logged in')
                return redirect('dashboard')
            else:
                messages.error(request, "Invalid Password")
        else:
            messages.error(request, "Invalid Username")

    return render(request, 'login.html')


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


