# import mysql.connector
from .models import *
from .colnames import *
from datetime import datetime
import math
import mysql.connector
import base64
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned

tablenames = [
    "accountinfo",     #0
    "accountrecord",   #1
    "barangay_record", #2
    "consumerinfo",    #3
    "payment_history", #4
    "ratestable",      #5
    "systemuser",      #6
    # "yearly_records"
]
alltables = [
    accountinfo,
    accountrecord,
    barangay_record,
    consumerinfo,
    payment_history,
    ratestable,
    systemuser,
    #yearly_records,
]


sorted_tables = []

# mydb = mysql.connector.connect(
#    host="localhost",
#    user="root",
#    password="yjh434ctuG@-@",
#    database="lgu_ginatilan_db"
# )
# mycursor = mydb.cursor()


def porter_in():
    col = 0
    for t in range(len(tablenames)):
        mycursor.execute("SELECT count(*) FROM information_schema.columns WHERE TABLE_NAME = '"+tablenames[t]+"';")
        print(tablenames[t])
        for c in range(mycursor.fetchone()[0]):
            print(f"    ---{columnnames[col]}")
            mycursor.execute("SELECT " + columnnames[col] + " FROM "+tablenames[t]+";")
            result=mycursor.fetchall()
            for x in result:
                alltables[t][c].append(x[0])
            col+=1
        rearrange(tablenames[t])
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
    sorted_tables.append(arr)
con_info = ConsumerInfo()
b_rec = BarangayRecord()
rt = ConsumerType()
bar = [
    'Anao',
    'Cagsing',
    'Calabawan',
    'Cambagte',
    'Campisong',
    'Cañorong',
    'Guiwanon',
    'Looc',
    'Malatbo',
    'Mangaco',
    'Palanas',
    'Poblacion',
    'Salamanca',
    'San Roque',
    'Others...'
]
months = [
    'jan',
    'feb',
    'mar',
    'apr',
    'may',
    'jun',
    'jul',
    'aug',
    'sept',
    'oct',
    'nov',
    'dec'
]    
def porter_out(tables):
    penalty = Penalty()
    penalty.penaltycode = 'P001'
    penalty.penalty_after = 0
    penalty.penalty_rate = 0
    penalty.daysappliedafter = 0
    penalty.penalty_info = ''
    penalty.save()
    print("porting out...barangays")
    for i in bar:
        b = Barangays()
        b.barangay = i
        b.save()
    print("porting out...rates")
    for i in tables[5]:
        rt_out(i)
    print("porting out...system users")
    for i in tables[6]:
        sys_user_out(i)
    print("porting out...consumers")
    for i in range(len(tables[0])):
        con_info.consumer_id = tables[0][i][0]
        con_info.firstname = tables[0][i][1]
        con_info.lastname = tables[0][i][2]
        con_info.middlename = tables[0][i][13]
        con_info.installation_address = Barangays.objects.get(id=int(tables[0][i][4]))
        con_info.homeaddress = con_info.installation_address.barangay
        con_info.meternumber = tables[0][i][5]
        con_info.initialmeterreading = tables[0][i][6]
        con_info.contypeid = ConsumerType.objects.get(contypeid="C00"+tables[0][i][7]) 
        con_info.status = tables[0][i][8]
        con_info.penaltycounter = tables[0][i][11]
        con_info.stopmeterflag = tables[0][i][12]
        con_info.disconnectionflag = False
        con_info.deleteflag = tables[0][i][14]
        con_info.penaltycode = Penalty.objects.get(penaltycode="P001")
        con_info.save()
    print("porting out...transactions-received amount")
    for i in range(len(tables[4])):
        create = False
        try:
            Transactions.objects.get(or_number=tables[4][i][3])
        except ObjectDoesNotExist:
            trans = Transactions()
            create = True
        except MultipleObjectsReturned:
            pass
        if create:
            con = ConsumerInfo.objects.get(consumer_id=tables[4][i][7])
            if tables[4][i][2].month == 1:
                trans.month = 12
                trans.year = tables[4][i][2].year-1
            else:
                trans.month = tables[4][i][2].month-1
                trans.year = tables[4][i][2].year
            if trans.year >= 2019:
                trans.date = tables[4][i][2]
                trans.acctID = ConsumerInfo.objects.get(consumer_id=tables[4][i][7])
                trans.transType = 'Received Amount'
                trans.receivedamt = tables[4][i][1]
                trans.processedBy = tables[4][i][5]
                trans.or_number = tables[4][i][3]
                trans.save()

                # try:
                #     brec = BarangayRecord.objects.get(year=trans.year, barangaycode=con.installation_address)
                #     brec.__dict__[f"total_paid_{months[trans.month-1]}"] += trans.payment
                # except ObjectDoesNotExist:
                #     brec = BarangayRecord()
                #     brec.barangayrec_id = f"{con.installation_address.id}-{trans.year}"
                #     brec.year = trans.year
                #     brec.barangaycode = con.installation_address
                #     brec.__dict__[f"total_paid_{months[trans.month-1]}"] = trans.payment
                #     brec.__dict__[f"total_usage_{months[trans.month-1]}"] = 0
                #     brec.__dict__[f"total_due_{months[trans.month-1]}"] = 0
                # brec.save()
    for i in tables[1]:
        if i[5] >= 2019:
            reading_index = 6
            date_index = 7
            usage_index = 9
            bill_index = 12
            paidamt_index = 13
            con = ConsumerInfo.objects.get(consumer_id=i[175])
            for j in tables[1]:
                if j[175] == i[175]:
                    if j[5] == i[5]-1:
                        con.current_reading = j[149]
                        break
            if i[3]:
                con.excess = 0
            con.save()
            for m in range(1,13):
                if i[bill_index]:
                    billing_out(con, i[1], i[reading_index], i[date_index], i[5], i[usage_index], m, i[paidamt_index], i[bill_index])
                reading_index += 13
                date_index += 13
                usage_index += 13
                bill_index += 13
                paidamt_index += 13

    
