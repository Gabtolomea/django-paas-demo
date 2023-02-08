# import mysql.connector
from .models import *
from .colnames import *
from datetime import datetime
import math
import mysql.connector
import base64
from django.core.exceptions import ObjectDoesNotExist

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

mydb = mysql.connector.connect(
   host="localhost",
   user="root",
   password="yjh434ctuG@-@",
   database="lgu_ginatilan_db"
)
mycursor = mydb.cursor()


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
trans = Transactions()
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
reading_index = 6
date_index = 7
usage_index = 9
bill_index = 12
def porter_out(tables):
    global reading_index, date_index, usage_index, bill_index
    penalty = Penalty()
    penalty.penaltycode = 'P001'
    penalty.penalty_after = 0
    penalty.penalty_rate = 0
    penalty.daysappliedafter = 0
    penalty.penalty_info = ''
    penalty.save()
    print("porter out...barangays")
    for i in bar:
        b = Barangays()
        b.barangay = i
        b.save()
    print("porter out...rates")
    for i in tables[5]:
        rt_out(i)
    print("porter out...system users")
    for i in tables[6]:
        sys_user_out(i)
    print("porter out...consumers")
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
    print("porter out...transactions-billing")
    for i in tables[1]:
        if i[5] >= 2022:
            con = ConsumerInfo.objects.get(consumer_id=i[175])
            for m in range(1,13):
                if i[bill_index] != 0:
                    billing_out(con, i[1], i[reading_index], i[date_index], i[5], i[usage_index], i[bill_index], m)
            reading_index = 6
            date_index = 7
            usage_index = 9
            bill_index = 12
    print("porter out...transactions-payment")
    for i in range(len(tables[4])):
        if tables[4][i][2].month == 1:
            trans.month = 12
            trans.year = tables[4][i][2].year-1
        else:
            trans.month = tables[4][i][2].month-1
            trans.year = tables[4][i][2].year
        if trans.year >= 2022:
            trans.transactionid = tables[4][i][0]
            trans.date = tables[4][i][2]
            trans.acctID = ConsumerInfo.objects.get(consumer_id=tables[4][i][7])
            trans.transType = 'Payment'
            trans.payment = tables[4][i][1]
            trans.processedBy = tables[4][i][5]
            trans.or_number = tables[4][i][3]
            try:
                brec = BarangayRecord.objects.get(year=trans.year, barangaycode=ConsumerInfo.objects.get(consumer_id=tables[4][i][7]).installation_address)
                brec.__dict__[f"total_paid_{months[trans.month-1]}"] += trans.payment
            except ObjectDoesNotExist:
                brec = BarangayRecord()
                brec.barangayrec_id = f"{con.installation_address.id}-{trans.year}"
                brec.year = trans.year
                brec.barangaycode = con.installation_address
                brec.__dict__[f"total_paid_{months[trans.month-1]}"] = trans.payment
                brec.__dict__[f"total_usage_{months[trans.month-1]}"] = 0
                brec.__dict__[f"total_due_{months[trans.month-1]}"] = 0
            brec.save()
            trans.save()

   
def billing_out(con, rate, reading, date, year, usage, bill, month):
    global reading_index, date_index, usage_index, bill_index
    tran = Transactions()
    tran.acctID = con
    tran.contypeid = "C00"+rate
    tran.meterReading = reading
    date_str = date
    if date_str!=" " and date_str!="":
        try:
            tran.date = datetime.strptime(date_str, '%Y-%m-%d')
            tran.year = datetime.strptime(date_str, '%Y-%m-%d').year
        except ValueError:
            tran.date = datetime.strptime(date_str, '%m-%d-%Y')
            tran.year = datetime.strptime(date_str, '%m-%d-%Y').year
    tran.month = month
    tran.year = year
    tran.payment = 0
    tran.transType = 'Billing'
    prev = reading - usage
    if prev < 0:
        tran.prevReading = reading
        tran.processedBy = "System Adjustment"
    else:
        tran.prevReading = prev
    if bill < 0 or usage < 0:
        tran.usage = 0
        tran.bill = 0
        tran.processedBy = "System Adjustment"
    else:
        tran.usage = usage
        tran.bill = bill

    try:
        brec = BarangayRecord.objects.get(year=tran.year, barangaycode=con.installation_address)
        brec.__dict__[f"total_usage_{months[month-1]}"] += tran.usage
        brec.__dict__[f"total_due_{months[month-1]}"] += tran.bill
    except ObjectDoesNotExist:
        brec = BarangayRecord()
        brec.barangayrec_id = f"{con.installation_address.id}-{tran.year}"
        brec.year = tran.year
        brec.barangaycode = con.installation_address
        brec.__dict__[f"total_usage_{months[month-1]}"] = tran.usage
        brec.__dict__[f"total_due_{months[month-1]}"] = tran.bill
        brec.__dict__[f"total_paid_{months[month-1]}"] = 0

    reading_index += 13
    date_index += 13
    usage_index += 13
    bill_index += 13

    brec.save()
    tran.save()
    

def balance():
    for i in ConsumerInfo.objects.all():
        user = ConsumerInfo.objects.get(consumer_id = i.consumer_id)
        trans = Transactions.objects.filter(acctID = i.consumer_id)
        asc_trans = trans.order_by('year', 'month')
        bal = 0
        for i in range(len(asc_trans)):
            if asc_trans[i].transType == 'Billing':
                bal+=asc_trans[i].bill
            elif asc_trans[i].transType == 'Payment':
                bal=bal-asc_trans[i].payment
        user.current_bal = math.ceil(bal*100)/100
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
