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
    # porter()
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

def ledger(request):
    return render(request, 'dashboard.html')