from django.http import HttpResponse
from django.shortcuts import redirect
from .DBdb import *
from .models import *
from django.core.exceptions import ObjectDoesNotExist


def unauthenticated_user(view_func):
    def wrapper_func(request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('bills_list')
        else:
            return view_func(request, *args, **kwargs)
    return wrapper_func

# def allowed_users(allowed_roles=[]):
# 	def decorator(view_func):
# 		def wrapper_func(request, *args, **kwargs):
# 			u_type = None
# 			if request.user.u_type is not None:
# 				u_type = request.user.u_type
# 			if u_type in allowed_roles:
# 				return view_func(request, *args, **kwargs)
# 			else:
# 				return HttpResponse('You are not authorized to view this page')
# 		return wrapper_func
# 	return decorator
