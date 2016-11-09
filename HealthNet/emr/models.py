from django.utils import timezone
import datetime
from user.models import Doctor, Patient
from django.contrib.auth.models import User
from hospital.models import *


class EMRItem(models.Model):
    """This is generic item which can be stored in the EMR, other models will extend this"""
    title = models.CharField(default="", max_length=50)
    patient = models.ForeignKey(Patient, blank=True, null=True)
    date_created = models.DateTimeField(auto_now_add=True, blank=True)
    content = models.CharField(max_length=200)
    priority = models.IntegerField(default=0)


    def getType(self):
        for subtype in ['emrvitals', 'emrprofile', 'emrtest', 'emrprescription']:
            if hasattr(self, subtype):
                return getattr(self, subtype).getType()
        return 'generic_item'


class EMRVitals(EMRItem):
    """This model will store a set of vital sign readings as well as height, weight ...etc"""
    restingBPM = models.IntegerField(default=0)  # Resting pulse in beats/min
    bloodPressure = models.CharField(max_length=10, default="")  # Blood pressure in format ###/###
    height = models.FloatField(default=0)  # Height of the patient in inches
    weight = models.FloatField(default=0)  # Weight of a person in Lbs

    def getType(self):
        return 'vitals'


class EMRAdmitStatus(EMRItem):
    hospital = models.ForeignKey(Hospital, null=True, blank=True)
    admit = models.BooleanField(default=True)



class EMRProfile(models.Model):
    patient = models.OneToOneField(Patient, blank=True, null=True)
    birthdate = models.DateTimeField(default=timezone.now)
    gender = models.CharField(max_length=10, default="")
    blood_type = models.CharField(max_length=3, default="")
    family_history = models.CharField(max_length=200, default="")
    comments = models.CharField(max_length=200, default="")

    admit_status = models.OneToOneField(EMRAdmitStatus, blank=True, null=True)


    def getInumber(self):
        return self.patient.insuranceNum

    def getAge(self):
        years = timezone.now().year - self.birthdate.year
        months = timezone.now().month - self.birthdate.month
        days = timezone.now().day - self.birthdate.day

        inc = (months>=0) and (days>=0)
        if inc:
            years += 1

        return years

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