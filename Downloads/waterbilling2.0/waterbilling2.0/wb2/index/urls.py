from . import views
from . import reports
from django.urls import path
from .views import  mark_unpaid ,delinquent_accounts


urlpatterns = [
    path('port',views.porter,name='port'),
    path('',views.lp,name='landing'),
    path('login/',views.signin,name='login'),
    path('user_creation', views.user_creation,name='user_creation'),
    path('signout', views.signout,name='signout'),
    path('bills_list', views.bills_list, name='bills_list'),
    path('bills_list/ledger/<id>/', views.ledger,name='ledger'),
    path('bills_list/ledger/conmon_summary/<id>/<int:year>', views.monthly_summary,name='monthly_summary'),
    path('bills_list/ledger/payment_history/<id>/<int:year>', views.payment_history,name='payment_history'),
    path('editpayment/<id>/', views.editpayment,name='editpayment'),
    path('undodelete', views.undodelete,name='undodelete'),
    path('payment/<int:id>/', views.payment, name='payment'),

    path('monthlypayment/', views.monthlypayment, name='monthlypayment'),
    path('meterreading', views.meterreading,name='meterreading'),
    path('meterreading/bulkreading', views.bulkreading,name='bulkreading'),
    path('meterreading/deletereading/<int:id>', views.deletereading,name='deletereading'),
    path('meterreading/<id>/<int:year>', views.inputreading,name='inputreading'),
    path('forgetpassword', views.forgetpassword,name='forgetpassword'),
    path('resetpassword/<uidb64>/<token>', views.resetpassword,name='resetpassword'),
    path('stopmeter/<id>', views.stopmeter,name='stopmeter'),
    path('enablemeter/<id>', views.enablemeter,name='enablemeter'),
    path('consumercreation', views.consumercreation,name='consumercreation'),
    path('consumer_list/', views.consumer_list, name='consumer_list'),
    path('consumer_list/consumercreation', views.consumercreation,name='consumercreation'),
    path('consumer_list/<id>/', views.consumerupdate, name='consumerupdate'),
    path('deleteconsumer', views.deleteconsumer,name='deleteconsumer'),
    path('disconnectconsumer/<id>', views.disconnectconsumer,name='disconnectconsumer'),
    path('reconnectconsumer/<id>', views.reconnectconsumer,name='reconnectconsumer'),
    path('sysuser/', views.sysuser,name='sysuser'),
    path('sysuser/user_creation', views.user_creation,name='user_creation'),
    path('sysuser/edit/<id>/', views.user_edit, name='user_edit'),
    path('deleteUser/<id>/', views.deleteUser, name='deleteUser'),
    path('about', views.about, name='about'),
    path('reports', views.reports, name='reports'),
    path('reports/barangayreport/<int:year>', views.barangayreport, name='barangayreport'),
    #path('reports/view_barangay/<id>/', views.view_barangay, name='view_barangay'),
    path('reports/barangayreport/view_barangay/<str:id>/<int:year>/', views.view_barangay, name='view_barangay'),
    path('reports/usage_report_data/<int:year>', views.usage_report_data, name='usage_report_data'),
    path('reports/revenue_report/<int:year>', views.revenue_report, name='revenue_report'),
    path('reports/consumption/<int:year>', views.consumption, name='consumption'),
    path('reports/monthly_collections/', views.monthly_collections, {'year': None}, name='monthly_collections'),
    path("reports/billing-report/", reports.monthly_billing_report, name="billing_report"),
    path('reports/monthly_collections/<int:year>/', views.monthly_collections, name='monthly_collections'),
    path('reports/record_list', views.record_list, name ='record_list'), #added by kathrina D. Bandajon nov. 26, 2024 -.- ID: AllPaid2611
    path('unsettled_bills',views.unsettled_bills, name='unsettled_bills'),
    path('unsettled_bills/<id>/<int:year>',views.view_unsettled_bills, name='view_unsettled_bills'),
    path('payment/<id>/', views.payment, name='payment'),
    path('additional_fee/<id>/', views.additional_fee, name='additional_fee'),
    path('settings/new_consumertype', views.new_consumertype, name='new_consumertype'),
    path('settings/discount',views.discount, name='discount'),
    path('settings/discount/editdiscount/<id>', views.editdiscount, name='editdiscount'),
    path('settings/deletediscount/<id>', views.deletediscount, name='deletediscount'),
    path('settings/penalty', views.penalty, name='penalty'),
    path('settings/penalty/editpenalty/<id>', views.editpenalty, name='editpenalty'),    
    path('settings/exemptions/', views.exemptiont, name= 'exemptiont'),
    path('settings/addexemptions/<str:id>/', views.addexemption, name='addexemptions'),
    path('settings/userprof', views.userprof, name='userprof'),
    path('settings', views.viewprof, name='settings'),
    path('add_issue/<id>/<int:year>', views.add_issue, name='add_issue'),
    path('issues', views.issues_view, name='issues'),
    path('issue_details/<id>', views.issue_details, name='issue_details'),
    path('submit_comment/<id>', views.submit_comment, name='submit_comment'),
    path('resolve_issue', views.resolve_issue,name='resolve_issue'),
    path('new_penalty', views.new_penalty), #added by K. Bandajon October 29, 2024 The new penalty rate-.- ID: NewPenaltyOct2024
    path("mark_unpaid/<int:transaction_id>/", mark_unpaid, name="mark_unpaid"),#added Adjay
    path('payment_history/<str:id>/', views.payment_history, name='payment_history'),#added Adjay
    path('delinquent-accounts/', delinquent_accounts, name='delinquent_accounts'),#zel added
    path('delinquent_months/', views.delinquent_months, name='delinquent_months'),#added by Enjambre
    path("average_consumption_all_report/", reports.average_consumption_all_report, name="average_consumption_all_report"), #not yet applied
    path('bills_list/ledger/additionalfeeslist/<str:consumer_id>/', views.additionalfeeslist, name='additionalfeeslist'),
    
    
    path('consumer/<int:consumer_id>/fees/', views.additionalfeeslist, name='additionalfeeslist'),
    path('payfee/<int:id>/', views.addfee_paymentmethod, name='addfee_paymentmethod'),
    path('additionalfees/<int:fee_id>/transactions/', views.addfeepayment_history, name='payment_history'),
    #path('consumer/<str:consumer_id>/getbill/', views.process_bill_selection, name='process_bill_selection')
    #path('year-dropdown/', views.year_dropdown, name='year_dropdown'),
]

