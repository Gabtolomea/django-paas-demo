import uuid
import mysql.connector
import pandas as pd
import time
from .models import *
from django.core.exceptions import ObjectDoesNotExist
import os
import math
import random
import string
import math
import datetime
from datetime import datetime
from .dataporter import *
import time

def n_int(var):
    if var is None:
        return 0
    else:
        return var

def n_str(var):
    if var is None:
        return ''
    else:
        return var

def str_int(var):
    if var == '':
        return 0
    else:
        return int(var)
def camelize():
    cons = ConsumerInfo.objects.all()
    for c in cons:
        c.firstname = c.firstname.title()
        c.lastname = c.lastname.title()
        c.middlename = c.middlename.title()
        c.save()
def enye(cons):
    for c in cons:
        chars = ["ã‘","ã±"]
        for char in chars:
            if char in c.firstname:
                c.firstname = c.firstname.replace(char, "ñ")
            if char in c.lastname:
                c.lastname = c.lastname.replace(char, "ñ")
            if char in c.middlename:
                c.middlename = c.middlename.replace(char, "ñ")
            c.save()
def capitalize():
    cons = ConsumerInfo.objects.all()
    for c in cons:
        c.firstname = c.firstname.upper()
        c.lastname = c.lastname.upper()
        c.middlename = c.middlename.upper()
        c.save()
def years(id):
    years = []
    alltrans = Transactions.objects.filter(acctID=id, transType='Billing') | Transactions.objects.filter(acctID=id, transType='Reset Meter')
    for i in alltrans:
        if i.date.year not in years:
            years.append(i.date.year)
    if datetime.today().year not in years:
        years.append(datetime.today().year)
    return years
def last_reading(id, year, mo):
    allyears = years(id)
    allyears.sort(reverse=True)
    fyears = [item for item in allyears if item <= year]
    for i in fyears:
        for j in reversed(range(1,mo)):
            try:
                lasttran = Transactions.objects.get(acctID=id, transType='Billing', year=i, month=j)
                lastreading = lasttran.meterReading
                return lastreading
            except ObjectDoesNotExist:
                pass
        mo = 13
    return 0

def create_brec(address_id, year):
    con_b_rec = BarangayRecord()  
    con_b_rec.barangayrec_id = f"{address_id}-{year}"
    con_b_rec.barangaycode = Barangays.objects.get(id=address_id)
    con_b_rec.year = year
    con_b_rec.total_due_jan = 0
    con_b_rec.total_due_feb = 0
    con_b_rec.total_due_mar = 0
    con_b_rec.total_due_apr = 0
    con_b_rec.total_due_may = 0
    con_b_rec.total_due_jun = 0
    con_b_rec.total_due_jul = 0
    con_b_rec.total_due_aug = 0
    con_b_rec.total_due_sept = 0
    con_b_rec.total_due_oct = 0
    con_b_rec.total_due_nov = 0
    con_b_rec.total_due_dec = 0
    con_b_rec.total_paid_jan = 0
    con_b_rec.total_paid_feb = 0
    con_b_rec.total_paid_mar = 0
    con_b_rec.total_paid_apr = 0
    con_b_rec.total_paid_may = 0
    con_b_rec.total_paid_jun = 0
    con_b_rec.total_paid_jul = 0
    con_b_rec.total_paid_aug = 0
    con_b_rec.total_paid_sept = 0
    con_b_rec.total_paid_oct = 0
    con_b_rec.total_paid_nov = 0
    con_b_rec.total_paid_dec = 0
    con_b_rec.total_usage_jan = 0
    con_b_rec.total_usage_feb = 0
    con_b_rec.total_usage_mar = 0
    con_b_rec.total_usage_apr = 0
    con_b_rec.total_usage_may = 0
    con_b_rec.total_usage_jun = 0
    con_b_rec.total_usage_jul = 0
    con_b_rec.total_usage_aug = 0
    con_b_rec.total_usage_sept = 0
    con_b_rec.total_usage_oct = 0
    con_b_rec.total_usage_nov = 0
    con_b_rec.total_usage_dec = 0
    return con_b_rec
