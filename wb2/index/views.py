
from os import system
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.shortcuts import redirect
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import EmailMessage
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string

import mysql.connector

from wb2 import settings
from .forms import *
from .decorators import *
from .models import *


tablenames = [
    "accountinfo",
    "accountrecord",
    "barangay_record",
    "consumerinfo",
    "gettotalbill",
    "oldconsumerinfo",
    "payment_history",
    "ratestable",
    "revenuecode",
    "systemuser",
    "yearly_records"
]
columnnames = [
    "accountinfoid",
    "firstname",
    "middlename",
    "lastname",
    "address",
    'barangay',
    'meternumber',
    'initial_meter_reading',
    'rateid',
    'status',
    'duedate',
    'consumerid_id',
    'penalty_flag',
    'deleted_flag',
    'stop_meter_flag',
    'accountid',
    'rateid',
    'prevyeardue',
    'excesspayment',
    'commulative_bill',
    'year',
    'reading_jan',
    'reading_date_jan',
    'reading_postedby_jan',
    'usage_jan',
    'penalty_jan',
    'bill_jan',
    'totalbill_jan',
    'paidamt_jan',
    'datepaid_jan',
    'dateposted_jan',
    'postedby_jan',
    'txrefnum_jan',
    'ior_jan',
    'reading_feb',
    'reading_date_feb',
    'reading_postedby_feb',
    'usage_feb',
    'penalty_feb',
    'bill_feb',
    'totalbill_feb',
    'paidamt_feb',
    'datepaid_feb',
    'dateposted_feb',
    'postedby_feb',
    'txrefnum_feb',
    'ior_feb',
    'reading_mar',
    'reading_date_mar',
    'reading_postedby_mar',
    'usage_mar',
    'penalty_mar',
    'bill_mar',
    'totalbill_mar',
    'paidamt_mar',
    'datepaid_mar',
    'dateposted_mar',
    'postedby_mar',
    'txrefnum_mar',
    'ior_mar',
    'reading_apr',
    'reading_date_apr',
    'reading_postedby_apr',
    'usage_apr',
    'penalty_apr',
    'bill_apr',
    'totalbill_apr',
    'paidamt_apr',
    'datepaid_apr',
    'dateposted_apr',
    'postedby_apr',
    'txrefnum_apr',
    'ior_apr',
    'reading_may',
    'reading_date_may',
    'reading_postedby_may',
    'usage_may',
    'penalty_may',
    'bill_may',
    'totalbill_may',
    'paidamt_may',
    'datepaid_may',
    'dateposted_may',
    'postedby_may',
    'txrefnum_may',
    'ior_may',
    'reading_jun',
    'reading_date_jun',
    'reading_postedby_jun',
    'usage_jun',
    'penalty_jun',
    'bill_jun',
    'totalbill_jun',
    'paidamt_jun',
    'datepaid_jun',
    'dateposted_jun',
    'postedby_jun',
    'txrefnum_jun',
    'ior_jun',
    'reading_jul',
    'reading_date_jul',
    'reading_postedby_jul',
    'usage_jul',
    'penalty_jul',
    'bill_jul',
    'totalbill_jul',
    'paidamt_jul',
    'datepaid_jul',
    'dateposted_jul',
    'postedby_jul',
    'txrefnum_jul',
    'ior_jul',
    'reading_aug',
    'reading_date_aug',
    'reading_postedby_aug',
    'usage_aug',
    'penalty_aug',
    'bill_aug',
    'totalbill_aug',
    'paidamt_aug',
    'datepaid_aug',
    'dateposted_aug',
    'postedby_aug',
    'txrefnum_aug',
    'ior_aug',
    'reading_sept',
    'reading_date_sept',
    'reading_postedby_sept',
    'usage_sept',
    'penalty_sept',
    'bill_sept',
    'totalbill_sept',
    'paidamt_sept',
    'datepaid_sept',
    'dateposted_sept',
    'postedby_sept',
    'txrefnum_sept',
    'ior_sept',
    'reading_oct',
    'reading_date_oct',
    'reading_postedby_oct',
    'usage_oct',
    'penalty_oct',
    'bill_oct',
    'totalbill_oct',
    'paidamt_oct',
    'datepaid_oct',
    'dateposted_oct',
    'postedby_oct',
    'txrefnum_oct',
    'ior_oct',
    'reading_nov',
    'reading_date_nov',
    'reading_postedby_nov',
    'usage_nov',
    'penalty_nov',
    'bill_nov',
    'totalbill_nov',
    'paidamt_nov',
    'datepaid_nov',
    'dateposted_nov',
    'postedby_nov',
    'txrefnum_nov',
    'ior_apr',
    'reading_dec',
    'reading_date_dec',
    'reading_postedby_dec',
    'usage_dec',
    'penalty_dec',
    'bill_dec',
    'totalbill_dec',
    'paidamt_dec',
    'datepaid_dec',
    'dateposted_dec',
    'postedby_dec',
    'txrefnum_dec',
    'ior_dec',
    'consumerid_id',
    'amountpaid_str_apr',
    'amountpaid_str_aug',
    'amountpaid_str_dec',
    'amountpaid_str_feb',
    'amountpaid_str_jan',
    'amountpaid_str_jul',
    'amountpaid_str_jun',
    'amountpaid_str_mar',
    'amountpaid_str_may',
    'amountpaid_str_nov',
    'amountpaid_str_oct',
    'amountpaid_str_sept',
    'accountinfoid',
    'amountpaid_history',
    'datepaid_history',
    'postedby_history',
    'or_number_history',
    'previous_reading',
    'barangay_val',
    'barangay_name',
    'year',
    'total_due_ytd',
    'total_paid_ytd',
    'total_usage',
    'total_due_january',
    'total_paid_january',
    'usage_january',
    'total_due_february',
    'total_paid_february',
    'usage_february',
    'total_due_march',
    'total_paid_march',
    'usage_march',
    'total_due_april',
    'total_paid_april',
    'usage_april',
    'total_due_may',
    'total_paid_may',
    'usage_may',
    'total_due_june',
    'total_paid_june',
    'usage_june',
    'total_due_july',
    'total_paid_july',
    'usage_july',
    'total_due_august',
    'total_paid_august',
    'usage_august',
    'total_due_september',
    'total_paid_september',
    'usage_september',
    'total_due_october',
    'total_paid_october',
    'usage_october',
    'total_due_november',
    'total_paid_november',
    'usage_november',
    'total_due_december',
    'total_paid_december',
    'usage_december',
    'consumerid',
    'firstname',
    'middlename',
    'lastname',
    'birthday',
    'mobilenumber',
    'mobilenumber2',
    'emailaddress',
    'homeaddress',
    'sex',
    'installcount',
    'profilepic',
    'barangay',
    'sitio',
    'oldconsumerid',
    'deleted_flag',
    'bill_id',
    'con_id',
    'currentdue',
    'rateid',
    'paid',
    'current_reading',
    'reading_date',
    'previous_reading',
    'consumption',
    'con_id',
    'firstname',
    'middlename',
    'lastname',
    'con_category',
    'meternumber',
    'address',
    'id',
    'amount',
    'date',
    'or_number',
    'time',
    'postedby',
    'consumer',
    'accountinfoid',
    'meternumber',
    'year',
    'rateid',
    'minimumreading',
    'minimumreading_charge',
    'rateafterminimum',
    'ratepenalty',
    'ratepenaltyfrequency',
    'paymentchedday',
    'id',
    'application_fee',
    'mayors_permit',
    'gravel_excavation',
    'asphalted_road',
    'cemented_road',
    'additionalfee_pipe_of_20_lineal_feet',
    'residentialservice_per_month',
    'commercialservice_per_month',
    'residentialservice_excess_per_cubicmeter',
    'commercialservice_excess_per_cubicmeter',
    'drilling_from_mainline',
    'reinstallation_fee',
    'tapping_fee',
    'repair_fee',
    'transfer_fee',
    'three_month_penalty',
    'disconnection_after',
    'send_disconnection_notice_after',
    'fix_amount_penalty',
    'penalty_after',
    'percentage_penalty',
    'userid',
    'password',
    'firstname',
    'middlename',
    'mobilenumber',
    'lastname',
    'emailaddress',
    'usertype',
    'profilepic',
    'approver_flag',
    'year',
    'total_due_ytd',
    'total_paid_ytd', 
    'total_usage', 
    'total_due_january',
    'total_paid_january',
    'usage_january',
    'total_due_february', 
    'total_paid_february',
    'usage_february', 
    'total_due_march', 
    'total_paid_march', 
    'usage_march', 
    'total_due_april', 
    'total_paid_april', 
    'usage_april', 
    'total_due_may', 
    'total_paid_may', 
    'usage_may', 
    'total_due_june', 
    'total_paid_june', 
    'usage_june', 
    'total_due_july', 
    'total_paid_july', 
    'usage_july', 
    'total_due_august', 
    'total_paid_august', 
    'usage_august', 
    'total_due_september', 
    'total_paid_september', 
    'usage_september',
    'total_due_october', 
    'total_paid_october', 
    'usage_october', 
    'total_due_november', 
    'total_paid_november', 
    'usage_november', 
    'total_due_december', 
    'total_paid_december',
    'usage_december',

]

