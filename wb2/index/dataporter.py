
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
# mydb = mysql.connector.connect(
#     host="localhost",
#     user="root",
#     password="yjh434ctuG@-@",
#     database="lgu_ginatilan_db"
# )
# mycursor = mydb.cursor()

def porter():
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

b_rec = BarangayRecord()
sys_user = SystemUsers()
rt = Rates()
def porter_out(tables):
    for i in tables[2]:
        b_rec_out(i)
    for i in tables[7]:
        rt_out(i)
    for i in tables[9]:
        sys_user_out(i)



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
