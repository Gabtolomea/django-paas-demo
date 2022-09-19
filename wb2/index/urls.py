from . import views

from django.urls import path
from django.views.generic.base import RedirectView

from django.contrib.auth import views as auth_views

urlpatterns = [
    path('lp',views.lp,name='lp'),
    path('',views.signin,name='login'),
    path('user_creation', views.user_creation,name='user_creation'),
    path('dashboard', views.dashboard,name='dashboard'),
    path('signout', views.signout,name='signout'),

   

    
]