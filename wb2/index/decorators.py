from django.http import HttpResponse
from django.shortcuts import redirect

def unauthenticated_user(view_func):
    def wrapper_func(request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('/')
        else:
            return view_func(request, *args, **kwargs)
    return wrapper_func

def session_login_required(function=None, session_key='user'):
	def decorator(view_func):
		def wrapper_func(request, *args, **kwargs):
			u_type = None
			if request.user.u_type is not None:
				u_type = request.user.u_type

			if session_key in request.session:
				return view_func(request, *args, **kwargs)
			else:
				return HttpResponse('You are not authorized to view this page')
		return wrapper_func
	return decorator