from User.models import *
from hospital.models import *



h = Hospital.objects.create(name="The hospital")
h.save()


d = Doctor.objects.create(UserName="testud", Password="pass", firstName="Doctor", lastName="Strange")
d.hospital = h
d.save()


p = Patient.objects.create(UserName="testu", Password="pass", firstName="Patient", lastName="Zero")

p.hospital = h
p.save()
p.doctor = d
p.save()

n = Nurse.objects.create(UserName="testn", Password="pass", firstName="The", lastName="Nurse")
n.save()