from django.db import models

from django.contrib.auth.models import AbstractUser
# Create your models here.


class SystemUsers(AbstractUser):
    USER_TYPE = (
        ('',''),
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

