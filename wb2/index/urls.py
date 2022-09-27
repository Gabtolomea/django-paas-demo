from . import views

from django.urls import path
from django.views.generic.base import RedirectView

from django.contrib.auth import views as auth_views

urlpatterns = [
    path('port',views.porter,name='porter'),
    path('',views.lp,name='landing'),
    path('login',views.signin,name='login'),
    path('user_creation', views.user_creation,name='user_creation'),
    path('dashboard', views.dashboard,name='dashboard'),
    path('signout', views.signout,name='signout'),
    path('ledger/<id>/', views.ledger,name='ledger'),
    path('meterreading/', views.meterreading,name='meterreading'),
    path('forgetpassword', views.forgetpassword,name='forgetpassword'),
    path('reset/<uidb64>/<token>/',auth_views.PasswordResetConfirmView.as_view(template_name="password_reset_form.html"),name="password_reset_confirm"),
    path('consumercreation', views.consumercreation,name='consumercreation'),
    path('bills_list/', views.bills_list, name='bills_list'),
    path('consumer_list/', views.consumer_list, name='consumer_list')
    path('inputreading', views.inputreading, name='inputreading')
    # path('reset_password_complete/',auth_views.PasswordResetCompleteView.as_view(template_name="password_reset_done.html"),name="password_reset_complete"),

]