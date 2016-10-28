from django.contrib import admin
from user.models import *

# Register your models here.
admin.site.register(Patient)
admin.site.register(Nurse)
admin.site.register(Doctor)
admin.site.register(Event)