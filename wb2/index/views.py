from multiprocessing import context
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
        'rt_id',
        'minimumreading',
        'minimumreading_charge',
        'rateafterminimum',
        'ratepenalty',
        'ratepenaltyfrequency',
        'paymentchedday',
        'revid',
        'application_fee',
        'mayors_permit',
        'gravel_excavation',
        'asphalted_road',
        'cemented_road',
        'additional_fee_pipe_of_20_lineal_feet',
        'residentialservice_per_month',
        'commercialservice_per_month',
        'residentialservice_excess_per_cubicmeter',
        'commercialservice_per_cubicmeter',
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
        'su_firstname',
        'su_middlename',
        'su_mobilenumber',
        'su_lastname',
        'su_emailaddress',
        'usertype',
        'su_profilepic',
        'approver_flag',
        'yr_year',
        'yr_total_paid_ytd', 
        'yr_total_usage', 
        'yr_total_due_january',
        'yr_total_paid_january',
        'yr_usage_january',
        'yr_total_due_february', 
        'yr_total_paid_february',
        'yr_usage_february', 
        'yr_total_due_march', 
        'yr_total_paid_march', 
        'yr_usage_march', 
        'yr_total_due_april', 
        'yr_total_paid_april', 
        'yr_usage_april', 
        'yr_total_due_may', 
        'yr_total_paid_may', 
        'yr_usage_may', 
        'yr_total_due_june', 
        'yr_total_paid_june', 
        'yr_usage_june', 
        'yr_total_due_july', 
        'yr_total_paid_july', 
        'yr_usage_july', 
        'yr_total_due_august', 
        'yr_total_paid_august', 
        'yr_usage_august', 
        'yr_total_due_september', 
        'yr_total_paid_september', 
        'yr_usage_september',
        'yr_total_due_october', 
        'yr_total_paid_october', 
        'yr_usage_october', 
        'yr_total_due_november', 
        'yr_total_paid_november', 
        'yr_usage_november', 
        'yr_total_due_december', 
        'yr_total_paid_december',
        'yr_usage_december',

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
        txtrefnum_jan,
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
        txtrefnum_feb,
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
        txtrefnum_mar,
        ior_mar,
        reading_apr,
        reading_postedby_apr,
        usage_apr,
        penalty_apr,
        bill_apr,
        totalbill_apr,
        paidamt_apr,
        datepaid_apr,
        dateposted_apr,
        postedby_apr,
        txtrefnum_apr,
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
        txtrefnum_jun,
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
        txtrefnum_jul,
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
        txtrefnum_aug,
        ior_aug,
        reading_sept,
        reading_date_sept,
        reading_postedby_sept,
        usage_sept,
        penalty_sept,
        bill_sept,
        totalbill_sept,
        paidamt_sept,
        totalbill_sept,
        paidamt_sept,
        datepaid_sept,
        dateposted_sept,
        postedby_sept,
        txtrefnum_sept,
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
        txtrefnum_oct,
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
        txtrefnum_nov,
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
        txtrefnum_dec,
        ior_dec,
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
    mycursor = mydb.cursor()

    for t in range(len(tablenames)):
        tablename = tablenames[t]
        print(type(tablename))
        mycursor.execute("SELECT count(*) FROM information_schema.columns WHERE table_name = "+tablenames[t])
        count = mycursor.fetchone()[0]
        print(count)
        for c in range(count):
            mycursor.execute("SELECT " + columnnames[c] + " FROM "+tablename)
            myresult = mycursor.fetchall()
            print(columnnames[c])

    

    context = {

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

    return render(request, 'login.html')

def home(request):
    return render(request, 'home.html')

def user_creation(request):
    form = SystemUserForm()
    if request.method == "POST":
        form = SystemUserForm(request.POST)
        if form.is_valid():
            form.save()

            return redirect('login')

    context = {
        'form':form, 
        'errors':form.errors,
    }
    return render(request, 'registration.html', context)