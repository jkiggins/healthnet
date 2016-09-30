from django.db import models

#from Calendar.models import Calendar
#from hospital.models import Hospital
#from EMR.models import EMR

#from Hospital.models import Hospital
from Calendar.models import Calendar, Notification
from hospital.models import Hospital
from EMR.models import EMR


# Create your models here.
class User(models.Model):


    Calendar = models.ForeignKey(Calendar , on_delete=models.CASCADE)
    UserName = models.CharField(max_length=15)
    Password = models.CharField(max_length=20)
    Hospital = models.ForeignKey(Hospital , on_delete=models.CASCADE)
    Notification = models.ForeignKey(Notification , on_delete=models.CASCADE)


    class Meta:
        abstract = True

    def __str__(self):
        return str(self.name)

# this extension of User represents a patient
class Patient(User):
    insuranceNum = models.CharField(max_length=12)
    EMR = models.ForeignKey(EMR, on_delete=models.CASCADE)
