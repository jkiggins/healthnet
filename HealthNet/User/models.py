from django.db import models
from Calendar.models import Calendar
from Hospital.models import Hospital

# Create your models here.

class User(models.Model):

    Calendar = models.ForeignKey(Calendar , on_delete=models.CASCADE)
    UserName = models.CharField(max_length=15)
    Password = models.CharField(max_length=20)
    Hospital = models.ForeignKey(Hospital , on_delete=models.CASCADE)
    #Notification = models.ForeignKey(Notification , on_delete=models.CASCADE)

    class Meta:
        abstract = True