accountinfoid = []
firstname = []
middlename = []
lastname = []
address = []
barangay = []
meternumber = []
initial_meter_reading = []
acc_info_rateid = []
status = []
duedate = []
consumerid_id = []
penalty_flag = []
deleted_flag = []
stop_meter_flag = []

accountid = []
acc_rec_rateid = []
prevyeardue = []
excesspayment = []
commulative_bill = []
year = []
reading_jan = []
reading_date_jan = []
reading_postedby_jan = []
usage_jan = []
penalty_jan = []
bill_jan = []
totalbill_jan = []
paidamt_jan = []
datepaid_jan = []
dateposted_jan = []
postedby_jan = []
txrefnum_jan = []
ior_jan = []
reading_feb = []
reading_date_feb = []
reading_postedby_feb = []
usage_feb = []
penalty_feb = []
bill_feb = []
totalbill_feb = []
paidamt_feb = []
datepaid_feb = []
dateposted_feb = []
postedby_feb = []
txrefnum_feb = []
ior_feb = []
reading_mar = []
reading_date_mar = []
reading_postedby_mar = []
usage_mar = []
penalty_mar = []
bill_mar = []
totalbill_mar = []
paidamt_mar = []
datepaid_mar = []
dateposted_mar = []
postedby_mar = []
txrefnum_mar = []
ior_mar = []
reading_apr = []
reading_date_apr = []
reading_postedby_apr = []
usage_apr = []
penalty_apr = []
bill_apr = []
totalbill_apr = []
paidamt_apr = []
datepaid_apr = []
dateposted_apr = []
postedby_apr = []
txrefnum_apr = []
ior_apr = []
reading_may = []
reading_date_may = []
reading_postedby_may = []
usage_may = []
penalty_may = []
bill_may = []
totalbill_may = []
paidamt_may = []
datepaid_may = []
dateposted_may = []
postedby_may = []
txrefnum_may = []
ior_may = []
reading_jun = []
reading_date_jun = []
reading_postedby_jun = []
usage_jun = []
penalty_jun = []
bill_jun = []
totalbill_jun = []
paidamt_jun = []
datepaid_jun = []
dateposted_jun = []
postedby_jun = []
txrefnum_jun = []
ior_jun = []
reading_jul = []
reading_date_jul = []
reading_postedby_jul = []
usage_jul = []
penalty_jul = []
bill_jul = []
totalbill_jul = []
paidamt_jul = []
datepaid_jul = []
dateposted_jul = []
postedby_jul = []
txrefnum_jul = []
ior_jul = []
reading_aug = []
reading_date_aug = []
reading_postedby_aug = []
usage_aug = []
penalty_aug = []
bill_aug = []
totalbill_aug = []
paidamt_aug = []
datepaid_aug = []
dateposted_aug = []
postedby_aug = []
txrefnum_aug = []
ior_aug = []
reading_sept = []
reading_date_sept = []
reading_postedby_sept = []
usage_sept = []
penalty_sept = []
bill_sept = []
totalbill_sept = []
paidamt_sept = []
datepaid_sept = []
dateposted_sept = []
postedby_sept = []
txrefnum_sept = []
ior_sept = []
reading_oct = []
reading_date_oct = []
reading_postedby_oct = []
usage_oct = []
penalty_oct = []
bill_oct = []
totalbill_oct = []
paidamt_oct = []
datepaid_oct = []
dateposted_oct = []
postedby_oct = []
txrefnum_oct = []
ior_oct = []
reading_nov = []
reading_date_nov = []
reading_postedby_nov = []
usage_nov = []
penalty_nov = []
bill_nov = []
totalbill_nov = []
paidamt_nov = []
datepaid_nov = []
dateposted_nov = []
postedby_nov = []
txrefnum_nov = []
ior_apr = []
reading_dec = []
reading_date_dec = []
reading_postedby_dec = []
usage_dec = []
penalty_dec = []
bill_dec = []
totalbill_dec = []
paidamt_dec = []
datepaid_dec = []
dateposted_dec = []
postedby_dec = []
txrefnum_dec = []
ior_dec = []
consumerid_id = []
amountpaid_str_apr = []
amountpaid_str_aug = []
amountpaid_str_dec = []
amountpaid_str_feb = []
amountpaid_str_jan = []
amountpaid_str_jul = []
amountpaid_str_jun = []
amountpaid_str_mar = []
amountpaid_str_may = []
amountpaid_str_nov = []
amountpaid_str_oct = []
amountpaid_str_sept = []
acc_rec_accountinfoid = []
amountpaid_history = []
datepaid_history = []
postedby_history = []
or_number_history = []
acc_rec_previous_reading = []

