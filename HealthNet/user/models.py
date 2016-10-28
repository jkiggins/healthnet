from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
import datetime


class Nurse(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    hospital = models.OneToOneField('hospital.Hospital', null=True, blank=True)

    def __str__(self):
        return self.user.get_full_name()

    # TODO: add methods as they are needed,
    def getType(self):
        return "nurse"

# this extension of user represents a patient

class Patient(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    hospital = models.ForeignKey('hospital.Hospital', null=True, blank=True)
    doctor = models.ForeignKey('Doctor', null=True, blank=True)
    insuranceNum = models.CharField(max_length=12, default="")
    emr = models.OneToOneField('emr.EMR', null=True, blank=True)
    address = models.CharField(max_length=50, default="")
    phone = models.CharField(max_length=10, default="")

    def __str__(self):
        return self.user.get_full_name()


    # TODO: add methods as they are needed,
    def getType(self):
        return "patient"


#this extension of user represents a doctor

class Doctor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    hospitals = models.ManyToManyField('hospital.Hospital')
    patientCap = models.IntegerField(default=5)  # maximum number of patients a doctor can have

    def __str__(self):
        return self.user.get_full_name()

    # TODO: add methods as they are needed
    def getType(self):
        return "doctor"


class Event(models.Model):
    APP_BUFFER = datetime.timedelta(minutes=15)

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, null=True, blank=True)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, null=True, blank=True)
    hospital = models.ForeignKey('hospital.Hospital', null=True, blank=True)
    startTime = models.DateTimeField(default=timezone.now)
    endTime = models.DateTimeField()
    description = models.CharField(max_length=200, default="")
    appointment = models.BooleanField(default=False)


    def conflicts(self):
        """This method checks for conflicting events. This method should be run before saving any event
        0 - No conflicts
        1 - The event is too long and extends into another event
        2 - The event starts before the end of another event
        """

        if self.doctor.event_set.filter(startTime__lte=self.endTime).filter(startTime__gte=self.startTime).count() != 0:
            return 1
        if self.doctor.event_set.filter(endTime__lte=self.endTime).filter(endTime__gte=self.startTime).count() != 0:
            return 2

        if self.appointment:
            if self.patient.event_set.filter(startTime__lte=self.endTime+Event.APP_BUFFER).filter(startTime__gte=self.startTime-Event.APP_BUFFER).count() != 0:
                return 1
            if self.patient.event_set.filter(endTime__lte=self.endTime).filter(endTime__gte=self.startTime).count() != 0:
                return 2

        return 0

    def getType(self):
        return "event"




