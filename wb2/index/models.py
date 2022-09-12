from calendar import c
from datetime import date
from pyexpat import model
from tkinter import CASCADE
from django.db import models

from django.contrib.auth.models import AbstractUser
# Create your models here.


class SystemUsers(AbstractUser):
    USER_TYPE = (
        ('Admin','Admin'),
        ('Teller','Teller'),
        ('Supervisor','Supervisor'),
        ('Manager','Manager'),
        ('Meter Reader','Meter Reader'),
    )   
    midname = models.CharField(max_length=20, blank=True)
    lastname = models.CharField(max_length=20, blank=True)
    mobilenum = models.CharField(max_length=20, blank=True)
    usertype = models.CharField(max_length=20, choices=USER_TYPE)
    profilepic = models.ImageField(blank=True, null=True)

class Rates(models.Model):
    minReading = models.IntegerField()
    minReadingCharge = models.IntegerField()
    rateAfterMin = models.IntegerField()
    ratePenalty = models.IntegerField()
    ratePenaltyFreq = models.IntegerField()

class Barangays(models.Model):
    barangay = models.CharField(max_length=20, blank=True)

class BarangayRecord(models.Model):
    B_RecordID = models.IntegerField()
    barangaycode = models.ForeignKey(Barangays, on_delete=models.CASCADE, default='')
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

class Status(models.Model):
    status = models.CharField(max_length=20, blank=True)

class ConsumerInfo(models.Model):
    meternumber = models.IntegerField()
    firstname = models.CharField(max_length=20, blank=True)
    middlename = models.CharField(max_length=20, blank=True)
    lastname = models.CharField(max_length=20, blank=True)
    barangaycode = models.ForeignKey(Barangays, on_delete=models.CASCADE, default='')
    initialmeterreading = models.IntegerField()
    statuscode = models.ForeignKey(Status, on_delete=models.CASCADE, default='')
    penaltyflag = models.BooleanField()
    stopmeterflag = models.BooleanField()
    deleteflag = models.BooleanField()

class Penalties(models.Model):
    penalty = models.IntegerField()

class Discounts(models.Model):
    discount = models.IntegerField()


class Transactions(models.Model):
    TRANS_TYPE = (
        ('j','j'),
    )
    date = models.DateField()
    acctID = models.ForeignKey(ConsumerInfo, on_delete=models.CASCADE, default='')
    transType = models.CharField(max_length=20, choices=TRANS_TYPE)
    meterReading = models.IntegerField()
    ratescode = models.ForeignKey(Rates, on_delete= models.CASCADE, default='')
    penaltyCode = models.ForeignKey(Penalties, on_delete= models.CASCADE, default='')
    discountcode = models.ForeignKey(Discounts, on_delete= models.CASCADE, default='')
    payment = models.IntegerField()
    processedBy = models.ForeignKey(SystemUsers, on_delete=models.CASCADE, default='')