barangay_val=[]
barangay_name=[]
brgy_rec_year=[]
total_due_ytd=[]
total_paid_ytd=[]
total_usage=[]
total_due_january=[]
total_paid_january=[]
usage_january=[]
total_due_february=[]
total_paid_february=[]
usage_february=[]
total_due_march=[]
total_paid_march=[]
usage_march=[]
total_due_april=[]
total_paid_april=[]
usage_april=[]
total_due_may=[]
total_paid_may=[]
usage_may=[]
total_due_june=[]
total_paid_june=[]
usage_june=[]
total_due_july=[]
total_paid_july=[]
usage_july=[]
total_due_august=[]
total_paid_august=[]
usage_august=[]
total_due_september=[]
total_paid_september=[]
usage_september=[]
total_due_october=[]
total_paid_october=[]
usage_october=[]
total_due_november=[]
total_paid_november=[]
usage_november=[]
total_due_december=[]
total_paid_december=[]
usage_december=[]

consumerid=[]
cons_info_firstname=[]
cons_info_middlename=[]
cons_info_lastname=[]
cons_info_birthday=[]
mobilenumber=[]
mobilenumber2=[]
emailaddress=[]
homeaddress=[]
sex=[]
installcount=[]
profilepic=[]
cons_info_barangay=[]
sitio=[]
oldconsumerid=[]
cons_info_deleted_flag=[]

