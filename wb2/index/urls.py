from . import views

from django.urls import path
from django.views.generic.base import RedirectView
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('port',views.porter,name='port'),
    path('',views.lp,name='landing'),
    # path('dashboard',views.dashboard,name='dashboard'),
    path('login/',views.signin,name='login'),
    path('user_creation', views.user_creation,name='user_creation'),
    path('signout', views.signout,name='signout'),
    path('bills_list', views.bills_list, name='bills_list'),
    path('bills_list/p/<int:p>', views.bills_list_p, name='bills_list_p'),
    path('bills_list/ledger/<id>/', views.ledger,name='ledger'),
    path('payment/<id>/', views.payment, name='payment'),
    path('meterreading', views.meterreading,name='meterreading'),
    path('meterreading/p/<int:p>', views.meterreading_p,name='meterreading_p'),
    path('meterreading/<id>/<int:year>', views.inputreading,name='inputreading'),
    path('forgetpassword', views.forgetpassword,name='forgetpassword'),
    path('reset/<uidb64>/<token>/',auth_views.PasswordResetConfirmView.as_view(template_name="password_reset_form.html"),name="password_reset_confirm"),
    path('consumercreation', views.consumercreation,name='consumercreation'),
    path('consumer_list/', views.consumer_list, name='consumer_list'),
    path('consumer_list/p/<int:p>', views.consumer_list_p, name='consumer_list_p'),
    path('consumer_list/consumercreation', views.consumercreation,name='consumercreation'),
    path('consumer_list/<int:id>/', views.userupdate, name='userupdate'),
    path('deleteconsumer/<int:id>', views.deleteconsumer,name='deleteconsumer'),
    path('sysuser/', views.sysuser,name='sysuser'),
    path('user_creation', views.user_creation,name='user_creation'),
    path('sysuser/<id>/', views.user_edit, name='user_edit'),
    path('deleteUser/<id>/', views.deleteUser, name='deleteUser'),
    path('about', views.about, name='about'),
    path('reports', views.reports, name='reports'),
    path('reports/waterusage/<int:year>', views.barangayreport, name='barangayreport'),
    path('reports/view_barangay/<id>/', views.view_barangay, name='view_barangay'),
    path('reports/usage_report_data/<int:year>', views.usage_report_data, name='usage_report_data'),
    path('reports/bbm/<id>',views.bbm, name='bbm'),
    path('reports/revenue_report/<int:year>', views.revenue_report, name='revenue_report'),
    path('unsettled_bills/',views.unsettled_bills, name='unsettled_bills'),
    path('unsettled_bills/p/<int:p>', views.unsettled_bills_p, name='unsettled_bills_p'),
    path('reports/unsettled_bills/<id>/<int:year>',views.view_unsettled_bills, name='view_unsettled_bills'),
    path('payment/<id>/', views.payment, name='payment'),
    path('new_consumertype', views.new_consumertype, name='new_consumertype'),
    path('discount',views.discount, name='discount'),
    path('penalty', views.penalty, name='penalty'),

    # path('reset_password_complete/',auth_views.PasswordResetCompleteView.as_view(template_name="password_reset_done.html"),name="password_reset_complete"),

]