def get_balance(id):
    user = ConsumerInfo.objects.get(consumer_id = id)
    trans = Transactions.objects.filter(acctID = id)
    asc_trans = trans.order_by('year', 'month','transactionid')
    bal = 0
    for i in range(len(asc_trans)):
        if asc_trans[i].transType == 'Billing':
            bal+=asc_trans[i].bill
        elif asc_trans[i].transType == 'Payment':
            bal-=asc_trans[i].payment
        elif asc_trans[i].transType == 'Penalty':
            bal+=asc_trans[i].bill
        elif asc_trans[i].transType == 'Discount':
            bal-=asc_trans[i].payment
    try:
        user.current_reading = trans.filter(transType='Billing').order_by('-year', '-month')[0].meterReading
    except IndexError:
        pass
    user.current_bal = math.ceil(bal*100)/100
    if user.current_bal < 0:
        user.excess += (user.current_bal*-1)
        user.current_bal = 0
    if user.excess < 0:
        user.excess = 0
        user.current_bal += (user.excess*-1)
    user.save()


def gen_token():
    nums = [str(x) for x in range(10)]
    alphabet = list(string.ascii_lowercase)
    choices = nums + alphabet
    token = ""
    d = datetime.now().timestamp()
    random.seed(d)
    for i in range(10):
        char = random.choice(choices)
        token+=(char)
    return token

def spz():
    allzerobills = Transactions.objects.filter(transType="Billing", is_billpaid = False, bill = 0)
    for i in allzerobills:
        i.is_billpaid = True
        i.save()

def sxz():
    allconsumers = ConsumerInfo.objects.all()
    for i in allconsumers:
        i.excess = 0
        i.save()
def portfromcsv():
    df = pd.read_csv("21723-latesttransactions.csv")
    arr_df = df.to_numpy()
    class billings():
        def __init__(self, transid, date,transtype, reading,prevreading, usage, contype, disc, bill, month, year, payment, pb, ornum, conid):
            self.transid = int(transid)
            self.date = date
            self.reading = int(reading)
            self.payment = int(payment)
            self.pb = pb
            self.ornum = ornum
            self.transtype = transtype
            self.month = int(month)
            self.conid = conid
            self.year = int(year)
            self.prevreading = int(prevreading)
            self.usage = int(usage)
            self.contype = contype
            self.disc = disc
            self.bill = int(bill)
    class payments():
        def __init__(self, disc, month, year, payment, pb, ornum, conid):
            self.payment = int(payment)
            self.pb = pb
            self.ornum = ornum
            self.month = int(month)
            self.conid = conid
            self.year = int(year)
            self.disc = disc
    new_billings = []
    new_payments = []
    for i in arr_df:
        # print(i)
        if i[2] == "Billing":
            b = billings(i[0],i[1],i[2],i[3],i[4],i[5],i[6],i[7],i[8],i[10],i[11],i[13],i[14],i[15],i[16])
            new_billings.append(b)
        elif i[2] == "Payment":
            p = payments(i[7],i[10],i[11],i[13],i[14],i[15],i[16])
            new_payments.append(p)
    for i in new_billings:
        con = ConsumerInfo.objects.get(consumer_id=i.conid)
        try:
            bulkinputreading(con, i.year, i.reading, i.pb, i.month)
        except MultipleObjectsReturned:
            pass
    for i in new_payments:
        bulkpayment(i.payment, i.ornum, i.disc, i.pb, i.conid, i.month, i.year)
