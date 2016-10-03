from django.db import models
from django.utils import timezone

class EMR(models.Model):
    """This model will be used to link test results, vitals, diagnosis, medications, and notee"""
    # TODO: determine if there are any fields that should be in this model
    emergency = models.CharField(max_length=10, default="")  # emergency contact

class EMRItem(models.Model):
    """This is generic item which can be stored in the EMR, other models will extend this"""
    emr = models.ForeignKey(EMR, on_delete=models.CASCADE, null=True, blank=True)
    dateCreated = models.DateTimeField(default=timezone.now)
    # appointment = models.ForeignKey(Appointment)  # the ability to link each emr item to an appointment associated with its creation

    class Meta:
        abstract = True


class EMRVitals(EMRItem):
    """This model will store a set of vital sign readings as well as height, weight ...etc"""
    restingBPM = models.IntegerField(default=0)  # Resting pulse in beats/min
    bloodPressure = models.CharField(max_length=10, default="")  # Blood pressure in format ###/###
    height = models.FloatField(default=0)  # Height of the patient in inches
    weight = models.FloatField(default=0)  # Weight of a person in Lbs
    age = models.IntegerField(default=0)
    comments = models.CharField(max_length=1000, default="")
    # TODO: add more vitals

class EMRNote(EMRItem):
    comments = models.CharField(max_length=500, default="")
    # TODO: decide if we want to use markdown formatting

class EMRTrackedMetric(EMRItem):
    """This model is a generic tracked metric, meaning a provider can track some arbitrary detail about a patient
    across different appointments"""
    label = models.CharField(max_length=200, default="")  # unique label for metric
    comments = models.CharField(max_length=500, default="")  # comments about the metric, this may be a simple as a number or consist of a few sentences