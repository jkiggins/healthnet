from django.db import models
from django.utils import timezone

class Syslog(models.Model):
    type = models.CharField(max_length=50, default="")  # Log type/heading (i.e Appointment Created, EMR viewing)
    message = models.CharField(max_length=200, default="")  # Log message, usually generated by the system
    date_created = models.DateTimeField(default=timezone.now)

    @staticmethod
    def log(_type, _message):
        Syslog.objects.create(type=_type, message = _message, date_created = timezone.now())

    @staticmethod
    def logUser(_type, _message, _user):
        _message += ":{0}, {1}".format(_user.lastName, _user.firstName)
        Syslog.log(_type, _message)

    @staticmethod
    def deleteEvent(event, user):
        Syslog.objects.create(type="Delete", message = "User: {0} deleted event: {1}".format(user.user.get_full_name(), event.description))
        event.delete()

    @staticmethod
    def modifyEvent(event, user):
        Syslog.objects.create(type = "Modify", message = "User: {0} modified event: {1} with primary key: {3}".format(user.user.get_full_name(), event.description, event.id))

    @staticmethod
    def viewEMR(emr, user):
        Syslog.objects.create(type="View", message="User: {0} viewed emr log with primary key {1}".format(user.user.get_full_name(), emr.id))

    @staticmethod
    def createEvent(event, user):
        Syslog.objects.create(type="Create", message="User: {0} created event with description: {1} and primary key {2}".format(user.user.get_full_name(), event.description, event.id))