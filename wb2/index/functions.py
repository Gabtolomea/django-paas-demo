
import pandas as pd
import csv
from .models import *
from django.core.exceptions import ObjectDoesNotExist
import random
import string
import math
from datetime import datetime
from .dataporter import *
import mysql.connector
import os
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2 import service_account
from django.db.models import F
from django.db import transaction
from django.db.models import F, Q

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
def enye_cons():
    cons = ConsumerInfo.objects.all()
    for c in cons:
        chars = ["ã‘","ã±","Ã±"]
        for char in chars:
            if char in c.firstname:
                c.firstname = c.firstname.replace(char, "ñ")
            if char in c.lastname:
                c.lastname = c.lastname.replace(char, "ñ")
            if char in c.middlename:
                c.middlename = c.middlename.replace(char, "ñ")
            c.save()
def enye_bars():
    bars = Barangays.objects.all()
    for b in bars:
        chars = ["ã‘","ã±","Ã±","ÃƒÂ±","ÃƒÆ’Ã‚Â±"]
        for char in chars:
            if char in b.barangay:
                b.barangay = b.barangay.replace(char, "ñ")
            b.save()
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
        if asc_trans[i].transType == 'Additional Fees':
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
        con_b_rec.__dict__[f"total_paid_{months[month-1]}"] += amount
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
                    
    con_b_rec.__dict__[f"total_due_{months[d-1]}"] += bill
    con_b_rec.__dict__[f"total_usage_{months[d-1]}"] += usage
    
    con_b_rec.save()
    get_balance(consumer.consumer_id)
def set_first_tran():
    cons = ConsumerInfo.objects.all()
    for c in cons:
        trans = Transactions.objects.filter(acctID_id=c.consumer_id).order_by('year')
        try:
            c.first_tran = trans[0].year
        except IndexError:
            c.first_tran = 0
        c.save()
def get_consumers_yearly():
    cons = ConsumerInfo.objects.all()
    y2019 = len(cons.filter(first_tran__lt=2020))
    y2020 = len(cons.filter(first_tran__lt=2021))
    y2021 = len(cons.filter(first_tran__lt=2022))
    y2022 = len(cons.filter(first_tran__lt=2023))
    y2023 = len(cons.filter(first_tran__lt=2024))
    print(f"y2019 = {y2019}")
    print(f"y2020 = {y2020}")
    print(f"y2021 = {y2021}")
    print(f"y2022 = {y2022}")
    print(f"y2023 = {y2023}")


class MonthYearPair:
    def __init__(self, month, year):
        self.month = month
        self.year = year

