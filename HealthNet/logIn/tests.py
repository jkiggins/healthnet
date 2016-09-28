from django.test import TestCase

def RegistrationTests(TestCase):

    def test_register_a_patient_by_form():
        """Attempt To register a user and make sure they show up in the database"""

    def test_register_a_patient_twice():
        """Attempt to register a patient twice, make sure the appropriate message is displayed"""
        #TODO: determine what message is returned

    def test_invalid_insurace_numer():
        """Attept to register a user with an invalid insurance Number, make sure it redirects to health insurance website"""

def LoginTests(TestCase):

    def test_login_form_patient():
        """Create a new patient and attempt to login as that user"""

    def test_login_form_nurse():
        """Create a new nurse and attempt to login"""

    def test_login_form_doctor():
        """Create a new Doctor and attempt to login as doctor"""

    def attempt_to_login_with_fake_user():
        """Attempt to login with fake user and make sure it redirects to approprate page"""
        #TODO: figure out what page it would redrect to

