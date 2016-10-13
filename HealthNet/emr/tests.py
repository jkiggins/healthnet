from django.test import TestCase
import datetime
from django.utils import timezone
from .models import EMR, EMRItem, EMRVitals, EMRNote

class EMRMethodTests(TestCase):

    def createEMRInDatabase(self):
        charTest = "TestEMR"
        testEMR = EMR(emergency=charTest)
        self.assertIsInstance(EMR,msg="Object is not an EMR")