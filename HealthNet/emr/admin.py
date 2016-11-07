from django.contrib import admin
from .models import *

# Register your models here.

admin.site.register(EMRItem)
admin.site.register(EMRPrescription)
admin.site.register(EMRTest)
admin.site.register(EMRVitals)