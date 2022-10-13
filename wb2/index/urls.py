from . import views

from django.urls import path
from django.views.generic.base import RedirectView
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('port',views.porter,name='port'),
    path('',views.lp,name='landing'),
    path('login',views.signin,name='login'),
    path('signout', views.signout,name='signout'),
    path('bills_list/', views.bills_list, name='bills_list'),
    path('bills_list/<id>/', views.ledger,name='ledger'),
    path('payment/<id>/', views.payment, name='payment'),
    path('meterreading/', views.meterreading,name='meterreading'),
    path('meterreading/<id>/<int:year>', views.inputreading,name='inputreading'),
    path('stopmeter/<id>/', views.stopmeter, name='stopmeter'),
    path('consumer_list/', views.consumer_list, name='consumer_list'),
    path('consumer_list/consumercreation', views.consumercreation,name='consumercreation'),
    path('consumer_list/<int:id>/', views.userupdate, name='userupdate'),
    path('sysuser/', views.sysuser,name='sysuser'),
    path('user_creation', views.user_creation,name='user_creation'),
    path('user_edit/<id>/', views.user_edit, name='user_edit'),
    path('deleteUser/<id>/', views.deleteUser, name='deleteUser'),
    path('about', views.about, name='about'),
    path('barangayreport', views.br, name='br'),
    path('barangayreport/<int:year>', views.barangayreport, name='barangayreport'),
    path('view_barangay/<id>/', views.view_barangay, name='view_barangay'),
    path('usage_report_data/<int:year>', views.usage_report_data, name='usage_report_data'),
    path('usage_report_data/<int:year>/barangay_by_monthly/<id>/', views.barangay_by_monthly, name='barangay_by_monthly'),
    path('revenue_report/<int:year>', views.revenue_report, name='revenue_report'),
    path('unsettled_bills/',views.unsettled_bill, name='unsettled_bills'),
    path('view_unsettled_bills/',views.unsettled_bill, name='view_unsettled_bills')



    # path('reset_password_complete/',auth_views.PasswordResetCompleteView.as_view(template_name="password_reset_done.html"),name="password_reset_complete"),

]