def bulkpayment(amount, or_num, dis_code, pb, id, month, year):
    if amount != 0:
        consumer = ConsumerInfo.objects.get(consumer_id=id)
        con_bar = consumer.installation_address
        try:
            con_b_rec = BarangayRecord.objects.get(barangaycode_id=con_bar, year=year)
        except ObjectDoesNotExist:
            con_b_rec = create_brec(consumer.installation_address_id, year)
        rt = Transactions()
        rt.receivedamt = amount
        rt.acctID = consumer
        rt.transType = "Received Amount"
        rt.date = datetime.today()
        rt.year = year
        rt.month = month
        rt.processedBy = pb
        rt.or_number = or_num
        rt.save()
        consumer.excess += amount
        consumer.save()
        if consumer.excess > 0:
            unsettled = Transactions.objects.filter(acctID_id=consumer, transType="Billing", is_billpaid=False).order_by('-year', '-month')
            if unsettled:
                for i in unsettled:
                    if consumer.excess>=i.bill:
                        ex = consumer.excess - i.bill
                        pt = Transactions()
                        pt.acctID = consumer
                        pt.transType = "Payment"
                        pt.date = datetime.today()
                        pt.year = i.year
                        pt.month = i.month
                        pt.payment = i.bill
                        pt.save()
                        i.is_billpaid = True
                        i.save()
                        consumer.excess = ex
                    else:
                        break
                consumer.save()
        try:
            discount = Discount.objects.get(discountcode=dis_code)
        except ObjectDoesNotExist:
            pass
        else:
            dt = Transactions()
            dt.acctID = consumer
            dt.transType = "Discount"
            dt.date = datetime.today()
            dt.year = year
            dt.month = month
            dt.processedBy = pb
            dt.discountcode = discount.discountcode
            dt.payment = amount*(discount.discount_rate/100)
            amount -= amount*(discount.discount_rate/100)
            dt.save()
            rt.discountcode = dt.transactionid
            rt.processedBy = pb.username
            rt.save()
        get_balance(id)
        match month:
            case 1:
                con_b_rec.total_paid_jan += amount
            case 2:
                con_b_rec.total_paid_feb += amount
            case 3:
                con_b_rec.total_paid_mar += amount
            case 4:
                con_b_rec.total_paid_apr += amount
            case 5:
                con_b_rec.total_paid_may += amount
            case 6:
                con_b_rec.total_paid_jun += amount
            case 7:
                con_b_rec.total_paid_jul += amount
            case 8:
                con_b_rec.total_paid_aug += amount
            case 9:
                con_b_rec.total_paid_sept += amount
            case 10:
                con_b_rec.total_paid_oct += amount
            case 11:
                con_b_rec.total_paid_nov += amount
            case 12:
                con_b_rec.total_paid_dec += amount
        con_b_rec.save()

