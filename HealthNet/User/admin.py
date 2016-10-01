from django.contrib import admin
from User.models import Patient, Nurse, Doctor

# Register your models here.
admin.site.register(Patient)
admin.site.register(Nurse)
admin.site.register(Doctor)