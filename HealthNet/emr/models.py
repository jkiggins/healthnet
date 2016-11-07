from django.db import models
from django.utils import timezone
import datetime
from user.models import Doctor, Patient
from django.contrib.auth.models import User


class EMRItem(models.Model):
    """This is generic item which can be stored in the EMR, other models will extend this"""
    title = models.CharField(default="", max_length=50)
    patient = models.ForeignKey(Patient, blank=True, null=True)
    date_created = models.DateTimeField(auto_now_add=True, blank=True)
    content = models.CharField(max_length=200)
    priority = models.IntegerField(default=0)


    def getType(self):
        return 'generic_item'


class EMRVitals(EMRItem):
    """This model will store a set of vital sign readings as well as height, weight ...etc"""
    restingBPM = models.IntegerField(default=0)  # Resting pulse in beats/min
    bloodPressure = models.CharField(max_length=10, default="")  # Blood pressure in format ###/###
    height = models.FloatField(default=0)  # Height of the patient in inches
    weight = models.FloatField(default=0)  # Weight of a person in Lbs

    def getType(self):
        return 'vitals'


class EMRProfile(EMRItem):
    birthdate = models.DateTimeField(default=timezone.now)
    gender = models.CharField(max_length=10, default="")
    blood_type = models.CharField(max_length=3, default="")

    def getType(self):
        return 'profile'


class EMRTest(EMRItem):
    images = models.ImageField(null=True, blank=True)
    released = models.BooleanField(default=False)

    def getType(self):
        return 'test'


"""
This Prescription class holds all the information relating to a single prescription

Extending EMRItem for created DateTime and linked to a emr
"""
class EMRPrescription(EMRItem):
    # Created DateTimeField is found in EMRItem
    proivder = models.ForeignKey(User, null=True, blank=True)
    # TODO: DRUG DATABASE
    dosage = models.CharField(max_length=50, default="", null=False)
    amountPerDay = models.CharField(max_length=50, default="", null=False)
    startDate = models.DateField(default=datetime.date.today)
    endDate = models.DateField(default=(timezone.now() + datetime.timedelta(days=30)))
    deactivated = models.BooleanField(default=False)

    def getType(self):
        return 'prescription'