def billing_out(con, rate, reading, date, year, usage, month, payment, bill):
    billingT = Transactions()
    billingT.acctID = con
    billingT.contypeid = "C00"+rate
    if con.current_reading:
        prev = con.current_reading
    else:
        prev = reading - usage
    if reading == 0:
        billingT.meterReading = prev
    else:
        billingT.meterReading = reading
    date_str = date
    if date_str!=" " and date_str!="":
        try:
            billingT.date = datetime.strptime(date_str, '%Y-%m-%d')
            billingT.year = datetime.strptime(date_str, '%Y-%m-%d').year
        except ValueError:
            billingT.date = datetime.strptime(date_str, '%m-%d-%Y')
            billingT.year = datetime.strptime(date_str, '%m-%d-%Y').year
    billingT.month = month
    billingT.year = year
    billingT.payment = 0
    billingT.transType = 'Billing'
    billingT.is_billpaid = payment!=0
    if prev < 0:
        billingT.prevReading = reading
        billingT.processedBy = "System Adjustment"
    else:
        billingT.prevReading = prev
    if usage < 0:
        billingT.usage = 0
        billingT.bill = 0
    else:
        if bill < 0:
            billingT.usage = 0
            billingT.bill = 0
        else:
            con.current_reading = billingT.meterReading
            con.save()
            billingT.usage = billingT.meterReading - prev
            rate = ConsumerType.objects.get(contypeid=billingT.contypeid)
            if billingT.usage <= rate.minReading:
                billingT.bill = rate.minReadingCharge
            else:
                billingT.bill = ((billingT.usage - rate.minReading) * rate.rateAfterMin) + rate.minReadingCharge
            try:
                brec = BarangayRecord.objects.get(year=billingT.year, barangaycode=con.installation_address)
                brec.__dict__[f"total_usage_{months[month-1]}"] += billingT.usage
                brec.__dict__[f"total_due_{months[month-1]}"] += billingT.bill
            except ObjectDoesNotExist:
                brec = BarangayRecord()
                brec.barangayrec_id = f"{con.installation_address.id}-{billingT.year}"
                brec.year = billingT.year
                brec.barangaycode = con.installation_address
                brec.__dict__[f"total_usage_{months[month-1]}"] = billingT.usage
                brec.__dict__[f"total_due_{months[month-1]}"] = billingT.bill
                brec.__dict__[f"total_paid_{months[month-1]}"] = 0
            brec.save()
    billingT.save()
    if payment:
        create = False
        try:
            paymentT = Transactions.objects.get(acctID_id = con, transType="Payment", year = year, month = month)
            create = True
        except ObjectDoesNotExist:
            paymentT = Transactions()
            create = True
        except MultipleObjectsReturned:
            pass
        if create:
            paymentT.date = date
            paymentT.acctID = con
            paymentT.transType = 'Payment'
            if payment > billingT.bill:
                con.excess += payment-billingT.bill
            elif payment < billingT.bill:
                con.excess -= billingT.bill-payment
            paymentT.payment = billingT.bill
            paymentT.month = month
            paymentT.year = year
            try:
                brec = BarangayRecord.objects.get(year=paymentT.year, barangaycode=con.installation_address)
                brec.__dict__[f"total_paid_{months[paymentT.month-1]}"] += paymentT.payment
            except ObjectDoesNotExist:
                brec = BarangayRecord()
                brec.barangayrec_id = f"{con.installation_address.id}-{paymentT.year}"
                brec.year = paymentT.year
                brec.barangaycode = con.installation_address
                brec.__dict__[f"total_paid_{months[paymentT.month-1]}"] = paymentT.payment
                brec.__dict__[f"total_usage_{months[paymentT.month-1]}"] = 0
                brec.__dict__[f"total_due_{months[paymentT.month-1]}"] = 0
            brec.save()
            con.save()
            paymentT.save()