bill_id=[]
con_id=[]
currentdue=[]
rateid=[]
paid=[]
current_reading=[]
reading_date=[]
previous_reading=[]
consumption=[]

old_con_id=[]
old_firstname=[]
old_middlename=[]
old_lastname=[]
con_category=[]
old_meternumber=[]
old_address=[]

pay_hist_id=[]
amount=[]
pay_hist_date=[]
or_number=[]
time=[]
postedby=[]
consumer=[]
pay_hist_accountinfoid=[]
pay_hist_meternumber=[]
pay_hist_year=[]

rt_id=[]
minimumreading=[]
minimumreading_charge=[]
rateafterminimum=[]
ratepenalty=[]
ratepenaltyfrequency=[]
paymentchedday=[]

revid=[]
application_fee=[]
mayors_permit=[]
gravel_excavation=[]
asphalted_road=[]
cemented_road=[]
additional_fee_pipe_of_20_lineal_feet=[]
residentialservice_per_month=[]
commercialservice_per_month=[]
residentialservice_excess_per_cubicmeter=[]
commercialservice_per_cubicmeter=[]
drilling_from_mainline=[]
reinstallation_fee=[]
tapping_fee=[]
repair_fee=[]
transfer_fee=[]
three_month_penalty=[]
disconnection_after=[]
send_disconnection_notice_after=[]
fix_amount_penalty=[]
penalty_after=[]
percentage_penalty=[]

