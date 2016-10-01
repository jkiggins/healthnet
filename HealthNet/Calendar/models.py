from django.db import models
from django.forms import ModelForm
from django.utils import timezone

import datetime


# Create your models here.
class Calendar(models.Model):
    """This model will hold the events for each user and provide an interface for rendering the calendar"""
    allEvents = models.ManyToManyField('Event')


class Event(models.Model):
#    patient = models.ForeignKey('Patient', related_name='appointments')
#    doctor = models.ForeignKey('Doctor', related_name='appointments')
    startTime = models.DateTimeField(default=timezone.now)
    endTime = models.DateTimeField(default=timezone.now)
#    hospital = models.ForeignKey('Hospital')

#    def __str__(self):
#        return "Patient: " + self.patient.UserName + \
#                " Doctor: " + self.doctor.UserName


#class EventForm(ModelForm):
#    class Meta:
#        model = Event
#        fields = ['patient', 'doctor', 'hospital', 'startTime', 'endTime']



class Notification(models.Model):
    """This model will define a notification. Notifications have a many-to-many relationship with users"""
