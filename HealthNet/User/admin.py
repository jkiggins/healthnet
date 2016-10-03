from django.contrib import admin
from User.models import *

# Register your models here.
admin.site.register(Patient)
admin.site.register(Nurse)
admin.site.register(Doctor)
admin.site.register(Event)
admin.site.register(Calendar)