userid=[]
password=[]
su_firstname=[]
su_middlename=[]
su_mobilenumber=[]
su_lastname=[]
su_emailaddress=[]
usertype=[]
su_profilepic=[]
approver_flag=[]

yr_year=[]
total_due_ytd=[]
yr_total_paid_ytd=[]
yr_total_usage=[]
yr_total_due_january=[]
yr_total_paid_january=[]
yr_usage_january=[]
yr_total_due_february =[]
yr_total_paid_february=[]
yr_usage_february =[]
yr_total_due_march =[]
yr_total_paid_march =[]
yr_usage_march=[] 
yr_total_due_april =[]
yr_total_paid_april =[]
yr_usage_april =[]
yr_total_due_may =[]
yr_total_paid_may =[]
yr_usage_may =[]
yr_total_due_june=[] 
yr_total_paid_june =[]
yr_usage_june =[]
yr_total_due_july =[]
yr_total_paid_july =[]
yr_usage_july =[]
yr_total_due_august =[]
yr_total_paid_august =[]
yr_usage_august =[]
yr_total_due_september =[]
yr_total_paid_september =[]
yr_usage_september =[]
yr_total_due_october =[]
yr_total_paid_october =[]
yr_usage_october =[]
yr_total_due_november =[]
yr_total_paid_november =[]
yr_usage_november=[]
yr_total_due_december =[]
yr_total_paid_december=[]
yr_usage_december=[]

