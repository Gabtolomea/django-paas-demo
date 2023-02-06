from datetime import date, datetime
from django.db import models
from django.contrib.auth.models import AbstractUser
from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
import sys
# Create your models here.

class LoginRec(models.Model):
    username = models.CharField(max_length=20,primary_key = True)
    token = models.CharField(max_length = 10)
    last_access = models.DateTimeField()
    expiration = models.DateTimeField(default = datetime.now())


    

class SystemUsers(AbstractUser):
    first_name = models.CharField(max_length=20, blank=True)
    last_name = models.CharField(max_length=20, blank=True)
    username = models.CharField(max_length=20,primary_key = True)
    is_admin = models.BooleanField(default=False)
    is_teller = models.BooleanField(default=False)
    is_supervisor = models.BooleanField(default=False)
    is_manager = models.BooleanField(default=False)
    is_reader = models.BooleanField(default=False)
    mid_name = models.CharField(max_length=20, blank=True)
    mobilenum = models.CharField(max_length=20, blank=True)
    authorizedapprover = models.CharField(max_length=20)
    email = models.EmailField(max_length=100,null=True, blank=True)
    profilepic = models.ImageField(upload_to= '', blank=True, null=True, default='profile12.png')
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        SIZE = 300, 300
        if self.profilepic:
            pic = Image.open(self.profilepic.path)
            pic.thumbnail(SIZE, Image.LANCZOS)
            pic.save(self.profilepic.path)

    
    def __str__(self) -> str:
        return self.username
    

class ConsumerType(models.Model):
    contypeid = models.CharField(primary_key=True, max_length=20)
    contype = models.CharField(max_length=20)
    minReading = models.IntegerField()
    minReadingCharge = models.IntegerField()
    rateAfterMin = models.IntegerField()
    date_added = models.DateField(auto_now_add=True)
    date_mod = models.DateField(auto_now=True)
    added_by = models.ForeignKey(SystemUsers, on_delete=models.SET_NULL, null=True)

    def __str__(self) -> str:
        return self.contype

class Penalty(models.Model):
    penaltycode = models.CharField(primary_key=True, max_length=20)
    penalty_after =  models.IntegerField(default = 0)#months
    penalty_rate = models.FloatField(default = 0)
    penalty_info = models.TextField(max_length=300, blank=True, null=True)
    date_added = models.DateField(auto_now_add=True, null=True)
    daysappliedafter = models.IntegerField(default=0)
    added_by = models.ForeignKey(SystemUsers, on_delete=models.SET_NULL, null=True)
    def __str__(self) -> str:
        return self.penaltycode


class Discount(models.Model):
    discountcode = models.CharField(primary_key=True, max_length=20)
    discount_rate = models.IntegerField()
    date_added = models.DateField(auto_now_add=True)
    added_by = models.ForeignKey(SystemUsers, on_delete=models.SET_NULL, null=True)

class Barangays(models.Model):
    barangay = models.CharField(max_length=20, blank=True)
    def __str__(self) -> str:
        return self.barangay
class BarangayRecord(models.Model):
    barangayrec_id = models.CharField(primary_key = True ,max_length=20)
    barangaycode = models.ForeignKey(Barangays,on_delete=models.SET_NULL, null=True)
    year = models.IntegerField()
    total_due_jan = models.IntegerField()
    total_paid_jan = models.IntegerField()
    total_usage_jan = models.IntegerField()
    total_due_feb = models.IntegerField()
    total_paid_feb = models.IntegerField()
    total_usage_feb = models.IntegerField()
    total_due_mar = models.IntegerField()
    total_paid_mar = models.IntegerField()
    total_usage_mar = models.IntegerField()
    total_due_apr = models.IntegerField()
    total_paid_apr = models.IntegerField()
    total_usage_apr = models.IntegerField()
    total_due_may = models.IntegerField()
    total_paid_may = models.IntegerField()
    total_usage_may = models.IntegerField()
    total_due_jun = models.IntegerField()
    total_paid_jun = models.IntegerField()
    total_usage_jun = models.IntegerField()
    total_due_jul = models.IntegerField()
    total_paid_jul = models.IntegerField()
    total_usage_jul = models.IntegerField()
    total_due_aug = models.IntegerField()
    total_paid_aug = models.IntegerField()
    total_usage_aug = models.IntegerField()
    total_due_sept = models.IntegerField()
    total_paid_sept = models.IntegerField()
    total_usage_sept = models.IntegerField()
    total_due_oct = models.IntegerField()
    total_paid_oct = models.IntegerField()
    total_usage_oct = models.IntegerField()
    total_due_nov = models.IntegerField()
    total_paid_nov = models.IntegerField()
    total_usage_nov = models.IntegerField()
    total_due_dec = models.IntegerField()
    total_paid_dec = models.IntegerField()
    total_usage_dec = models.IntegerField()