def bulkinputreading(consumer, year, reading, pb, d):
    try:
        con_b_rec = BarangayRecord.objects.get(barangaycode_id=consumer.installation_address_id, year=year)
    except ObjectDoesNotExist:
        con_b_rec = create_brec(consumer.installation_address_id, year)
        
    bill = 0
    usage = 0
    if reading != 0:
        try:
            billtran = Transactions.objects.get(acctID=consumer.consumer_id, transType='Billing', year=year, month=d)
            try:
                mo = d + 1
                ye = year
                if d == 12:
                    mo = 1
                    ye += 1
                next = Transactions.objects.get(acctID=consumer.consumer_id, transType='Billing', year=ye, month=mo)
                next.prevReading = reading
                next.usage = next.meterReading - reading
                next.save()
            except ObjectDoesNotExist:
                pass
            billtran.meterReading = reading
            billtran.date = datetime.today()
            billtran.usage = reading - billtran.prevReading
            usage = billtran.usage
            rate = ConsumerType.objects.get(contypeid=billtran.contypeid)
            dif = billtran.bill
            if billtran.usage <= rate.minReading:
                billtran.bill = rate.minReadingCharge
            else:
                billtran.bill = ((billtran.usage - rate.minReading) * rate.rateAfterMin) + rate.minReadingCharge
            billtran.processedBy = str(pb)
            billtran.save()
            dif = billtran.bill - dif
            try:
                paymentT = Transactions.objects.get(acctID_id=consumer.consumer_id, transType='Payment', year=ye, month=d)
                if dif:
                    paymentT.payment = paymentT.payment + dif
                    consumer.excess = consumer.excess - dif
                    consumer.current_bal = consumer.current_bal - dif
                paymentT.save()
                consumer.save()
            except ObjectDoesNotExist:
                pass
        except ObjectDoesNotExist:
            lastreading = consumer.current_reading
            bill = 0
            billtran = Transactions()
            billtran.acctID = consumer
            billtran.transType = 'Billing'
            billtran.date = datetime.today()
            billtran.month = d
            if billtran.month == 0:
                billtran.month = 12
            billtran.year = year
            billtran.meterReading = reading
            billtran.prevReading = lastreading
            billtran.usage = reading - lastreading
            usage = billtran.usage
            billtran.contypeid = consumer.contypeid_id
            rate = ConsumerType.objects.get(contypeid=consumer.contypeid_id)
            if billtran.usage <= rate.minReading:
                billtran.bill = rate.minReadingCharge
            else:
                bill = ((billtran.usage - rate.minReading) * rate.rateAfterMin) + rate.minReadingCharge
                billtran.bill = bill
            billtran.payment = 0
            billtran.processedBy = pb
            billtran.save()
            try:
                mo = d + 1
                ye = year
                if d == 12:
                    mo = 1
                    ye += 1
                next = Transactions.objects.get(acctID=consumer.consumer_id, transType='Billing', year=ye, month=mo)
                next.usage = next.meterReading - reading
                next.save()
            except ObjectDoesNotExist:
                pass
        if consumer.excess > 0:
            unsettled = Transactions.objects.filter(acctID_id=consumer, transType="Billing", is_billpaid=False).order_by('-year', '-month')
            if unsettled:
                for u in unsettled:
                    if consumer.excess>=u.bill:
                        ex = consumer.excess - u.bill
                        pt = Transactions()
                        pt.acctID = consumer
                        pt.transType = "Payment"
                        pt.date = datetime.today()
                        pt.year = u.year
                        pt.month = u.month
                        pt.payment = u.bill
                        pt.save()
                        u.is_billpaid = True
                        u.save()
                        consumer.excess = ex
                        consumer.save()
                    else:
                        consumer.save()
                        break
    match d:
        case 1:
            con_b_rec.total_due_jan += bill
            con_b_rec.total_usage_jan += usage
        case 2:
            con_b_rec.total_due_feb += bill
            con_b_rec.total_usage_feb += usage
        case 3:
            con_b_rec.total_due_mar += bill
            con_b_rec.total_usage_mar += usage
        case 4:
            con_b_rec.total_due_apr += bill
            con_b_rec.total_usage_apr += usage
        case 5:
            con_b_rec.total_due_may += bill
            con_b_rec.total_usage_may += usage
        case 6:
            con_b_rec.total_due_jun += bill
            con_b_rec.total_usage_jun += usage
        case 7:
            con_b_rec.total_due_jul += bill
            con_b_rec.total_usage_jul += usage
        case 8:
            con_b_rec.total_due_aug += bill
            con_b_rec.total_usage_aug += usage
        case 9:
            con_b_rec.total_due_sept += bill
            con_b_rec.total_usage_sept += usage
        case 10:
            con_b_rec.total_due_oct += bill
            con_b_rec.total_usage_oct += usage
        case 11:
            con_b_rec.total_due_nov += bill
            con_b_rec.total_usage_nov += usage
        case 12:
            con_b_rec.total_due_dec += bill
            con_b_rec.total_usage_dec += usage
    
    con_b_rec.save()
    get_balance(consumer.consumer_id)


def dump_database():
    cnx = mysql.connector.connect(
        user='root',
        password='jazfer',
        host='localhost',
        port=3307,
        database='wb2'
    )

    cursor = cnx.cursor()

    cursor.execute("SHOW TABLES")
    tables = cursor.fetchall()

    timestamp = datetime.now().strftime("%Y.%m.%d-%H.%M")
    print(timestamp)
    directory = 'C:/Users/CTU/Downloads/Dump/'
    directory = f'{directory}{timestamp}/'
    os.makedirs(directory, exist_ok=True) 
    dump_file_path = f'{directory}wb2_data_dump.sql'
    
    if os.path.exists(dump_file_path):
        os.remove(dump_file_path)

    with open(dump_file_path, 'w', buffering=1000000) as dump_file:
        print("Dumping...")

        dump_file.write(f"DROP DATABASE IF EXISTS `wb2`;\n\n")
        dump_file.write(f"CREATE DATABASE IF NOT EXISTS `wb2`;\n\n")
        dump_file.write(f"USE `wb2`;\n\n")
        dump_file.write(f"SET FOREIGN_KEY_CHECKS=0;\n\n")

        print("Success...")

    cursor.close()
    cnx.close()
