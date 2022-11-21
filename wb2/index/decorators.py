from django.http import HttpResponse
from django.contrib import messages
from django.shortcuts import redirect
from .DBdb import *

def unauthenticated_user(view_func):
	def wrapper_func(request, *args, **kwargs):
		if ReqParams.cs.auth:
			return redirect('test')
		else:
			return view_func(request, *args, **kwargs)
	return wrapper_func

def authenticated_user(view_func):
	def wrapper_func(request, *args, **kwargs):
		if not ReqParams.cs.auth:
			return redirect('login')
		else:
			return view_func(request, *args, **kwargs)
	return wrapper_func



def allowed_users(allowed_roles=[]):
	def decorator(view_func):
		def wrapper_func(request, *args, **kwargs):
			u_type = None
			if request.user.u_type is not None:
				u_type = request.user.u_type

			if u_type in allowed_roles:
				return view_func(request, *args, **kwargs)
			else:
				return HttpResponse('You are not authorized to view this page')
		return wrapper_func
	return decorator