accountinfo = [
    accountinfoid,
    firstname,
    middlename,
    lastname,
    address,
    barangay,
    meternumber,
    initial_meter_reading,
    acc_info_rateid,
    status,
    duedate,
    consumerid_id,
    penalty_flag,
    deleted_flag,
    stop_meter_flag
]
accountrecord = [
    accountid,
    acc_rec_rateid,
    prevyeardue,
    excesspayment,
    commulative_bill,
    year,
    reading_jan,
    reading_date_jan,
    reading_postedby_jan,
    usage_jan,
    penalty_jan,
    bill_jan,
    totalbill_jan,
    paidamt_jan,
    datepaid_jan,
    dateposted_jan,
    postedby_jan,
    txrefnum_jan,
    ior_jan,
    reading_feb,
    reading_date_feb,
    reading_postedby_feb,
    usage_feb,
    penalty_feb,
    bill_feb,
    totalbill_feb,
    paidamt_feb,
    datepaid_feb,
    dateposted_feb,
    postedby_feb,
    txrefnum_feb,
    ior_feb,
    reading_mar,
    reading_date_mar,
    reading_postedby_mar,
    usage_mar,
    penalty_mar,
    bill_mar,
    totalbill_mar,
    paidamt_mar,
    datepaid_mar,
    dateposted_mar,
    postedby_mar,
    txrefnum_mar,
    ior_mar,
    reading_apr,
    reading_date_apr,
    reading_postedby_apr,
    usage_apr,
    penalty_apr,
    bill_apr,
    totalbill_apr,
    paidamt_apr,
    datepaid_apr,
    dateposted_apr,
    postedby_apr,
    txrefnum_apr,
    ior_apr,
    reading_may,
    reading_date_may,
    reading_postedby_may,
    usage_may,
    penalty_may,
    bill_may,
    totalbill_may,
    paidamt_may,
    datepaid_may,
    dateposted_may,
    postedby_may,
    txrefnum_may,
    ior_may,
    reading_jun,
    reading_date_jun,
    reading_postedby_jun,
    usage_jun,
    penalty_jun,
    bill_jun,
    totalbill_jun,
    paidamt_jun,
    datepaid_jun,
    dateposted_jun,
    postedby_jun,
    txrefnum_jun,
    ior_jun,
    reading_jul,
    reading_date_jul,
    reading_postedby_jul,
    usage_jul,
    penalty_jul,
    bill_jul,
    totalbill_jul,
    paidamt_jul,
    datepaid_jul,
    dateposted_jul,
    postedby_jul,
    txrefnum_jul,
    ior_jul,
    reading_aug,
    reading_date_aug,
    reading_postedby_aug,
    usage_aug,
    penalty_aug,
    bill_aug,
    totalbill_aug,
    paidamt_aug,
    datepaid_aug,
    dateposted_aug,
    postedby_aug,
    txrefnum_aug,
    ior_aug,
    reading_sept,
    reading_date_sept,
    reading_postedby_sept,
    usage_sept,
    penalty_sept,
    bill_sept,
    totalbill_sept,
    paidamt_sept,
    datepaid_sept,
    dateposted_sept,
    postedby_sept,
    txrefnum_sept,
    ior_sept,
    reading_oct,
    reading_date_oct,
    reading_postedby_oct,
    usage_oct,
    penalty_oct,
    bill_oct,
    totalbill_oct,
    paidamt_oct,
    datepaid_oct,
    dateposted_oct,
    postedby_oct,
    txrefnum_oct,
    ior_oct,
    reading_nov,
    reading_date_nov,
    reading_postedby_nov,
    usage_nov,
    penalty_nov,
    bill_nov,
    totalbill_nov,
    paidamt_nov,
    datepaid_nov,
    dateposted_nov,
    postedby_nov,
    txrefnum_nov,
    ior_apr,
    reading_dec,
    reading_date_dec,
    reading_postedby_dec,
    usage_dec,
    penalty_dec,
    bill_dec,
    totalbill_dec,
    paidamt_dec,
    datepaid_dec,
    dateposted_dec,
    postedby_dec,
    txrefnum_dec,
    ior_dec,
    consumerid_id,
    amountpaid_str_apr,
    amountpaid_str_aug,
    amountpaid_str_dec,
    amountpaid_str_feb,
    amountpaid_str_jan,
    amountpaid_str_jul,
    amountpaid_str_jun,
    amountpaid_str_mar,
    amountpaid_str_may,
    amountpaid_str_nov,
    amountpaid_str_oct,
    amountpaid_str_sept,
    acc_rec_accountinfoid,
    amountpaid_history,
    datepaid_history,
    postedby_history,
    or_number_history,
    acc_rec_previous_reading,
]
barangay_record = [
    barangay_val,
    barangay_name,
    brgy_rec_year,
    total_due_ytd,
    total_paid_ytd,
    total_usage,
    total_due_january,
    total_paid_january,
    usage_january,
    total_due_february,
    total_paid_february,
    usage_february,
    total_due_march,
    total_paid_march,
    usage_march,
    total_due_april,
    total_paid_april,
    usage_april,
    total_due_may,
    total_paid_may,
    usage_may,
    total_due_june,
    total_paid_june,
    usage_june,
    total_due_july,
    total_paid_july,
    usage_july,
    total_due_august,
    total_paid_august,
    usage_august,
    total_due_september,
    total_paid_september,
    usage_september,
    total_due_october,
    total_paid_october,
    usage_october,
    total_due_november,
    total_paid_november,
    usage_november,
    total_due_december,
    total_paid_december,
    usage_december,
]
consumerinfo = [
    consumerid,
    cons_info_firstname,
    cons_info_middlename,
    cons_info_lastname,
    cons_info_birthday,
    mobilenumber,
    mobilenumber2,
    emailaddress,
    homeaddress,
    sex,
    installcount,
    profilepic,
    cons_info_barangay,
    sitio,
    oldconsumerid,
    cons_info_deleted_flag,
]
gettotalbill = [
    bill_id,
    con_id,
    currentdue,
    rateid,
    paid,
    current_reading,
    reading_date,
    previous_reading,
    consumption,
]
oldconsumerinfo = [
    old_con_id,
    old_firstname,
    old_middlename,
    old_lastname,
    con_category,
    old_meternumber,
    old_address,
]
payment_history = [
    pay_hist_id,
    amount,
    pay_hist_date,
    or_number,
    time,
    postedby,
    consumer,
    pay_hist_accountinfoid,
    pay_hist_meternumber,
    pay_hist_year,
]
ratestable = [
    rt_id,
    minimumreading,
    minimumreading_charge,
    rateafterminimum,
    ratepenalty,
    ratepenaltyfrequency,
    paymentchedday,
]
revenuecode = [
    revid,
    application_fee,
    mayors_permit,
    gravel_excavation,
    asphalted_road,
    cemented_road,
    additional_fee_pipe_of_20_lineal_feet,
    residentialservice_per_month,
    commercialservice_per_month,
    residentialservice_excess_per_cubicmeter,
    commercialservice_per_cubicmeter,
    drilling_from_mainline,
    reinstallation_fee,
    tapping_fee,
    repair_fee,
    transfer_fee,
    three_month_penalty,
    disconnection_after,
    send_disconnection_notice_after,
    fix_amount_penalty,
    penalty_after,
    percentage_penalty,
]
systemuser = [
    userid,
    password,
    su_firstname,
    su_middlename,
    su_mobilenumber,
    su_lastname,
    su_emailaddress,
    usertype,
    su_profilepic,
    approver_flag
]
yearly_records =[
    yr_year,
    total_due_ytd,
    yr_total_paid_ytd, 
    yr_total_usage, 
    yr_total_due_january,
    yr_total_paid_january,
    yr_usage_january,
    yr_total_due_february, 
    yr_total_paid_february,
    yr_usage_february, 
    yr_total_due_march, 
    yr_total_paid_march, 
    yr_usage_march, 
    yr_total_due_april, 
    yr_total_paid_april, 
    yr_usage_april, 
    yr_total_due_may, 
    yr_total_paid_may, 
    yr_usage_may, 
    yr_total_due_june, 
    yr_total_paid_june, 
    yr_usage_june, 
    yr_total_due_july, 
    yr_total_paid_july, 
    yr_usage_july, 
    yr_total_due_august, 
    yr_total_paid_august, 
    yr_usage_august, 
    yr_total_due_september, 
    yr_total_paid_september, 
    yr_usage_september, 
    yr_total_due_october, 
    yr_total_paid_october, 
    yr_usage_october, 
    yr_total_due_november, 
    yr_total_paid_november, 
    yr_usage_november, 
    yr_total_due_december, 
    yr_total_paid_december,
    yr_usage_december,
]
alltables = [
    accountinfo, 
    accountrecord,
    barangay_record,
    consumerinfo,
    gettotalbill,
    oldconsumerinfo,
    payment_history,
    ratestable,
    revenuecode,
    systemuser,
    yearly_records,
]

