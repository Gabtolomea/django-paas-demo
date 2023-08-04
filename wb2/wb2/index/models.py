from datetime import datetime
from django.db import models
from django.contrib.auth.models import AbstractUser
from PIL import Image
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
    total_due_jan = models.IntegerField(default=0)
    total_paid_jan = models.IntegerField(default=0)
    total_usage_jan = models.IntegerField(default=0)
    total_due_feb = models.IntegerField(default=0)
    total_paid_feb = models.IntegerField(default=0)
    total_usage_feb = models.IntegerField(default=0)
    total_due_mar = models.IntegerField(default=0)
    total_paid_mar = models.IntegerField(default=0)
    total_usage_mar = models.IntegerField(default=0)
    total_due_apr = models.IntegerField(default=0)
    total_paid_apr = models.IntegerField(default=0)
    total_usage_apr = models.IntegerField(default=0)
    total_due_may = models.IntegerField(default=0)
    total_paid_may = models.IntegerField(default=0)
    total_usage_may = models.IntegerField(default=0)
    total_due_jun = models.IntegerField(default=0)
    total_paid_jun = models.IntegerField(default=0)
    total_usage_jun = models.IntegerField(default=0)
    total_due_jul = models.IntegerField(default=0)
    total_paid_jul = models.IntegerField(default=0)
    total_usage_jul = models.IntegerField(default=0)
    total_due_aug = models.IntegerField(default=0)
    total_paid_aug = models.IntegerField(default=0)
    total_usage_aug = models.IntegerField(default=0)
    total_due_sept = models.IntegerField(default=0)
    total_paid_sept = models.IntegerField(default=0)
    total_usage_sept = models.IntegerField(default=0)
    total_due_oct = models.IntegerField(default=0)
    total_paid_oct = models.IntegerField(default=0)
    total_usage_oct = models.IntegerField(default=0)
    total_due_nov = models.IntegerField(default=0)
    total_paid_nov = models.IntegerField(default=0)
    total_usage_nov = models.IntegerField(default=0)
    total_due_dec = models.IntegerField(default=0)
    total_paid_dec = models.IntegerField(default=0)
    total_usage_dec = models.IntegerField(default=0)


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
    current_reading = models.IntegerField(default=0)
    cummulative = models.FloatField(default=0)
    date_added = models.DateField(auto_now_add=True, null=True)
    excess = models.IntegerField(default=0)
    penaltycode = models.ForeignKey(Penalty, on_delete= models.SET_NULL, null=True, default='POO1')
    first_tran = models.IntegerField(null=True)
    excep_accnt = models.BooleanField(default=False)
    has_additionalfees = models.BooleanField(default=False)

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
    prevReading = models.IntegerField(blank=True, null=True)
    usage = models.IntegerField(blank=True, null=True)
    contypeid = models.CharField(max_length=20, blank=True, null=True)#consumertype
    penaltyCode = models.ForeignKey(Penalty, on_delete= models.SET_NULL, null=True)
    discountcode = models.CharField(max_length=50, null=True)
    bill = models.FloatField(null=True)
    is_billpaid = models.BooleanField(default = False)
    month = models.IntegerField(blank=True, null=True)
    year = models.IntegerField(blank=True, null=True)
    receivedamt = models.FloatField(null=True)
    payment = models.FloatField(null=True)
    processedBy = models.CharField(max_length=50, null=True)
    or_number = models.CharField(max_length=100)
    is_issue = models.BooleanField(default=False)
    months_not_paid = models.IntegerField(default=0)
    def __str__(self) -> str:
        return str(self.transactionid)

class Issues(models.Model):
    issueid = models.AutoField(primary_key=True)
    transactionid = models.ForeignKey(Transactions, on_delete=models.CASCADE)
    issue = models.CharField(max_length=100)
    date = models.DateField(auto_now_add=True)
    last_comment = models.CharField(max_length=100, null=True)
    issued_by = models.CharField(max_length=100, null=True)
    is_seen = models.BooleanField(default=False)
    status = models.CharField(max_length=20, default='Pending')

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

class Messages(models.Model):
    message_id = models.AutoField(primary_key=True)
    issue_id = models.ForeignKey(Issues, on_delete=models.CASCADE)
    from_user = models.ForeignKey(SystemUsers, on_delete=models.CASCADE, related_name='from_user')
    to_user = models.ForeignKey(SystemUsers, on_delete=models.CASCADE, related_name='to_user')
    message = models.CharField(max_length=100)
    date = models.DateField(auto_now_add=True)
    time = models.TimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

class AdditionalFees(models.Model):
    feeid = models.AutoField(primary_key=True)
    consumer_id = models.ForeignKey(ConsumerInfo, on_delete=models.CASCADE)
    fee_name = models.CharField(max_length=100)
    amount = models.FloatField()
    months = models.IntegerField()
    month_counter = models.IntegerField(default=1)
    remainder = models.IntegerField()
    current_tran = models.IntegerField(null=True)
    date_added = models.DateField(auto_now_add=True)