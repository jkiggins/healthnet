from django.db import models
from django.utils import timezone
from hospital.models import Hospital
from emr.models import EMR


# Create your models here.
class User(models.Model):

    Calendar = models.OneToOneField('Calendar', null=True, blank=True)
    UserName = models.CharField(max_length=15, default="", unique=True)
    Password = models.CharField(max_length=20, default="")

    firstName = models.CharField(max_length=20, default="")
    lastName = models.CharField(max_length=20, default="")
    # name = models.CharField(max_length=30)

    def __str__(self):
        return self.firstName + ", " + self.lastName

    class Meta:
        abstract = True


#this extension of User represents a nurse
class Nurse(User):
  #  hospital = models.OneToOneField(Hospital, null = True, blank = True)
    trusted = models.ManyToManyField('Doctor', blank = True)

    # TODO: add methods as they are needed,
    def getType(self):
        return "nurse"

# this extension of User represents a patient
class Patient(User):
    hospital = models.ForeignKey('hospital.Hospital', null=True, blank=True)
    doctor = models.ForeignKey('Doctor', null=True, blank=True)
    insuranceNum = models.CharField(max_length=12, default="", unique=True)
    emr = models.OneToOneField(EMR, null=True, blank=True)
    address = models.CharField(max_length=50, default="")
    email = models.CharField(max_length=50, default="")
    phone = models.CharField(max_length=10, default="")


    # TODO: add methods as they are needed,
    def getType(self):
        return "patient"


#this extension of User represents a doctor
class Doctor(User):
    hospitals = models.ManyToManyField(Hospital)
    patientCap = models.IntegerField(default=5)  # maximum number of patients a doctor can have

    # TODO: add methods as they are needed
    def getType(self):
        return "doctor"


######################################################################################
####################  Calendar Classes and work        ###############################
######################################################################################

class Calendar(models.Model):
    allEvents = models.ManyToManyField('Event')


class Event(models.Model):
    patient = models.ForeignKey('Patient')
    doctor = models.ForeignKey('Doctor')
    hospital = models.ForeignKey('hospital.Hospital')
    startTime = models.DateTimeField(default=timezone.now)
    endTime = models.DateTimeField()
