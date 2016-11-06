from django.test import TestCase
from emr.models import *
from user.models import *
from hospital.models import Hospital
import datetime
from django.utils import timezone

class EMRMethodTests(TestCase):

    def setUp(self):
        """sets up the Environment to test in"""
        # ============= CREATE USERS =============
        # HOSPITAL
        h = Hospital.objects.create(name="The Hospital")
        # DOCTOR
        ud = User.objects.create_user(
            username="doc",
            password="pass",
            email="",
            first_name="Doc",
            last_name="Martin")
        d = Doctor.objects.create(user=ud)
        d.hospitals.add(h)
        # PATIENT
        up = User.objects.create_user(
            username="pat",
            password="pass",
            email="",
            first_name="Pat",
            last_name="Star")
        Patient.objects.create(user=up, doctor=d, hospital=h)
        # NURSE
        un = User.objects.create_user(
            username="nurse",
            password="pass",
            email="",
            first_name="Nurse",
            last_name="Joy")
        Nurse.objects.create(user=un, hospital=h)
        # HOSPTIAL ADMIN
        uha = User.objects.create_user(
            username="hosadmin",
            password="pass",
            email="",
            first_name="Kid",
            last_name="Cudi")
        HospitalAdmin.objects.create(user=uha, hospital=h)

    def test_createGenericEMRInDatabase(self):

        testEMR = EMRItem(title="TestEMR",
                          patient=Patient.objects.all()[0],
                          date_created=timezone.now,
                          content="test",
                          priority=0
                          )
        self.assertIsInstance(testEMR,EMRItem, msg="Object is not an EMR")



