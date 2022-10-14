# import mysql.connector
from .models import *
from .colnames import *
from datetime import datetime
import math
import mysql.connector

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
    # "yearly_records"
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
    #yearly_records,
]


sorted_tables = []

# mydb = mysql.connector.connect(
#     host="localhost",
#     user="root",
#     password="database2021",
#     database="lgu_ginatilan_db"
# )
# mycursor = mydb.cursor()
def porter_in():
    col = 0
    for t in range(len(tablenames)):
        mycursor.execute("SELECT count(*) FROM information_schema.columns WHERE TABLE_NAME = '"+tablenames[t]+"';")
        for c in range(mycursor.fetchone()[0]):
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
sys_user = SystemUsers()
rt = Rates()
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
    'San Roque'
]
usage_rec = usage_record()
def porter_out(tables):
    penalty = Penalty()
    penalty.penaltycode = 'P001'
    penalty.penalty_after = 0
    penalty.penalty_rate = 0
    penalty.penalty_info = ''
    penalty.save()
    for i in bar:
        b = Barangays()
        b.barangay = i
        b.save()
    for i in tables[2]:
        b_rec_out(i)
    for i in tables[7]:
        rt_out(i)
    for i in tables[9]:
        sys_user_out(i)
    for i in range(len(tables[3])):
        con_info.consumer_id = int(tables[3][i][0])
        con_info.firstname = tables[3][i][1]
        con_info.lastname = tables[3][i][2]
        con_info.middlename = tables[3][i][3]
        con_info.installation_address = Barangays.objects.get(id=tables[3][i][12])
        con_info.homeaddress = Barangays.objects.get(id=tables[3][i][12]).barangay
        con_info.meternumber = tables[0][i][5]
        con_info.initialmeterreading = tables[0][i][6]
        con_info.rateid = Rates.objects.get(rate_id=tables[0][i][7])
        con_info.penaltycode = Penalty.objects.get(penaltycode='P001')
        con_info.status = tables[0][i][8]
        con_info.penaltycounter = tables[0][i][11]
        con_info.stopmeterflag = tables[0][i][12]
        con_info.deleteflag = tables[0][i][14]
        con_info.save()
    for i in range(len(tables[6])):
        trans.transactionid = tables[6][i][0]
        trans.date = tables[6][i][2]
        arr = tables[6][i][7].split("-")
        trans.acctID = ConsumerInfo.objects.get(consumer_id=arr[0])
        trans.transType = 'Payment'
        trans.payment = tables[6][i][1]
        trans.processedBy = tables[6][i][5]
        trans.or_number = tables[6][i][3]
        trans.year = tables[6][i][2].year
        trans.month = tables[6][i][2].month
        trans.save()
    for i in tables[1]:
        usage_rec.accountid =	i[0]
        usage_rec.rateid = i[1]
        usage_rec.prevyeardue = i[2]
        usage_rec.excesspayment = i[3]
        usage_rec.commulative_bill = i[4]
        usage_rec.year = i[5]
        usage_rec.reading_jan = i[6]
        usage_rec.reading_date_jan = i[8-1]
        usage_rec.reading_postedby_jan =	i[9-1]
        usage_rec.usage_jan =	i[10-1]
        usage_rec.penalty_jan	= i[11-1]
        usage_rec.bill_jan = i[12-1]
        usage_rec.totalbill_jan =	i[13-1]
        usage_rec.paidamt_jan = i[14-1]
        usage_rec.datepaid_jan = i[15-1]
        usage_rec.dateposted_jan = i[16-1]
        usage_rec.postedby_jan = i[17-1]
        usage_rec.txrefnum_jan = i[18-1]
        usage_rec.ior_jan	= i[19-1]
        usage_rec.reading_feb = i[20-1]
        usage_rec.reading_date_feb = i[21-1]
        usage_rec.reading_postedby_feb = i[22-1]
        usage_rec.usage_feb = i[23-1]
        usage_rec.penalty_feb	= i[24-1]
        usage_rec.bill_feb = i[25-1]
        usage_rec.totalbill_feb = i[26-1]
        usage_rec.paidamt_feb = i[27-1]
        usage_rec.datepaid_feb =i [28-1]
        usage_rec.dateposted_feb =i [29-1]
        usage_rec.postedby_feb =i [30-1]
        usage_rec.txrefnum_feb =i [31-1]
        usage_rec.ior_feb = i[32-1]
        usage_rec.reading_mar = i[33-1]
        usage_rec.reading_date_mar = i[34-1]
        usage_rec.reading_postedby_mar = i[35-1]
        usage_rec.usage_mar = i[36-1]
        usage_rec.penalty_mar = i[37-1]
        usage_rec.bill_mar = i[38-1]
        usage_rec.totalbill_mar = i[39-1]
        usage_rec.paidamt_mar = i[40-1]
        usage_rec.datepaid_mar = i[41-1]
        usage_rec.dateposted_mar = i[42-1]
        usage_rec.postedby_mar = i[43-1]
        usage_rec.txrefnum_mar = i[44-1]
        usage_rec.ior_mar = i[45-1]
        usage_rec.reading_apr	= i[46-1]
        usage_rec.reading_date_apr = i[47-1]
        usage_rec.reading_postedby_apr = i[48-1]
        usage_rec.usage_apr = i[49-1]
        usage_rec.penalty_apr = i[50-1]
        usage_rec.bill_apr = i[51-1]
        usage_rec.totalbill_apr = i[52-1]
        usage_rec.paidamt_apr	= i[53-1]
        usage_rec.datepaid_apr = i[54-1]
        usage_rec.dateposted_apr = i[55-1]
        usage_rec.postedby_apr = i[56-1]
        usage_rec.txrefnum_apr = i[57-1]
        usage_rec.ior_apr = i[58-1]
        usage_rec.reading_may	= i[59-1]
        usage_rec.reading_date_may = i[60-1]
        usage_rec.reading_postedby_may = i[61-1]
        usage_rec.usage_may = i[62-1]
        usage_rec.penalty_may	= i[63-1]
        usage_rec.bill_may = i[64-1]
        usage_rec.totalbill_may = i[65-1]
        usage_rec.paidamt_may = i[66-1]
        usage_rec.datepaid_may = i[67-1]
        usage_rec.dateposted_may=	i[68-1]
        usage_rec.postedby_may = i[69-1]
        usage_rec.txrefnum_may = i[70-1]
        usage_rec.ior_may	= i[71-1]
        usage_rec.reading_jun	= i[72-1]
        usage_rec.reading_date_jun = i[73-1]
        usage_rec.reading_postedby_jun = i[74-1]
        usage_rec.usage_jun = i[75-1]
        usage_rec.penalty_jun	= i[76-1]
        usage_rec.bill_jun = i[77-1]
        usage_rec.totalbill_jun= i [78-1]
        usage_rec.paidamt_jun= i [79-1]
        usage_rec.datepaid_jun = i[80-1]
        usage_rec.dateposted_jun = i[81-1]
        usage_rec.postedby_jun = i[82-1]
        usage_rec.txrefnum_jun = i[83-1]
        usage_rec.ior_jun	= i[84-1]
        usage_rec.reading_jul= i [85-1]
        usage_rec.reading_date_jul = i[86-1]
        usage_rec.reading_postedby_jul = i[87-1]
        usage_rec.usage_jul = i[88-1]
        usage_rec.penalty_jul	= i[89-1]
        usage_rec.bill_jul = i[90-1]
        usage_rec.totalbill_jul = i[91-1]
        usage_rec.paidamt_jul	= i[92-1]
        usage_rec.datepaid_jul = i[93-1]
        usage_rec.dateposted_jul = i[94-1]
        usage_rec.postedby_jul = i[95-1]
        usage_rec.txrefnum_jul = i[96-1]
        usage_rec.ior_jul = i[97-1]
        usage_rec.reading_aug	= i[98-1]
        usage_rec.reading_date_aug = i[99-1]
        usage_rec.reading_postedby_aug = i[100-1]
        usage_rec.usage_aug = i[101-1]
        usage_rec.penalty_aug	= i[102-1]
        usage_rec.bill_aug = i[103-1]
        usage_rec.totalbill_aug = i[104-1]
        usage_rec.paidamt_aug	= i[105-1]
        usage_rec.datepaid_aug = i[106-1]
        usage_rec.dateposted_aug = i[107-1]
        usage_rec.postedby_aug = i[108-1]
        usage_rec.txrefnum_aug = i[109-1]
        usage_rec.ior_aug	= i[110-1]
        usage_rec.reading_sept = i[111-1]
        usage_rec.reading_date_sept = i[112-1]
        usage_rec.reading_postedby_sept = i[113-1]
        usage_rec.usage_sept = i[114-1]
        usage_rec.penalty_sept = i[115-1]
        usage_rec.bill_sept = i[116-1]
        usage_rec.totalbill_sept = i[117-1]
        usage_rec.paidamt_sept = i[118-1]
        usage_rec.datepaid_sept = i[119-1]
        usage_rec.dateposted_sept = i[120-1]
        usage_rec.postedby_sept = i[121-1]
        usage_rec.txrefnum_sept = i[122-1]
        usage_rec.ior_sept = i[123-1]
        usage_rec.reading_oct	= i[124-1]
        usage_rec.reading_date_oct = i[125-1]
        usage_rec.reading_postedby_oct = i[126-1]
        usage_rec.usage_oct = i[127-1]
        usage_rec.penalty_oct = i[128-1]
        usage_rec.bill_oct = i[129-1]
        usage_rec.totalbill_oct = i[130-1]
        usage_rec.paidamt_oct	= i[131-1]
        usage_rec.datepaid_oct = i[132-1]
        usage_rec.dateposted_oct = i[133-1]
        usage_rec.postedby_oct = i[134-1]
        usage_rec.txrefnum_oct = i[135-1]
        usage_rec.ior_oct = i[136-1]
        usage_rec.reading_nov	= i[137-1]
        usage_rec.reading_date_nov = i[138-1]
        usage_rec.reading_postedby_nov = i[139-1]
        usage_rec.usage_nov = i[140-1]
        usage_rec.penalty_nov = i[141-1]
        usage_rec.bill_nov = i[142-1]
        usage_rec.totalbill_nov = i[143-1]
        usage_rec.paidamt_nov	= i[144-1]
        usage_rec.datepaid_nov = i[145-1]
        usage_rec.dateposted_nov = i[146-1]
        usage_rec.postedby_nov = i[147-1]
        usage_rec.txrefnum_nov = i[148-1]
        usage_rec.ior_nov = i[149-1]
        usage_rec.reading_dec= i[150-1]
        usage_rec.reading_date_dec = i[151-1]
        usage_rec.reading_postedby_dec =	i[152-1]
        usage_rec.usage_dec	=i[153-1]
        usage_rec.penalty_dec	=i[154-1]
        usage_rec.bill_dec	=i[155-1]
        usage_rec.totalbill_dec=	i[156-1]
        usage_rec.paidamt_dec=	i[157-1]
        usage_rec.datepaid_dec	=i[158-1]
        usage_rec.dateposted_dec	=i[159-1]
        usage_rec.postedby_dec	=i[160-1]
        usage_rec.txrefnum_dec=	i[161-1]
        usage_rec.ior_dec	=i[162-1]
        arr= i[175].split('-')
        usage_rec.consumerid = ConsumerInfo.objects.get(consumer_id=arr[0])
        usage_rec.amountpaid_str_apr =	i[163]
        usage_rec.amountpaid_str_aug = i[164]
        usage_rec.amountpaid_str_dec = i[165]
        usage_rec.amountpaid_str_feb = i[166]
        usage_rec.amountpaid_str_jan = i[167]
        usage_rec.amountpaid_str_jul = i[168]
        usage_rec.amountpaid_str_jun = i[169]
        usage_rec.amountpaid_str_mar = i[170]
        usage_rec.amountpaid_str_may = i[171]
        usage_rec.amountpaid_str_nov = i[173-1]
        usage_rec.amountpaid_str_oct = i[174-1]
        usage_rec.amountpaid_str_sept = i[175-1]
        usage_rec.accountinfoid = i[176-1]
        usage_rec.amountpaid_history =i [177-1]
        usage_rec.datepaid_history = i[179-1]
        usage_rec.or_number_history = i[180-1]
        usage_rec.previous_reading = i[181-1]
        usage_rec.save()