current_table = []
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="yjh434ctuG@-@",
    database="lgu_ginatilan_db"
)
mycursor = mydb.cursor()
def porter_in(request):
    col = 0
    for t in range(len(tablenames)):
        mycursor.execute("SELECT count(*) FROM information_schema.columns WHERE TABLE_NAME = '"+tablenames[t]+"';")
        for c in range(mycursor.fetchone()[0]):
            mycursor.execute("SELECT " + columnnames[col] + " FROM "+tablenames[t]+";")
            result=mycursor.fetchall()
            for x in result:
                alltables[t][c].append(x[0])
            col+=1
    
    current_table = rearrange('barangay_record')#change string parameter to desired table name reference in tablenames above
    porter_out(current_table)
    return render(request, "home.html")

def rearrange(var):
    arr = []
    mycursor.execute("SELECT count(*) FROM information_schema.columns WHERE TABLE_NAME = '"+var+"';")
    cols = mycursor.fetchone()[0]
    mycursor.execute("SELECT count(*) FROM "+var+";")
    rows = mycursor.fetchone()[0]
    for r in range(rows):
        inner = []
        for c in range(cols):
            inner.append(globals()[var][c][r])
        arr.append(inner)

    return arr

def porter_out(table):
    b_rec = BarangayRecord()
    for i in table:
        b_rec.barangay_val = i[0]
        b_rec.year = i[2]
        b_rec.total_due_jan = i[6]
        b_rec.total_paid_jan = i[7]
        b_rec.total_usage_jan = i[8]
        b_rec.total_due_feb = i[9]
        b_rec.total_paid_feb = i[10]
        b_rec.total_usage_feb = i[11]
        b_rec.total_due_mar = i[12]
        b_rec.total_paid_mar = i[13]
        b_rec.total_usage_mar = i[14]
        b_rec.total_due_apr = i[15]
        b_rec.total_paid_apr = i[16]
        b_rec.total_usage_apr = i[17]
        b_rec.total_due_may = i[18]
        b_rec.total_paid_may = i[19]
        b_rec.total_usage_may = i[20]
        b_rec.total_due_jun = i[21]
        b_rec.total_paid_jun = i[22]
        b_rec.total_usage_jun = i[23]
        b_rec.total_due_jul = i[24]
        b_rec.total_paid_jul = i[25]
        b_rec.total_usage_jul = i[26]
        b_rec.total_due_aug = i[27]
        b_rec.total_paid_aug = i[28]
        b_rec.total_usage_aug = i[29]
        b_rec.total_due_sept = i[30]
        b_rec.total_paid_sept = i[31]
        b_rec.total_usage_sept = i[32]
        b_rec.total_due_oct = i[33]
        b_rec.total_paid_oct = i[34]
        b_rec.total_usage_oct = i[35]
        b_rec.total_due_nov = i[36]
        b_rec.total_paid_nov = i[37]
        b_rec.total_usage_nov = i[38]
        b_rec.total_due_dec = i[39]
        b_rec.total_paid_dec = i[40]
        b_rec.total_usage_dec = i[41]
        b_rec.save()

