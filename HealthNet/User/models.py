from django.db import models
from Calendar.models import Calendar

# Create your models here.

class User(models.Model):

    Calendar = models.ForeignKey(Calendar , on_delete=models.CASCADE)
    
    #Notification = models.ForeignKey(Notification , on_delete=models.CASCADE)

    class Meta:
        abstract = True