#Consumer Creation
class ConsumerInfo(models.Model):
    consumer_id = models.CharField(primary_key=True, max_length=15)
    meternumber = models.CharField(max_length=20, blank=True, null=True)
    firstname = models.CharField(max_length=50, blank=True)
    lastname = models.CharField(max_length=50, blank=True)
    middlename = models.CharField(max_length=50, blank=True)
    homeaddress = models.CharField(max_length=50, blank=True)
    installation_address = models.ForeignKey(Barangays, on_delete=models.CASCADE)
    initialmeterreading = models.IntegerField()
    contypeid = models.ForeignKey(ConsumerType,on_delete=models.CASCADE)#consumertype
    status = models.IntegerField()
    penaltycounter = models.IntegerField(null=True)
    stopmeterflag = models.BooleanField()
    deleteflag = models.BooleanField()
    disconnectionflag = models.BooleanField()
    mobilenum = models.CharField(max_length=20, blank=True)
    email = models.EmailField(max_length=100,null=True, blank=True)
    birthdate = models.DateField(null=True, blank=True)
    sex = models.CharField(max_length=6,null=True, blank=True)
    sitio = models.CharField(max_length=100,null=True, blank=True)
    picture = models.ImageField(null=True, blank=True)
    current_bal = models.FloatField(default=0)
    cummulative = models.FloatField(default=0)
    date_added = models.DateField(auto_now_add=True, null=True)
    penaltycode = models.ForeignKey(Penalty, on_delete= models.SET_NULL, null=True, default='POO1')
class Transactions(models.Model):
    TRANS_TYPE = (
        ('Billing','Billing'),
        ('Payment','Payment'),
        ('Penalty','Penalty'),
        ('Discount','Discount'),
    )
    transactionid = models.AutoField(primary_key=True)
    date = models.DateField(null=True, blank=True)
    acctID = models.ForeignKey(ConsumerInfo, on_delete=models.CASCADE)
    transType = models.CharField(max_length=20, choices=TRANS_TYPE)
    meterReading = models.IntegerField(blank=True, null=True)
    usage = models.IntegerField(blank=True, null=True)
    contypeid = models.CharField(max_length=20, blank=True, null=True)#consumertype
    penaltyCode = models.ForeignKey(Penalty, on_delete= models.SET_NULL, null=True)
    discountcode = models.CharField(max_length=50, null=True)
    bill = models.FloatField(null=True)
    month = models.IntegerField(blank=True, null=True)
    year = models.IntegerField(blank=True, null=True)
    payment = models.FloatField(null=True)
    processedBy = models.CharField(max_length=50, null=True)
    or_number = models.CharField(max_length=100)
    
    def __str__(self) -> str:
        return str(self.transactionid)

