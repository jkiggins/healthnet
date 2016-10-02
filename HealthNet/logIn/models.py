from django.db import models



# Create your models here.

class logIn(models.Model):
    errorstate = models.BooleanField(default=False)


    def __str__(self):
        return str(self.name)