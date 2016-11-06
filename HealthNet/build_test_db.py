from user.models import *
from hospital.models import Hospital
from emr.models import *
from django.contrib.auth.models import Permission, User

Hospital.objects.all().delete()
User.objects.all().delete()
Doctor.objects.all().delete()
Patient.objects.all().delete()

h = Hospital.objects.create(name="The Hospital")
h.save()

h1 = Hospital.objects.create(name="Eht Hospital")
h1.save()

ud = User.objects.create_user(
            username="drstrange",  # cleaned_data is autogenerated data. can be modified in form
            password="pass",
            email="",
            first_name="Doctor",
            last_name="Strange"
        )
ud.save()
d = Doctor.objects.create(user=ud)
d.hospitals.add(h)
d.hospitals.add(h1)
d.save()

ud = User.objects.create_user(
            username="drnormal",  # cleaned_data is autogenerated data. can be modified in form
            password="pass",
            email="",
            first_name="Doctor",
            last_name="Normal"
        )
ud.save()
d = Doctor.objects.create(user=ud)
d.hospitals.add(h)
d.save()




up = User.objects.create_user(
            username="patientzero",  # cleaned_data is autogenerated data. can be modified in form
            password="pass",
            email="",
            first_name="Patient",
            last_name="Zero")
up.save()

p = Patient.objects.create(user=up, doctor = d, hospital=h)
p.save()

up = User.objects.create_user(
    username="patientone",  # cleaned_data is autogenerated data. can be modified in form
    password="pass",
    email="",
    first_name="Patient",
    last_name="One")
up.save()


p = Patient.objects.create(user=up, doctor=d, hospital=h1)
p.save()


un = User.objects.create_user(
            username="nursenormal",  # cleaned_data is autogenerated data. can be modified in form
            password="pass",
            email="",
            first_name="Nurse",
            last_name="Normal")
un.save()
n = Nurse.objects.create(user=un, hospital=h)
n.save()


uha = User.objects.create_user(
            username="cudi",  # cleaned_data is autogenerated data. can be modified in form
            password="pass",
            email="",
            first_name="Kid",
            last_name="Cudi")
uha.save()
ha = HospitalAdmin.objects.create(user=uha, hospital=h1)
ha.save()