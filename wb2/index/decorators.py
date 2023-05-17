
from django.shortcuts import redirect
from .models import *


def unauthenticated_user(view_func):
    def wrapper_func(request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('bills_list')
        else:
            return view_func(request, *args, **kwargs)
    return wrapper_func

def allowed_users(allowed_roles=[]):
	def decorator(view_func):
		def wrapper_func(request, *args, **kwargs):
			proceed = False
			roles = [
				'admin',
				'teller',
				'supervisor',
                'manager',
                'reader'
            ]
			user = SystemUsers.objects.get(username=request.user)
			for i in roles:
				if user.__dict__[f'is_{i}'] and i in allowed_roles:
					proceed = True
			if proceed:
				return view_func(request, *args, **kwargs)
			else:
				return HttpResponse('You are not authorized to view this page')
		return wrapper_func
	return decorator

