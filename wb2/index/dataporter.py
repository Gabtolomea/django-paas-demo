import mysql.connector
from .models import *
from .colnames import *
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
sorted_tables = []
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="yjh434ctuG@-@",
    database="lgu_ginatilan_db"
)
mycursor = mydb.cursor()
def porter():
    # r = Rates.objects.get(rateid = str(1))
    # print(r)
    porter_in()
    porter_out(sorted_tables)
    
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
        con_info.consumer_id = tables[3][i][0]
        con_info.firstname = tables[3][i][1]
        con_info.lastname = tables[3][i][2]
        con_info.middlename = tables[3][i][3]
        con_info.barangaycode = Barangays.objects.get(id=tables[3][i][12])
        con_info.meternumber = tables[0][i][5]
        con_info.initialmeterreading = tables[0][i][6]
        con_info.rateid = Rates.objects.get(rateid=tables[0][i][7])
        con_info.status = tables[0][i][8]
        con_info.penaltyflag = tables[0][i][11]
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
        trans.save()


    for i in tables[1]:
        usage_rec.accountid = i[0]
        usage_rec.rateid = i[1]
        usage_rec.prevyeardue = i[2]
        usage_rec.excesspayment = i[3]
        usage_rec.commulative_bill = i[4]
        usage_rec.year = i[5]
        usage_rec.consumerid = ConsumerInfo.objects.get(consumer_id=i[6])
        usage_rec.accountinfoid = i[7]
        usage_rec.amountpaid_history = i[8]
        usage_rec.datepaid_history = i[9]
        usage_rec.postedby_history = i[10]
        usage_rec.or_number_history = i[11]
        usage_rec.previous_reading = i[12]
        usage_rec.reading_jan = i[13]
        usage_rec.reading_date_jan = i[14]
        usage_rec.reading_postedby_jan = i[15]
        usage_rec.usage_jan = i[16]
        usage_rec.penalty_jan = i[17]
        usage_rec.bill_jan = i[18]
        usage_rec.totalbill_jan = i[19]
        usage_rec.paidamt_jan = i[20]
        usage_rec.datepaid_jan = i[21]
        usage_rec.dateposted_jan = i[22]
        usage_rec.postedby_jan = i[23]
        usage_rec.txrefnum_jan = i[24]
        usage_rec.ior_jan = i[25]
        usage_rec.amountpaid_str_jan = i[26]

        
        usage_rec.reading_feb = i[27]
        usage_rec.reading_date_feb = i[28]
        usage_rec.reading_postedby_feb = i[29]
        usage_rec.usage_feb = i[30]
        usage_rec.penalty_feb = i[31]
        usage_rec.bill_feb = i[32]
        usage_rec.totalbill_feb = i[33]
        usage_rec.paidamt_feb = i[34]
        usage_rec.datepaid_feb = i[35]
        usage_rec.dateposted_feb = i[36]
        usage_rec.postedby_feb = i[37]
        usage_rec.txrefnum_feb = i[38]
        usage_rec.ior_feb = i[39]
        usage_rec.amountpaid_str_feb = i[40]

        usage_rec.reading_mar = i[41]
        usage_rec.reading_date_mar = i[42]
        usage_rec.reading_postedby_mar = i[43]
        usage_rec.usage_mar = i[44]
        usage_rec.penalty_mar = i[45]
        usage_rec.bill_mar = i[46]
        usage_rec.totalbill_mar = i[47]
        usage_rec.paidamt_mar = i[48]
        usage_rec.datepaid_mar = i[49]
        usage_rec.dateposted_mar = i[50]
        usage_rec.postedby_mar = i[51]
        usage_rec.txrefnum_mar = i[52]
        usage_rec.ior_mar = i[53]
        usage_rec.amountpaid_str_mar = i[54]

        usage_rec.reading_apr = i[55]
        usage_rec.reading_date_apr = i[56]
        usage_rec.reading_postedby_apr = i[57]
        usage_rec.usage_apr = i[58]
        usage_rec.penalty_apr = i[59]
        usage_rec.bill_apr = i[60]
        usage_rec.totalbill_apr = i[61]
        usage_rec.paidamt_apr = i[62]
        usage_rec.datepaid_apr = i[63]
        usage_rec.dateposted_apr = i[64]
        usage_rec.postedby_apr = i[65]
        usage_rec.txrefnum_apr = i[66]
        usage_rec.ior_apr = i[67]
        usage_rec.amountpaid_str_apr = i[68]

        usage_rec.reading_may = i[69]
        usage_rec.reading_date_may = i[70]
        usage_rec.reading_postedby_may = i[71]
        usage_rec.usage_may = i[72]
        usage_rec.penalty_may = i[73]
        usage_rec.bill_may = i[74]
        usage_rec.totalbill_may = i[75]
        usage_rec.paidamt_may = i[76]
        usage_rec.datepaid_may = i[77]
        usage_rec.dateposted_may = i[78]
        usage_rec.postedby_may = i[79]
        usage_rec.txrefnum_may = i[80]
        usage_rec.ior_may = i[81]
        usage_rec.amountpaid_str_may = i[82]

        usage_rec.reading_jun = i[83]
        usage_rec.reading_date_jun = i[84]
        usage_rec.reading_postedby_jun = i[85]
        usage_rec.usage_jun = i[86]
        usage_rec.penalty_jun = i[87]
        usage_rec.bill_jun = i[88]
        usage_rec.totalbill_jun = i[89]
        usage_rec.paidamt_jun = i[90]
        usage_rec.datepaid_jun = i[91]
        usage_rec.dateposted_jun = i[92]
        usage_rec.postedby_jun = i[93]
        usage_rec.txrefnum_jun = i[94]
        usage_rec.ior_jun = i[95]
        usage_rec.amountpaid_str_jun = i[96]

        usage_rec.reading_jul = i[97]
        usage_rec.reading_date_jul = i[98]
        usage_rec.reading_postedby_jul = i[99]
        usage_rec.usage_jul = i[100]
        usage_rec.penalty_jul = i[101]
        usage_rec.bill_jul = i[102]
        usage_rec.totalbill_jul = i[103]
        usage_rec.paidamt_jul = i[104]
        usage_rec.datepaid_jul = i[105]
        usage_rec.dateposted_jul = i[106]
        usage_rec.postedby_jul = i[107]
        usage_rec.txrefnum_jul = i[108]
        usage_rec.ior_jul = i[109]
        usage_rec.amountpaid_str_jul = i[110]

        usage_rec.reading_aug = i[111]
        usage_rec.reading_date_aug = i[112]
        usage_rec.reading_postedby_aug = i[113]
        usage_rec.usage_aug = i[114]
        usage_rec.penalty_aug = i[115]
        usage_rec.bill_aug = i[116]
        usage_rec.totalbill_aug = i[117]
        usage_rec.paidamt_aug = i[118]
        usage_rec.datepaid_aug = i[119]
        usage_rec.dateposted_aug = i[120]
        usage_rec.postedby_aug = i[121]
        usage_rec.txrefnum_aug = i[122]
        usage_rec.ior_aug = i[123]
        usage_rec.amountpaid_str_aug = i[124]

        usage_rec.reading_sept = i[125]
        usage_rec.reading_date_sept = i[126]
        usage_rec.reading_postedby_sept = i[127]
        usage_rec.usage_sept = i[128]
        usage_rec.penalty_sept = i[129]
        usage_rec.bill_sept = i[130]
        usage_rec.totalbill_sept = i[131]
        usage_rec.paidamt_sept = i[132]
        usage_rec.datepaid_sept = i[133]
        usage_rec.dateposted_sept = i[134]
        usage_rec.postedby_sept = i[135]
        usage_rec.txrefnum_sept = i[136]
        usage_rec.ior_sept = i[137]
        usage_rec.amountpaid_str_sept = i[138]

        usage_rec.reading_oct = i[139]
        usage_rec.reading_date_oct = i[140]
        usage_rec.reading_postedby_oct = i[141]
        usage_rec.usage_oct = i[142]
        usage_rec.penalty_oct = i[143]
        usage_rec.bill_oct = i[144]
        usage_rec.totalbill_oct = i[145]
        usage_rec.paidamt_oct = i[146]
        usage_rec.datepaid_oct = i[147]
        usage_rec.dateposted_oct = i[148]
        usage_rec.postedby_oct = i[149]
        usage_rec.txrefnum_oct = i[150]
        usage_rec.ior_oct = i[151]
        usage_rec.amountpaid_str_oct = i[152]

        usage_rec.reading_nov = i[153]
        usage_rec.reading_date_nov = i[154]
        usage_rec.reading_postedby_nov = i[155]
        usage_rec.usage_nov = i[156]
        usage_rec.penalty_nov = i[157]
        usage_rec.bill_nov = i[158]
        usage_rec.totalbill_nov = i[159]
        usage_rec.paidamt_nov = i[160]
        usage_rec.datepaid_nov = i[161]
        usage_rec.dateposted_nov = i[162]
        usage_rec.postedby_nov = i[163]
        usage_rec.txrefnum_nov = i[164]
        usage_rec.ior_nov = i[165]
        usage_rec.amountpaid_str_nov = i[166]

        usage_rec.reading_dec = i[167]
        usage_rec.reading_date_dec = i[168]
        usage_rec.reading_postedby_dec = i[169]
        usage_rec.usage_dec = i[170]
        usage_rec.penalty_dec = i[171]
        usage_rec.bill_dec = i[172]
        usage_rec.totalbill_dec = i[173]
        usage_rec.paidamt_dec = i[174]
        usage_rec.datepaid_dec = i[175]
        usage_rec.dateposted_dec = i[176]
        usage_rec.postedby_dec = i[177]
        usage_rec.txrefnum_dec = i[178]
        usage_rec.ior_dec = i[179]
        usage_rec.amountpaid_str_dec = i[180]

def sys_user_out(i):
    sys_user.username = i[0]
    sys_user.password = i[1]
    sys_user.first_name = i[2]
    sys_user.mid_name = i[3]
    sys_user.mobilenum = i[4]
    sys_user.last_name = i[5]
    sys_user.email = i[6]
    sys_user.profilepic = i[8]
    sys_user.authorizedapprover = i[9]
    sys_user.save()
def rt_out(i):
    rt.rateid = i[0]
    rt.minReading = i[1]
    rt.minReadingCharge = i[2]
    rt.rateAfterMin = i[3]
    rt.ratePenalty = i[4]
    rt.ratePenaltyFreq = i[5]
    rt.save()
def b_rec_out(i):
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