def billing_errors_to_csv():
    csv_file_path = "C:/Users/watersystem/Desktop/output.csv"
    header = ["Year", "Month", "Consumer ID", "Consumer Name", "Meter Reading", "Next Previous", "Next Current"]
    program_output = [header]

    consumer_transactions = {}

    for consumer in ConsumerInfo.objects.all():
        transactions = Transactions.objects.filter(acctID_id=consumer.consumer_id, transType='Billing').order_by('year', 'month')
        consumer_transactions[consumer.consumer_id] = list(transactions)
    for consumer in consumer_transactions:
        c = ConsumerInfo.objects.get(consumer_id=consumer)
        transactions = consumer_transactions[consumer]

        for i in range(len(transactions) - 1):
            t = transactions[i]
            nt = transactions[i + 1]

            t_year = t.year
            t_month = t.month
            t_reading = t.meterReading
            nt_prev_reading = nt.prevReading
            nt_reading = nt.meterReading

            if t_reading > nt_prev_reading and t_reading <= nt_reading:
                consumer_name = f"{c.firstname} {c.lastname}"
                program_output.append([t_year, t_month, consumer, consumer_name, t_reading, nt_prev_reading, nt_reading])

    with open(csv_file_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(program_output)

def fix_billing_errors():
    consumers = ConsumerInfo.objects.all().select_related('installation_address')
    transactions = Transactions.objects.filter(acctID__in=consumers, transType='Billing').order_by('year', 'month')

    for consumer in consumers:
        consumer_bal_delta = 0
        consumer_brec_updates = []

        consumer_transactions = transactions.filter(acctID=consumer)
        month_years = [MonthYearPair(t.month, t.year) for t in consumer_transactions]

        for i in range(len(month_years) - 1):
            current_transaction = consumer_transactions[i]
            next_transaction = consumer_transactions[i + 1]
            rate = ConsumerType.objects.get(contypeid=current_transaction.contypeid)

            if current_transaction.meterReading > next_transaction.prevReading and current_transaction.meterReading <= next_transaction.meterReading:
                rate_next = ConsumerType.objects.get(contypeid=next_transaction.contypeid)

                next_transaction.prevReading = current_transaction.meterReading
                next_transaction.usage = next_transaction.meterReading - next_transaction.prevReading
                dif = next_transaction.bill
                if next_transaction.bill == 0:
                    next_transaction.is_billpaid = False
                if next_transaction.usage <= rate_next.minReading or next_transaction.usage < 0:
                    next_transaction.bill = rate_next.minReadingCharge
                else:
                    next_transaction.bill = ((next_transaction.usage - rate_next.minReading) * rate_next.rateAfterMin) + rate_next.minReadingCharge
                next_transaction.processedBy = "System Adjustment"
                dif = next_transaction.bill - dif
                next_transaction.save()

                consumer_bal_delta += dif

                if dif:
                    try:
                        payment_transaction = Transactions.objects.get(acctID=consumer, year=next_transaction.year, month=next_transaction.month, transType="Payment")
                        payment_transaction.payment += dif
                        consumer.current_bal -= dif
                        payment_transaction.save()
                    except Transactions.DoesNotExist:
                        pass

                brec_key = f"{consumer.installation_address_id}-{next_transaction.year}"
                brec_field_due = f"total_due_{months[next_transaction.month - 1]}"
                brec_field_usage = f"total_usage_{months[next_transaction.month - 1]}"
                consumer_brec_updates.append((brec_key, brec_field_due, brec_field_usage, next_transaction.bill, next_transaction.usage))

            if current_transaction.bill == 0 and current_transaction.transType == "Billing":
                current_transaction.bill = rate.minReadingCharge
                current_transaction.is_billpaid = False
                consumer_bal_delta += current_transaction.bill

                brec_key = f"{consumer.installation_address_id}-{current_transaction.year}"
                brec_field_due = f"total_due_{months[current_transaction.month - 1]}"
                brec_field_usage = f"total_usage_{months[current_transaction.month - 1]}"
                consumer_brec_updates.append((brec_key, brec_field_due, brec_field_usage, current_transaction.bill, current_transaction.usage))

        Transactions.objects.bulk_update(consumer_transactions, ['prevReading', 'usage', 'bill', 'is_billpaid', 'processedBy'])

        for brec_key, brec_field_due, brec_field_usage, bill_delta, usage_delta in consumer_brec_updates:
            BarangayRecord.objects.filter(barangayrec_id=brec_key).update(
                **{brec_field_due: F(brec_field_due) - bill_delta, brec_field_usage: F(brec_field_usage) - usage_delta}
            )

        consumer.current_bal += consumer_bal_delta
        consumer.save()



def dump_database():
    
    cnx = mysql.connector.connect(
        user='root',
        password='jazfer',
        host='localhost',
        port=3307,
        database='wb2',
        charset='latin1'
    )

    cursor = cnx.cursor()

    cursor.execute("SHOW TABLES")
    tables = cursor.fetchall()

    timestamp = datetime.now().strftime("%Y.%m.%d")
    desktop_path = os.path.expanduser("~/Desktop")

    folder_name = "Dump"

    folder_path = os.path.join(desktop_path, folder_name)

    if os.path.exists(folder_path):
        print("Folder already exists!")
    else:
        os.makedirs(folder_path)
        print("Folder created successfully!")
    dump_directory = desktop_path + f'/{folder_name}/'
    dump_file_path = f'{dump_directory}{timestamp}wb2_data_dump.sql'
    
    if os.path.exists(dump_file_path):
        print("Already dumped today, returning")
        return

    with open(dump_file_path, 'w', buffering=1000000) as dump_file:
        print("Dumping...")

        dump_file.write(f"DROP DATABASE IF EXISTS `wb2`;\n\n")
        dump_file.write(f"CREATE DATABASE IF NOT EXISTS `wb2`;\n\n")
        dump_file.write(f"USE `wb2`;\n\n")
        dump_file.write(f"SET FOREIGN_KEY_CHECKS=0;\n\n")

        for table in tables:
            table_name = table[0]
            dump_file.write(f"DROP TABLE IF EXISTS `{table_name}`;\n")
            cursor.execute(f"SHOW CREATE TABLE `{table_name}`")
            create_table_result = cursor.fetchone()
            create_table_statement = create_table_result[1]
            create_table_statement = create_table_statement.replace("CREATE TABLE", "CREATE TABLE IF NOT EXISTS")
            dump_file.write(create_table_statement + ';\n\n')
            query = f"SELECT * FROM `{table_name}`"
            cursor.execute(query)
            rows = cursor.fetchall()

            if len(rows) > 0:
                batch_size = 1000
                num_rows = len(rows)
                num_batches = (num_rows // batch_size) + (num_rows % batch_size > 0)

                for batch_index in range(num_batches):
                    start_index = batch_index * batch_size
                    end_index = min((batch_index + 1) * batch_size, num_rows)
                    dump_file.write(f"INSERT INTO `{table_name}` VALUES\n")
                    for i in range(start_index, end_index):
                        row = rows[i]
                        values = [f"'{str(value).encode('ascii', 'ignore').decode()}'" if value is not None else 'NULL' for value in row]
                        row_data = f"({', '.join(values)})"
                        if i < end_index - 1:
                            row_data += ','
                        dump_file.write(row_data + '\n')

                    dump_file.write(';\n\n')
            else:
                dump_file.write(f"DELETE FROM `{table_name}`;\n\n")
        dump_file.write(f"SET FOREIGN_KEY_CHECKS=1;\n\n")

        print("Success...")

    cursor.close()
    cnx.close()
    
    credentials_file = "D:/waterbilling2.0/service_key.json"

    if not os.path.exists(credentials_file):
        print(f"Please save the service account credentials JSON file at the specified path.")
        return

    credentials = service_account.Credentials.from_service_account_file(credentials_file, scopes=["https://www.googleapis.com/auth/drive.file"])
    drive_service = build("drive", "v3", credentials=credentials)

    target_folder_id = "1eYsQ3H3IsjKFBB-ka34sGUx2vzuSuHiY"

    response = drive_service.files().list(q=f"'{target_folder_id}' in parents and trashed=false", fields="files(name)").execute()
    existing_files = response.get("files", [])


    for filename in os.listdir(dump_directory):
        file_path = os.path.join(dump_directory, filename)

        file_exists = any(file_info["name"] == filename for file_info in existing_files)
        if file_exists:
            print(f"File '{filename}' already exists in the target folder. Skipping...")
            continue

        file_metadata = {"name": filename, "parents": [target_folder_id]}
        media = MediaFileUpload(file_path)
        drive_service.files().create(body=file_metadata, media_body=media).execute()

    print("Files uploaded successfully to the specified folder on Google Drive.")


def update_from_csv():
    consumer_brec_updates = []
    with open('D:/waterbilling2.0/wb2/output.csv', 'r') as file:
        reader = csv.reader(file)
        trans = [[row[0], row[1], row[4]] for row in reader]
    trans = trans[1:]
    for t in trans:
        transaction = Transactions.objects.get(transactionid=t[0])
        consumer = ConsumerInfo.objects.get(consumer_id=t[2])
        if transaction.is_billpaid == False:
            consumer.current_bal -= transaction.bill
            transaction.is_billpaid = bool(t[1])
            brec_key = f"{consumer.installation_address_id}-{transaction.year}"
            brec_field_due = f"total_due_{months[transaction.month - 1]}"
            brec_field_usage = f"total_usage_{months[transaction.month - 1]}"
            consumer_brec_updates.append((brec_key, brec_field_due, brec_field_usage, transaction.bill, transaction.usage))
            for brec_key, brec_field_due, brec_field_usage, bill_delta, usage_delta in consumer_brec_updates:
                BarangayRecord.objects.filter(barangayrec_id=brec_key).update(**{
                    brec_field_due: F(brec_field_due) - bill_delta,
                    brec_field_usage: F(brec_field_usage) - usage_delta
                })
            transaction.save()
            consumer.save()


def get_bal_exempt(id):
    user = ConsumerInfo.objects.get(consumer_id = id)
    trans = Transactions.objects.filter(acctID = id)
    asc_trans = trans.order_by('year', 'month','transactionid')
    bal = 0
    for i in range(len(asc_trans)):
        if asc_trans[i].transType == 'Billing':
            bal+=asc_trans[i].bill
    try:
        user.current_reading = trans.filter(transType='Billing').order_by('-year', '-month')[0].meterReading
    except IndexError:
        pass
    user.current_bal = math.ceil(bal*100)/100
    if user.current_bal < 0:
        user.current_bal = 0
    user.save()


def exempt_accounts(consumer):
    bills = Transactions.objects.filter(acctID=consumer, transType='Billing')
    for b in bills:
        con_b_rec = BarangayRecord.objects.get(barangayrec_id=f"{consumer.installation_address.id}-{b.year}")
        con_b_rec.__dict__[f"total_due_{months[b.month - 1]}"] -= b.bill
        con_b_rec.save()
        b.bill = 0
    Transactions.objects.bulk_update(bills, ['bill'])

    
def adjust_excess_only():
    search = 'excess only'
    excess_only_accts = ConsumerInfo.objects.filter(Q(firstname__icontains=search) | Q(lastname__icontains=search))
    for acct in excess_only_accts:
        adjust_from_contype(acct.meternumber, 'C003')



def adjust_from_contype(meternumber, contype):
    consumer = ConsumerInfo.objects.get(meternumber=meternumber)
    consumer.contypeid = ConsumerType.objects.get(contypeid=contype)
    transactions = Transactions.objects.filter(acctID_id=consumer.consumer_id, is_billpaid=False, transType='Billing').exclude(contypeid=contype).order_by('year', 'month')

    for t in transactions:
        brec = BarangayRecord.objects.get(barangayrec_id=f"{consumer.installation_address.id}-{t.year}") 
        old_bill = t.bill
        t.contypeid = consumer.contypeid.contypeid
        if t.usage <= consumer.contypeid.minReading:
            t.bill = consumer.contypeid.minReadingCharge
        else:
            t.bill = ((t.usage - consumer.contypeid.minReading)*consumer.contypeid.rateAfterMin) + consumer.contypeid.minReadingCharge
        diff = t.bill - old_bill
        brec.__dict__[f"total_due_{months[t.month - 1]}"] -= diff
        brec.save()
        t.save()
    consumer.save()
    get_balance(consumer.consumer_id)

def set_overdue_months():
    consumers = ConsumerInfo.objects.filter(current_bal__gt=0, excep_accnt = False)
    for c in consumers:
        unpaid_trans = Transactions.objects.filter(acctID=c.consumer_id, is_billpaid=False, transType='Billing').order_by('year', 'month')
        for t in unpaid_trans:
            if t.months_not_paid >= 6:
                try:
                    issue = Issues.objects.get(consumer_id=c.consumer_id, transaction_id=t.transactionid)
                except ObjectDoesNotExist:
                    issue = Issues()
                    issue.consumer_id = c
                    issue.transaction_id = t
                    issue.issued_by = "System"
                issue.issue = f"Overdue for {t.months_not_paid} months"
                issue.save()
            else:
                t.months_not_paid += 1
                t.save()

def get_month_diff(month1, year1, month2, year2):
    return (year1 - year2) * 12 + (month1 - month2)


def set_months_unpaid():
    consumers = ConsumerInfo.objects.filter(current_bal__gt=0, excep_accnt = False)
    for c in consumers:
        unpaid_trans = Transactions.objects.filter(acctID=c.consumer_id, is_billpaid=False, transType='Billing').order_by('year', 'month')
        for t in unpaid_trans:
            t.months_not_paid = get_month_diff(date.today().month, date.today().year, t.month, t.year)
            t.save()
            if t.months_not_paid >= 6:
                try:
                    issue = Issues.objects.get(consumer_id=c.consumer_id, transaction_id=t.transactionid)
                except ObjectDoesNotExist:
                    issue = Issues()
                    issue.consumer_id = c
                    issue.transaction_id = t
                    issue.issued_by = "System"
                issue.issue = f"Overdue for {t.months_not_paid} months"
                issue.save()
