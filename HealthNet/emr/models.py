from django.db import models
from django.utils import timezone
import datetime
from user.models import Doctor, Patient


class EMRItem(models.Model):
    """This is generic item which can be stored in the EMR, other models will extend this"""
    patient = models.OneToOneField(Patient)
    date_created = models.DateTimeField(default=timezone.now)
    content = models.CharField(max_length=200)

    def getType(self):
        return 'generic_item'


class EMRTracking(EMRItem):
    """This model is a generic tracked metric, meaning a provider can track some arbitrary detail about a patient
    across different appointments"""
    name = models.CharField(max_length=200, default="", unique=True)  # unique label for metric
    rev = models.IntegerField(default=0)

    class Meta:
        abstract=True


class EMRVitals(EMRTracking, EMRItem):
    """This model will store a set of vital sign readings as well as height, weight ...etc"""
    restingBPM = models.IntegerField(default=0)  # Resting pulse in beats/min
    bloodPressure = models.CharField(max_length=10, default="")  # Blood pressure in format ###/###
    height = models.FloatField(default=0)  # Height of the patient in inches
    weight = models.FloatField(default=0)  # Weight of a person in Lbs


class EMRProfile(EMRItem):
    birthdate = models.DateTimeField(default=timezone.now)
    gender = models.CharField(max_length=10)
    blood_type = models.CharField(max_length=3)


class EMRTest(EMRItem):
    images = models.ImageField(null=True, blank=True)
    released = models.BooleanField(default=False)



"""
This Prescription class holds all the information relating to a single prescription

Extending EMRItem for created DateTime and linked to a emr
"""
class EMRPrescription(EMRItem):
    # Created DateTimeField is found in EMRItem
    doctor = models.ForeignKey('user.Doctor', null=False, blank=True)
    # TODO: DRUG DATABASE
    dosage = models.CharField(max_length=50, default="", null=False)
    amountPerDay = models.CharField(max_length=50, default="", null=False)
    startDate = models.DateField(default=datetime.date.today)
    endDate = models.DateField(default=(timezone.now() + datetime.timedelta(days=30)))
    deactivated = models.BooleanField(default=False)