from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

# Create your models here.
""""class User(models.Model):
    Calendar = models.OneToOneField('Calendar', null=true, on_delete=models.CASCADE)
    UserName = models.CharField(max_length=15, default="")
    Password = models.CharField(max_length=20, default="")

    firstName = models.CharField(max_length=20, default="")
    lastName = models.CharField(max_length=20, default="")
    # name = models.CharField(max_length=30)

    def __str__(self):
        return self.firstName + ", " + self.lastName

    class Meta:
        abstract = True"""


#this extension of User represents a nurse

class Nurse(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    hospital = models.OneToOneField('hospital.Hospital', null=True, blank=True)
    trusted = models.ManyToManyField('Doctor', blank = True)

    def __str__(self):
        return user.get_full_name()

    # TODO: add methods as they are needed,
    def getType(self):
        return "nurse"

# this extension of User represents a patient

class Patient(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    hospital = models.ForeignKey('hospital.Hospital', null=True, blank=True)
    doctor = models.ForeignKey('Doctor', null=True, blank=True)
    insuranceNum = models.CharField(max_length=12, default="")
    emr = models.OneToOneField('emr.EMR', null=True, blank=True)
    address = models.CharField(max_length=50, default="")
    phone = models.CharField(max_length=10, default="")

    def __str__(self):
        return user.get_full_name()


    # TODO: add methods as they are needed,
    def getType(self):
        return "patient"


#this extension of User represents a doctor

class Doctor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    hospitals = models.ManyToManyField('hospital.Hospital')
    patientCap = models.IntegerField(default=5)  # maximum number of patients a doctor can have

    def __str__(self):
        return user.get_full_name()

    # TODO: add methods as they are needed
    def getType(self):
        return "doctor"


######################################################################################
####################  Calendar Classes and work  #####################################
######################################################################################

class Event(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, null=True, blank=True)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, null=True, blank=True)
    hospital = models.ForeignKey('hospital.Hospital', null=True, blank=True)
    startTime = models.DateTimeField(default=timezone.now)
    endTime = models.DateTimeField()
    description = models.CharField(max_length=200, default="")
    appointment = models.BooleanField(default=False)

    def getType(self):
        return "event"




