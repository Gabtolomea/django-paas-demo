from django.http import HttpResponse
from django.shortcuts import redirect
from .DBdb import *
from .models import *
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import user_passes_test, login_required


def is_admin(request):
    if str(request.session[ReqParams.ADMIN]) == 'Admin':
        return True
    else:
        return False


rec_login_required = user_passes_test(
    lambda u: True if u.is_admin else False, login_url='login')


def admin_login_required(view_func):
    decorated_view_func = login_required(
        rec_login_required(view_func), login_url='login')
    return decorated_view_func


def is_teller(request):
    if str(request.session[ReqParams.TELLER]) == 'Teller':
        return True
    else:
        return False


rec_login_required = user_passes_test(
    lambda u: True if u.is_teller else False, login_url='login')
    

def teller_login_required(view_func):
    decorated_view_func = login_required(
        rec_login_required(view_func), login_url='login')
    return decorated_view_func


def is_supervisor(request):
    if str(request.session[ReqParams.SUPERVISOR]) == 'Supervisor':
        return True
    else:
        return False


rec_login_required = user_passes_test(
    lambda u: True if u.is_supervisor else False, login_url='login')


def supervisor_login_required(view_func):
    decorated_view_func = login_required(
        rec_login_required(view_func), login_url='login')
    return decorated_view_func


def is_manager(request):
    if str(request.session[ReqParams.MANAGER]) == 'Manager':
        return True
    else:
        return False


rec_login_required = user_passes_test(
    lambda u: True if u.is_manager else False, login_url='login')


def manager_login_required(view_func):
    decorated_view_func = login_required(
        rec_login_required(view_func), login_url='login')
    return decorated_view_func


def is_reader(request):
    if str(request.session[ReqParams.READER]) == 'Reader':
        return True
    else:
        return False


rec_login_required = user_passes_test(
    lambda u: True if u.is_reader else False, login_url='login')


def reader_login_required(view_func):
    decorated_view_func = login_required(
        rec_login_required(view_func), login_url='login')
    return decorated_view_func


def unauthenticated_user(view_func):
    def wrapper_func(request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('bills_list')
        else:
            return view_func(request, *args, **kwargs)
    return wrapper_func


# def allowed_users(user_roles=[]):
#     def decorator(view_func):
#         def wrapper_func(request, *args, **kwargs):
#             is_teller = None
#             if str(request.session[ReqParams.TELLER]) is not None:
#                 return True
#             if is_teller in user_roles:
#                 return view_func(request, *args, **kwargs)
#             else:
#                 return redirect('bills_list')
#         return wrapper_func
#     return decorator