class usage_record(models.Model):
    #generate date
    current_date =  date.today()

    accountid = models.CharField(max_length=45,primary_key=True)
    rateid = models.CharField(max_length=45,default= " ")
    prevyeardue = models.FloatField(default = 0)
    excesspayment = models.FloatField(default = 0)
    commulative_bill = models.FloatField(default = 0)
    year = models.BigIntegerField(default=current_date.year)
    consumerid = models.ForeignKey(ConsumerInfo,on_delete = models.CASCADE,default="")
    accountinfoid = models.CharField(max_length = 50,default = "")
    amountpaid_history = models.TextField(default = "")
    datepaid_history = models.TextField(default = "")
    postedby_history = models.TextField(default = "")
    or_number_history = models.TextField(default = "")
    previous_reading = models.FloatField(default = 0)



    #january
    reading_jan = models.FloatField(default = 0)
    reading_date_jan = models.CharField(max_length=45,default = " ")
    reading_postedby_jan = models.CharField(max_length=45,default = " ")
    usage_jan = models.FloatField(default = 0)
    penalty_jan = models.FloatField(default = 0)
    bill_jan = models.FloatField(default = 0)
    totalbill_jan = models.FloatField(default = 0)
    paidamt_jan = models.FloatField(default = 0)
    datepaid_jan = models.TextField(default = " ")
    dateposted_jan = models.CharField(max_length=45,default = " ")
    postedby_jan = models.TextField(default = " ")
    txrefnum_jan = models.CharField(max_length=45,default = " ")
    ior_jan = models.CharField(max_length=50,default=" ")
    amountpaid_str_jan = models.TextField(default="")
    #february
    reading_feb = models.FloatField(default = 0)
    reading_date_feb = models.CharField(max_length=45)
    reading_postedby_feb = models.CharField(max_length=45)
    usage_feb = models.FloatField(default = 0)
    penalty_feb = models.FloatField(default = 0)
    bill_feb = models.FloatField(default = 0)
    totalbill_feb = models.FloatField(default = 0)
    paidamt_feb = models.FloatField(default = 0)
    datepaid_feb = models.TextField(default = " ")
    dateposted_feb = models.CharField(max_length=45,default = " ")
    postedby_feb = models.TextField(default=" ")
    txrefnum_feb = models.CharField(max_length=45,default = " ")
    ior_feb = models.CharField(max_length=50,default=" ")
    amountpaid_str_feb = models.TextField(default="")
    #march
    reading_mar = models.FloatField(default = 0)
    reading_date_mar = models.CharField(max_length=45)
    reading_postedby_mar = models.CharField(max_length=45)
    usage_mar = models.FloatField(default = 0)
    penalty_mar = models.FloatField(default = 0)
    bill_mar = models.FloatField(default = 0)
    totalbill_mar = models.FloatField(default = 0)
    paidamt_mar = models.FloatField(default = 0)
    datepaid_mar = models.TextField(default = " ")
    dateposted_mar = models.TextField(default = " ")
    postedby_mar = models.TextField(default=" ")
    txrefnum_mar = models.CharField(max_length=45,default = " ")
    ior_mar = models.CharField(max_length=50,default=" ")
    amountpaid_str_mar = models.TextField(default ="")
    #april
    reading_apr = models.FloatField(default = 0)
    reading_date_apr = models.CharField(max_length=45)
    reading_postedby_apr = models.CharField(max_length=45)
    usage_apr = models.FloatField(default = 0)
    penalty_apr = models.FloatField(default = 0)
    bill_apr = models.FloatField(default = 0)
    totalbill_apr = models.FloatField(default = 0)
    paidamt_apr = models.FloatField(default = 0)
    datepaid_apr = models.TextField(default = " ")
    dateposted_apr = models.CharField(max_length=45,default = " ")
    postedby_apr = models.TextField(default=" ")
    txrefnum_apr = models.CharField(max_length=45,default = " ")
    ior_apr = models.CharField(max_length=50,default=" ")
    amountpaid_str_apr = models.TextField(default="")
    #may
    reading_may = models.FloatField(default = 0)
    reading_date_may = models.CharField(max_length=45)
    reading_postedby_may = models.CharField(max_length=45)
    usage_may = models.FloatField(default = 0)
    penalty_may = models.FloatField(default = 0)
    bill_may = models.FloatField(default = 0)
    totalbill_may = models.FloatField(default = 0)
    paidamt_may = models.FloatField(default = 0)
    datepaid_may = models.TextField(default = " ")
    dateposted_may = models.CharField(max_length=45,default = " ")
    postedby_may = models.TextField(default=" ")
    txrefnum_may = models.CharField(max_length=45,default = " ")
    ior_may = models.CharField(max_length=50,default=" ")
    amountpaid_str_may = models.TextField(default="")
    #june
    reading_jun = models.FloatField(default = 0)
    reading_date_jun = models.CharField(max_length=45)
    reading_postedby_jun = models.CharField(max_length=45)
    usage_jun = models.FloatField(default = 0)
    penalty_jun = models.FloatField(default = 0)
    bill_jun = models.FloatField(default = 0)
    totalbill_jun = models.FloatField(default = 0)
    paidamt_jun = models.FloatField(default = 0)
    datepaid_jun = models.TextField(default = " ")
    dateposted_jun = models.CharField(max_length=45,default = " ")
    postedby_jun = models.TextField(default=" ")
    txrefnum_jun = models.CharField(max_length=45,default = " ")
    ior_jun = models.CharField(max_length=50,default=" ")
    amountpaid_str_jun = models.TextField(default="")
    #july
    reading_jul = models.FloatField(default = 0)
    reading_date_jul = models.CharField(max_length=45)
    reading_postedby_jul = models.CharField(max_length=45)
    usage_jul = models.FloatField(default = 0)
    penalty_jul = models.FloatField(default = 0)
    bill_jul = models.FloatField(default = 0)
    totalbill_jul = models.FloatField(default = 0)
    paidamt_jul = models.FloatField(default = 0)
    datepaid_jul = models.TextField(default = " ")
    dateposted_jul = models.CharField(max_length=45,default = " ")
    postedby_jul = models.TextField(default=" ")
    txrefnum_jul = models.CharField(max_length=45,default = " ")
    ior_jul = models.CharField(max_length=50,default=" ")
    amountpaid_str_jul = models.TextField(default="")
    #august
    reading_aug = models.FloatField(default = 0)
    reading_date_aug = models.CharField(max_length=45)
    reading_postedby_aug = models.CharField(max_length=45)
    usage_aug = models.FloatField(default = 0)
    penalty_aug = models.FloatField(default = 0)
    bill_aug = models.FloatField(default = 0)
    totalbill_aug = models.FloatField(default = 0)
    paidamt_aug = models.FloatField(default = 0)
    datepaid_aug = models.TextField(default = " ")
    dateposted_aug = models.CharField(max_length=45,default = " ")
    postedby_aug = models.TextField(default=" ")
    txrefnum_aug = models.CharField(max_length=45,default = " ")
    ior_aug = models.CharField(max_length=50,default=" ")
    amountpaid_str_aug = models.TextField(default="")
    #september
    reading_sept = models.FloatField(default = 0)
    reading_date_sept = models.CharField(max_length=45)
    reading_postedby_sept = models.CharField(max_length=45)
    usage_sept = models.FloatField(default = 0)
    penalty_sept = models.FloatField(default = 0)
    bill_sept = models.FloatField(default = 0)
    totalbill_sept = models.FloatField(default = 0)
    paidamt_sept = models.FloatField(default = 0)
    datepaid_sept = models.TextField(default = " ")
    dateposted_sept = models.CharField(max_length=45,default = " ")
    postedby_sept = models.TextField(default=" ")
    txrefnum_sept = models.CharField(max_length=45,default = " ")
    ior_sept = models.CharField(max_length=50,default=" ")
    amountpaid_str_sept = models.TextField(default="")
    #october
    reading_oct = models.FloatField(default = 0)
    reading_date_oct = models.CharField(max_length=45)
    reading_postedby_oct = models.CharField(max_length=45)
    usage_oct = models.FloatField(default = 0)
    penalty_oct = models.FloatField(default = 0)
    bill_oct = models.FloatField(default = 0)
    totalbill_oct = models.FloatField(default = 0)
    paidamt_oct = models.FloatField(default = 0)
    datepaid_oct = models.TextField(default = " ")
    dateposted_oct = models.CharField(max_length=45,default = " ")
    postedby_oct = models.TextField(default=" ")
    txrefnum_oct = models.TextField(default = " ")
    ior_oct = models.CharField(max_length=50,default=" ")
    amountpaid_str_oct = models.TextField(default="")
    #november
    reading_nov = models.FloatField(default = 0)
    reading_date_nov = models.CharField(max_length=45)
    reading_postedby_nov = models.CharField(max_length=45)
    usage_nov = models.FloatField(default = 0)
    penalty_nov = models.FloatField(default = 0)
    bill_nov = models.FloatField(default = 0)
    totalbill_nov = models.FloatField(default = 0)
    paidamt_nov = models.FloatField(default = 0)
    datepaid_nov = models.TextField(default = " ")
    dateposted_nov = models.CharField(max_length=45,default = " ")
    postedby_nov = models.TextField(default=" ")
    txrefnum_nov = models.CharField(max_length=45,default = " ")
    ior_nov = models.CharField(max_length=50,default=" ")
    amountpaid_str_nov = models.TextField(default="")
    #december
    reading_dec = models.FloatField(default = 0)
    reading_date_dec = models.CharField(max_length=45)
    reading_postedby_dec = models.CharField(max_length=45)
    usage_dec = models.FloatField(default = 0)
    penalty_dec = models.FloatField(default = 0)
    bill_dec = models.FloatField(default = 0)
    totalbill_dec = models.FloatField(default = 0)
    paidamt_dec = models.FloatField(default = 0)
    datepaid_dec = models.TextField(default = " ")
    dateposted_dec = models.CharField(max_length=45,default = " ")
    postedby_dec = models.TextField(default=" ")
    txrefnum_dec = models.CharField(max_length=45,default = " ")
    ior_dec = models.CharField(max_length=50,default=" ")
    amountpaid_str_dec = models.TextField(default="")