def billing_out():
    u_rec = usage_record.objects.all()
    for u in u_rec:
        if u.totalbill_jan != 0:
            jan = Transactions()
            jan.acctID = u.consumerid
            jan.ratescode = u.rateid
            jan.meterReading = u.reading_jan
            date_str = u.reading_date_jan
            if date_str!=" " and date_str!="":
                jan.date = datetime.strptime(date_str, '%Y-%m-%d')
                jan.year = datetime.strptime(date_str, '%Y-%m-%d').year
            jan.month = 1
            jan.payment = 0
            jan.bill = u.totalbill_jan
            jan.payment = 0
            jan.transType = 'Billing'
            jan.usage = u.usage_jan
            jan.save()

        if u.totalbill_feb != 0:
            feb = Transactions()
            feb.acctID = u.consumerid
            feb.ratescode = u.rateid
            feb.meterReading = u.reading_feb
            date_str = u.reading_date_feb
            if date_str!=" " and date_str!="":
                feb.date = datetime.strptime(date_str, '%Y-%m-%d')
                feb.year = datetime.strptime(date_str, '%Y-%m-%d').year
            feb.month = 2
            feb.bill = u.totalbill_feb
            feb.payment = 0
            feb.transType = 'Billing'
            feb.usage = u.usage_feb
            feb.save()

        if u.totalbill_mar != 0:
            mar = Transactions()
            mar.acctID = u.consumerid
            mar.ratescode = u.rateid
            mar.meterReading = u.reading_mar
            date_str = u.reading_date_mar
            if date_str!=" " and date_str!="":
                mar.date = datetime.strptime(date_str, '%Y-%m-%d')
                mar.year = datetime.strptime(date_str, '%Y-%m-%d').year
            mar.month = 3
            mar.bill = u.totalbill_mar
            mar.payment = 0
            mar.transType = 'Billing'
            mar.usage = u.usage_mar
            mar.save()

        if u.totalbill_apr != 0:
            apr = Transactions()
            apr.acctID = u.consumerid
            apr.ratescode = u.rateid
            apr.meterReading = u.reading_apr
            date_str = u.reading_date_apr
            if date_str!=" " and date_str!="":
                apr.date = datetime.strptime(date_str, '%Y-%m-%d')
                apr.year = datetime.strptime(date_str, '%Y-%m-%d').year
            apr.month = 4
            apr.bill = u.totalbill_apr
            apr.payment = 0
            apr.transType = 'Billing'
            apr.usage = u.usage_apr
            apr.save()

        if u.totalbill_may != 0:
            may = Transactions()
            may.acctID = u.consumerid
            may.ratescode = u.rateid
            may.meterReading = u.reading_may
            date_str = u.reading_date_may
            if date_str!=" " and date_str!="":
                may.date = datetime.strptime(date_str, '%Y-%m-%d')
                may.year = datetime.strptime(date_str, '%Y-%m-%d').year
            may.month = 5
            may.bill = u.totalbill_may
            may.payment = 0
            may.transType = 'Billing'
            may.usage = u.usage_may
            may.save()

        if u.totalbill_jun != 0:
            jun = Transactions()
            jun.acctID = u.consumerid
            jun.ratescode = u.rateid
            jun.meterReading = u.reading_jun
            date_str = u.reading_date_jun
            if date_str!=" " and date_str!="":
                jun.date = datetime.strptime(date_str, '%Y-%m-%d')
                jun.year = datetime.strptime(date_str, '%Y-%m-%d').year
            jun.month = 6
            jun.bill = u.totalbill_jun
            jun.payment = 0
            jun.transType = 'Billing'
            jun.usage = u.usage_jun
            jun.save()

        if u.totalbill_jul != 0:
            jul = Transactions()
            jul.acctID = u.consumerid
            jul.ratescode = u.rateid
            jul.meterReading = u.reading_jul
            date_str = u.reading_date_jul
            if date_str!=" " and date_str!="":
                jul.date = datetime.strptime(date_str, '%Y-%m-%d')
                jul.year = datetime.strptime(date_str, '%Y-%m-%d').year
            jul.month = 7
            jul.bill = u.totalbill_jul
            jul.payment = 0
            jul.transType = 'Billing'
            jul.usage = u.usage_jul
            jul.save()

        if u.totalbill_aug != 0:
            aug = Transactions()
            aug.acctID = u.consumerid
            aug.ratescode = u.rateid
            aug.meterReading = u.reading_aug
            date_str = u.reading_date_aug
            if date_str!=" " and date_str!="":
                aug.date = datetime.strptime(date_str, '%Y-%m-%d')
                aug.year = datetime.strptime(date_str, '%Y-%m-%d').year
            aug.month = 8
            aug.bill = u.totalbill_aug
            aug.payment = 0
            aug.transType = 'Billing'
            aug.usage = u.usage_aug
            aug.save()

        if u.totalbill_sept != 0:
            sept = Transactions()
            sept.acctID = u.consumerid
            sept.ratescode = u.rateid
            sept.meterReading = u.reading_sept
            date_str = u.reading_date_sept
            if date_str!=" " and date_str!="":
                sept.date = datetime.strptime(date_str, '%Y-%m-%d')
                sept.year = datetime.strptime(date_str, '%Y-%m-%d').year
            sept.month = 9
            sept.bill = u.totalbill_sept
            sept.payment = 0
            sept.transType = 'Billing'
            sept.usage = u.usage_sept
            sept.save()

        if u.totalbill_oct != 0:
            oct = Transactions()
            oct.acctID = u.consumerid
            oct.ratescode = u.rateid
            oct.meterReading = u.reading_oct
            date_str = u.reading_date_oct
            if date_str!=" " and date_str!="":
                oct.date = datetime.strptime(date_str, '%Y-%m-%d')
                oct.year = datetime.strptime(date_str, '%Y-%m-%d').year
            oct.month = 10
            oct.bill = u.totalbill_oct
            oct.payment = 0
            oct.transType = 'Billing'
            oct.usage = u.usage_oct
            oct.save()


        if u.totalbill_nov != 0:
            nov = Transactions()
            nov.acctID = u.consumerid
            nov.ratescode = u.rateid
            nov.meterReading = u.reading_nov
            date_str = u.reading_date_nov
            if date_str!=" " and date_str!="":
                nov.date = datetime.strptime(date_str, '%Y-%m-%d')
                nov.year = datetime.strptime(date_str, '%Y-%m-%d').year
            nov.month = 11
            nov.bill = u.totalbill_nov
            nov.payment = 0
            nov.transType = 'Billing'
            nov.usage = u.usage_nov
            nov.save()

        if u.totalbill_dec != 0:
            dec = Transactions()
            dec.acctID = u.consumerid
            dec.ratescode = u.rateid
            dec.meterReading = u.reading_dec
            date_str = u.reading_date_dec
            if date_str!=" " and date_str!="":
                dec.date = datetime.strptime(date_str, '%Y-%m-%d')
                dec.year = datetime.strptime(date_str, '%Y-%m-%d').year-1
            dec.month = 12
            dec.bill = u.totalbill_dec
            dec.payment = 0
            dec.transType = 'Billing'
            dec.usage = u.usage_dec
            dec.save()

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
    sys_user.is_admin = False
    sys_user.is_teller = False
    sys_user.is_supervisor = False
    sys_user.is_manager = False
    sys_user.is_reader = False
    sys_user.username = i[0]
    sys_user.password = i[1]
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
    sys_user.profilepic = i[8]
    sys_user.authorizedapprover = i[9]
    sys_user.save()
def rt_out(i):
    rt.rate_id = int(i[0])
    rt.minReading = i[1]
    rt.minReadingCharge = i[2]
    rt.rateAfterMin = i[3]
    rt.ratePenalty = i[4]
    rt.ratePenaltyFreq = i[5]
    if i[0] == '1':
        rt.connectionType = 'Residential'
    elif i[0] == '2':
        rt.connectionType = 'Commercial'
    rt.added_by = None
    rt.date_added=date.today()
    rt.date_mod = date.today()
    rt.save()
def b_rec_out(i):
    b_rec.barangayrec_id = i[0]
    arr = i[0].split('-')
    b_rec.barangaycode = Barangays.objects.get(id=int(arr[0]))
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
