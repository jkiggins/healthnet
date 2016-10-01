from django.db import models
# Create your models here.


class Hospital(models.Model):
    name = models.CharField(max_length=200, default="")

    def __str__(self):
        return str(self.name)