class revenuecode(models.Model):
    application_fee = models.FloatField(default = 0)
    mayors_permit = models.FloatField(default = 0)
    gravel_excavation = models.FloatField(default = 0)
    asphalted_road = models.FloatField(default = 0)
    cemented_road = models.FloatField(default = 0)
    additionalfee_pipe_of_20_lineal_feet = models.FloatField(default = 0)
    residentialservice_per_month = models.FloatField(default = 0)
    commercialservice_per_month = models.FloatField(default = 0)
    residentialservice_excess_per_cubicmeter = models.FloatField(default = 0)
    commercialservice_excess_per_cubicmeter = models.FloatField(default = 0)
    drilling_from_mainline = models.FloatField(default = 0)
    reinstallation_fee = models.FloatField(default = 0)
    tapping_fee = models.FloatField(default = 0)
    repair_fee = models.FloatField(default = 0)
    transfer_fee = models.FloatField(default = 0)
    three_month_penalty = models.FloatField(default = 0)
    send_disconnection_notice_after = models.IntegerField(default = 0)#months
    disconnection_after = models.IntegerField(default = 0)#months
    penalty_after = models.IntegerField(default = 0)#months
    fix_amount_penalty = models.FloatField(default = 0)
    percentage_penalty = models.FloatField(default = 0)