#------------------JAZZY<3----------------------#

mycursor = mydb.cursor()
def porter_in(request):
    col = 0
    for t in range(len(tablenames)):
        mycursor.execute("SELECT count(*) FROM information_schema.columns WHERE TABLE_NAME = '"+tablenames[t]+"';")
        for c in range(mycursor.fetchone()[0]):
            mycursor.execute("SELECT " + columnnames[col] + " FROM "+tablenames[t]+";")
            result=mycursor.fetchall()
            for x in result:
                alltables[t][c].append(x[0])
            col+=1
    
    current_table = rearrange('ratestable')#change string parameter to desired table name reference in tablenames above
    porter_out(current_table)
    return render(request, "home.html")

def rearrange(var):
    arr = []
    mycursor.execute("SELECT count(*) FROM information_schema.columns WHERE TABLE_NAME = '"+var+"';")
    cols = mycursor.fetchone()[0]
    mycursor.execute("SELECT count(*) FROM "+var+";")
    rows = mycursor.fetchone()[0]
    for r in range(rows):
        inner = []
        for c in range(cols):
            inner.append(globals()[var][c][r])
        arr.append(inner)

    return arr

    
def porter_out(table):
    rt = Rates()
    for i in table:
        rt.minReading = i[0]
        rt.minReadingCharge = i[2]
        rt.rateAfterMin = i[3]
        rt.ratePenalty = i[4]
        rt.ratePenaltyFreq = i[5]
        rt.save()


#-----------------------------------#

        
def login(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, 'Logged in')
            return redirect('home')
        else:
            messages.error(request, "Invalid Username or Password")

    return render(request, 'login.html')


def home(request):
    return render(request, 'home.html')

def user_creation(request):
    form = SystemUserForm()
    if request.method == "POST":
        form = SystemUserForm(request.POST)
        if request.method == 'POST':
            is_admin = request.POST['admin']
            is_teller = request.POST['teller']
            is_supervisor = request.POST['supervisor']
            is_manager = request.POST['manager']
            is_meter = request.POST['meter']
            if form.is_valid():
                form.save()

                user = SystemUsers.objects.get(username=form.cleaned_data.get('username'))
                user.is_admin = is_admin
                user.is_teller = is_teller
                user.is_supervisor = is_supervisor
                user.is_manager = is_manager
                user.is_meter = is_meter
                user.save()

                return redirect('login')

    context = {
        'form':form, 
        'errors':form.errors,
    }
    return render(request, 'registration.html', context)