def balance():
    for i in ConsumerInfo.objects.all():
        user = ConsumerInfo.objects.get(consumer_id = i.consumer_id)
        trans = Transactions.objects.filter(acctID = i.consumer_id)
        asc_trans = trans.order_by('year', 'month')
        bal = 0
        for i in range(len(asc_trans)):
            if asc_trans[i].transType == 'Billing':
                user.current_reading = asc_trans[i].meterReading
                bal+=asc_trans[i].bill
            elif asc_trans[i].transType == 'Payment':
                bal=bal-asc_trans[i].payment
        user.current_bal = math.ceil(bal*100)/100
        # if user.current_bal < 0:
        #     user.excess += (user.current_bal*-1)
        #     user.current_bal = 0
        if user.excess < 0:
            user.excess = 0
            user.current_bal += (user.excess*-1)
        user.save()


def get_cummulative(id):
    user = ConsumerInfo.objects.get(consumer_id = id)
    trans = Transactions.objects.filter(acctID = id, year = date.today().year)
    asc_trans = trans.order_by('month','transactionid')
    cum = 0
    for i in range(len(asc_trans)):
        if asc_trans[i].transType == 'Billing':
            cum+=asc_trans[i].bill
        elif asc_trans[i].transType == 'Payment':
            cum=cum-asc_trans[i].payment
    user.cummulative = math.ceil(cum*100)/100
    user.save()
    return math.ceil(cum*100)/100
def sys_user_out(i):
    sys_user = SystemUsers()
    sys_user.is_admin = False
    sys_user.is_teller = False
    sys_user.is_supervisor = False
    sys_user.is_manager = False
    sys_user.is_reader = False
    sys_user.username = i[0]
    passAscii = base64.b64decode(i[1])
    p = passAscii.decode("ascii")
    print(f'username: {i[0]} | password: {p}')
    sys_user.set_password(str(p))
    sys_user.first_name = i[2]
    sys_user.mid_name = i[3]
    sys_user.mobilenum = i[4]
    sys_user.last_name = i[5]
    sys_user.email = i[6]
    role = i[7]
    if '1' in role:
        sys_user.is_admin = True
    if '2' in role:
        sys_user.is_teller = True
    if '3' in role:
        sys_user.is_supervisor = True
    if '4' in role:
        sys_user.is_manager = True
    if '5' in role:
        sys_user.is_reader = True
    sys_user.authorizedapprover = i[9]
    sys_user.save()
def rt_out(i):
    rt.contypeid = "C00"+i[0]
    rt.minReading = i[1]
    rt.minReadingCharge = i[2]
    rt.rateAfterMin = i[3]
    if i[0] == '1':
        rt.contype = 'Residential'
    elif i[0] == '2':
        rt.contype = 'Commercial'
    rt.added_by = None
    rt.date_added=date.today()
    rt.date_mod = date.today()
    rt.save()
