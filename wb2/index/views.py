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

from wb2 import settings
from .forms import *
from .decorators import *
from .models import *


def landingpage(request):
    context = {}
    return render(request, 'index.html', context)


def login(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, 'Logged in')
            return redirect('home')
        else:
            messages.error(request, "Invalid Username or Password")

    return render(request, 'login.html')

def home(request):
    return render(request, 'home.html')