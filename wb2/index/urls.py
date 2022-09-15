from . import views

from django.urls import path
from django.views.generic.base import RedirectView

from django.contrib.auth import views as auth_views

urlpatterns = [
    path('',views.landingpage,name='lp'),
    path('login',views.login,name='login'),
    path('userreg', views.user_creation,name='userreg')
    
]