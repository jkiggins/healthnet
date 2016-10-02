from django.test import TestCase

from .models import *
from hospital.models import Hospital
from django.utils import timezone
import datetime

def setup_environment():
    hospital = Hospital.objects.create(name="theHospital")
    d_calendar = Calendar.objects.create()
    p_calendar = Calendar.objects.create()

    doctor = Doctor.objects.create(firstName = "doctor", lastName = "strange", Calendar=d_calendar)
    doctor.hospitals.add(hospital)

    patient = Patient.objects.create(firstName = "patient", lastName = "Zero", Calendar = p_calendar, hospital = hospital)

    st = timezone.now()+datetime.timedelta(days=1)  # Start time for fake event
    et = timezone.now()+datetime.timedelta(days=1, hours=2) # End time for fake event

    e = Event.objects.create(patient=patient, doctor = doctor, hospital=hospital, startTime=st, endTime = et, description = "Test")

    patient.Calendar.allEvents.add(e)
    doctor.Calendar.allEvents.add(e)

    patient.save()
    doctor.save()

    return patient.id == doctor.id


class CalendarViewTest(TestCase):
    def test_setup_environment(self):
        """This test simply makes sure we can set up a database environment"""
        setup_environment()