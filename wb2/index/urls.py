from . import views

from django.urls import path
from django.views.generic.base import RedirectView

from django.contrib.auth import views as auth_views

urlpatterns = [
    path('',views.porter_in,name='p_in'),
    path('login',views.login,name='login'),
    path('user_creation', views.user_creation,name='user_creation')
    
]