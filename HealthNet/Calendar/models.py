2
from django.db import models

# Create your models here.


class Calendar(models.Model):
    """This model will hold the events for each user and provide an interface for rendering the calendar"""


class Notification(models.Model):
    """This model will define a notification. Notifications have a many-to-many relationship with users"""
