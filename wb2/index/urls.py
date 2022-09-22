from . import views

from django.urls import path
from django.views.generic.base import RedirectView

from django.contrib.auth import views as auth_views

urlpatterns = [
    path('lp',views.lp,name='lp'),
    path('login',views.signin,name='login'),
    path('user_creation', views.user_creation,name='user_creation'),
    path('dashboard', views.dashboard,name='dashboard'),
    path('signout', views.signout,name='signout'),
    # path('ledger', views.ledger,name='ledger'),
    path('reset_password/',auth_views.PasswordResetView.as_view(template_name="forgetpassword.html"),name="reset_password"),
    path('reset_password_sent/',auth_views.PasswordResetDoneView.as_view(template_name="resetsent.html"),name="password_reset_done"),
    path('reset/<uidb64>/<token>/',auth_views.PasswordResetConfirmView.as_view(template_name="password_reset_form.html"),name="password_reset_confirm"),
    path('reset_password_complete/',auth_views.PasswordResetCompleteView.as_view(template_name="password_reset_done.html"),name="password_reset_complete"),

]