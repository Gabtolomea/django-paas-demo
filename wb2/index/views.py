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

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="yjh434ctuG@-@",
    database="lgu_ginatilan_db"
)


def landingpage(request):
    tablenames = [
        'accountinfo',
        'accountrecord',
        'barangay_record',
        'consumerinfo',
        'gettotalbill',
        'meterreadingmodification_table',
        'oldconsumerinfo',
        'payment_history',
        'ratestable',
        'revenuecode',
        'systemuser',
        'yearly_records'
    ]

    columnnames = [
        'accountinfoid',
        'firstname',
        'middlename',
        'lastname',
        'address',
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
        'txtrefnum_jan',
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
        'txtrefnum_feb',
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
        'txtrefnum_mar',
        'ior_mar',
        'reading_apr',
        'reading_postedby_apr',
        'usage_apr',
        'penalty_apr',
        'bill_apr',
        'totalbill_apr',
        'paidamt_apr',
        'datepaid_apr',
        'dateposted_apr',
        'postedby_apr',
        'txtrefnum_apr',
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
        'txtrefnum_jun',
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
        'txtrefnum_jul',
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
        'txtrefnum_aug',
        'ior_aug',
        'reading_sept',
        'reading_date_sept',
        'reading_postedby_sept',
        'usage_sept',
        'penalty_sept',
        'bill_sept',
        'totalbill_sept',
        'paidamt_sept',
        'totalbill_sept',
        'paidamt_sept',
        'datepaid_sept',
        'dateposted_sept',
        'postedby_sept',
        'txtrefnum_sept',
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
        'txtrefnum_oct',
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
        'txtrefnum_nov',
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
        'txtrefnum_dec',
        'ior_dec',

    ]

    accountinfoid = [],
    firstname = [],
    middlename = [],
    lastname = [],
    address = [],
    barangay = [],
    meternumber = [],
    initial_meter_reading = [],
    acc_info_rateid = [],
    status = [],
    duedate = [],
    consumerid_id = [],
    penalty_flag = [],
    deleted_flag = [],
    stop_meter_flag = [],

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
    txtrefnum_jan = []
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
    txtrefnum_feb = []
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
    txtrefnum_mar = []
    ior_mar = []
    reading_apr = []
    reading_postedby_apr = []
    usage_apr = []
    penalty_apr = []
    bill_apr = []
    totalbill_apr = []
    paidamt_apr = []
    datepaid_apr = []
    dateposted_apr = []
    postedby_apr = []
    txtrefnum_apr = []
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
    txtrefnum_jun = []
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
    txtrefnum_jul = []
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
    txtrefnum_aug = []
    ior_aug = []
    reading_sept = []
    reading_date_sept = []
    reading_postedby_sept = []
    usage_sept = []
    penalty_sept = []
    bill_sept = []
    totalbill_sept = []
    paidamt_sept = []
    totalbill_sept = []
    paidamt_sept = []
    datepaid_sept = []
    dateposted_sept = []
    postedby_sept = []
    txtrefnum_sept = []
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
    txtrefnum_oct = []
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
    txtrefnum_nov = []
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
    txtrefnum_dec = []
    ior_dec = []

    mycursor = mydb.cursor()
    columnname = ""
    for t in tablenames:
        tablename = t
        mycursor.execute("SELECT " + columnname + " FROM "+tablename)
        myresult = mycursor.fetchall()
        for x in myresult:
            accountinfoid.append(x[0])

    accountinfo = [
        accountinfoid,
        firstname,
        middlename,
        lastname,
        address,
        barangay,
        meternumber,
        initial_meter_reading,
        rateid,
        status,
        duedate,
        consumerid_id,
        penalty_flag,
        deleted_flag,
        stop_meter_flag
    ]
    """
    accountrecord
    barangay_record
    consumerinfo
    gettotalbill
    meterreadingmodification_table
    oldconsumerinfo
    payment_history
    ratestable
    revenuecode
    systemuser
    yearly_records"""

    context = {
        'accountinfo': accountinfo,

        # 'accountrecord':accountrecord,
        # 'barangay_record':barangay_record,
        # 'consumerinfo':consumerinfo,
        # 'gettotalbill':gettotalbill,
        # 'meterreadingmodification_table':meterreadingmodification_table,
        # 'oldconsumerinfo':oldconsumerinfo,
        # 'payment_history':payment_history,
        # 'ratestable':ratestable,
        # 'revenuecode':revenuecode,
        # 'systemuser':systemuser,
        # 'yearly_records':yearly_records,
    }

    return render(request, 'home.html', context)


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

    return render(request, 'login2.0.html')


def home(request):
    return render(request, 'home.html')
