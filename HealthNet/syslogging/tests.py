from django.test import TestCase

def login_as_admin():
    """This will use the login app to login as an administrator, giving the tests full url access"""

def create_test_patient():
    """This will create a test patient for testing purposes"""

class SystemLogCreationTest():

    def test_patient_create_syslog(self):
        """A patient is created and the resulting log is verified"""

    def test_appointment_create_syslog(selfs):
        """An appointment is created and the resulting log is verified"""

    def test_emr_view_create_syslog(self):
        """request the emr as an admin, ensure a syslog is created"""

    def test_patient_profile_view_syslog(self):
        """request a patients profile, ensure a syslog is created"""

    def test_patient_profile_update_syslog(self):
        """modify a patients proflile and ensure an syslog is created"""

    def test_transfer_patient_syslog(self):
        """Transfer a patient and ensure an syslog is created"""

    def test_admit_patient_syslog(self):
        """Admit a patient to a hospital and ensure syslog is created"""
