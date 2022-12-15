from django.http import HttpResponse
from django.shortcuts import redirect
from .DBdb import *
from .models import *
from django.core.exceptions import ObjectDoesNotExist
from functools import wraps
from django.contrib.auth.decorators import user_passes_test, login_required

def unauthenticated_user(view_func):
    def wrapper_func(request, *args, **kwargs):
        try:
            request.session[ReqParams.username]
        except KeyError:
            username = ''
        else:
            username = request.session[ReqParams.username]
        try:
            LoginRec.objects.get(username=username)
        except ObjectDoesNotExist:
            a = False
        else:
            a = True
        if a:
            return redirect('bills_list')
        else:
            return view_func(request, *args, **kwargs)
    return wrapper_func


def authenticated_user(view_func):
    def wrapper_func(request, *args, **kwargs):
        try:
            request.session[ReqParams.username]
        except KeyError:
            username = ''
        else:
            username = request.session[ReqParams.username]
        try:
            LoginRec.objects.get(username=username)
        except ObjectDoesNotExist:
            a = True
        else:
            a = False
        if a:
            return redirect('login')
        else:
            return view_func(request, *args, **kwargs)
    return wrapper_func


# def allowed_users(allowed_roles=[]):
#     def decorator(view_func):
#         def wrapper_func(request, *args, **kwargs):
#             u_type = None
#             if request.user.u_type is not None:
#                 u_type = request.user.u_type
#             if u_type in allowed_roles:
#                 return view_func(request, *args, **kwargs)
#             else:
#                 return HttpResponse('You are not authorized to view this page')
#         return wrapper_func
#     return decorator

def is_admin(user):
    if str(user.is_admin) == 'Admin':
        return True
    else:
        return False
rec_login_required = user_passes_test(lambda u: True if u.is_admin else False, login_url= 'login')

def admin_login_required(view_func):
    decorated_view_func = login_required(rec_login_required(view_func), login_url='login')
    return decorated_view_func



def is_teller(user):
    if str(user.is_teller) == 'Teller':
        return True
    else:
        return False
rec_login_required = user_passes_test(lambda u: True if u.is_teller else False, login_url= 'login')

def teller_login_required(view_func):
    decorated_view_func = login_required(rec_login_required(view_func),login_url= 'login')
    return decorated_view_func



def is_supervisor(user):
    if str(user.is_suprvisor) == 'Supervisor':
        return True
    else:
        return False
rec_login_required = user_passes_test(lambda u: True if u.is_supervisor else False, login_url='login')

def supervisor_login_required(view_func):
    decorated_view_func = login_required(rec_login_required(view_func), login_url='login')
    return decorated_view_func



def is_manager(user):
    if str(user.is_manager) == 'Manager':
        return True
    else:
        return False
rec_login_required = user_passes_test(lambda u: True if u.is_manager else False, login_url='login')

def manager_login_required(view_func):
    decorated_view_func = login_required(rec_login_required(view_func), login_url='login')
    return decorated_view_func


def is_reader(user):
    if str(user.is_reader) == 'Reader':
        return True
    else:
        return False
rec_login_required = user_passes_test(lambda u: True if u.is_reader else False, login_url='login')

def reader_login_required(view_func):
    decorated_view_func = login_required(rec_login_required(view_func), login_url='login')
    return decorated_view_func
