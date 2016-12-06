import csv
from user.models import *
from hospital.models import *
from emr.models import *
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand



class Command(BaseCommand):

    blankpass=False
    def add_arguments(self, parser):
        parser.add_argument(
            '--blankpass',
            action='store_true',
            dest='blankpass',
            default=False,
            help='Use this option if you want the csv to export users with blank passwords',
        )

    def set_pass(self, row, index, tpass):
        if not self.blankpass:
            row[index] = tpass

    def handleDoctors(self, mpath):

        with open(mpath, 'w+', newline='') as csvfile:
            """Username,password,first_name,last_name,max_capacity,[phone_number],hospital1,[hospital2, …]"""
            doctors = csv.writer(csvfile)
            row = []
            for d in Doctor.objects.all().filter(accepted=True):
                row = [d.user.username, "", d.user.first_name, d.user.last_name, d.patientCap, ""]
                self.set_pass(row, 1, d.user.password)
                for h in d.hospitals.all():
                    row.append(h.name)

                doctors.writerow(row)

    def handleNurses(self, mpath):
        with open(mpath, 'w+', newline='') as csvfile:
            """Username,password,first_name,last_name,hospital,[phone_number],doctor1,[doctor2…]"""
            nurses = csv.writer(csvfile)
            row = []
            for n in Nurse.objects.all().filter(accepted=True):
                row = [n.user.username, "", n.user.first_name, n.user.last_name, n.hospital, ""]
                self.set_pass(row, 1, n.user.password)
                for d in n.doctor_set.all():
                    row.append(d.user.username)

                nurses.writerow(row)

    def handlePatients(self, mpath):
        with open(mpath, 'w+', newline='') as csvfile:
            """patient_email,patient_password,first_name,last_name,insurance_number,birth_date,sex, Doctor,hospital,
            [phone, address,emergency_contact_first,emergency_contact_last, emergency_contact_phone]"""

            patients = csv.writer(csvfile)
            row = []
            for p in Patient.objects.all().filter(accepted=True):
                row = [p.user.username, "", p.user.first_name, p.user.last_name, p.insuranceNum,
                       "", "", p.doctor.user.username,
                       p.hospital.name, p.phone, p.address, "", "", ""]

                if hasattr(p, "emrprofile") and not (p.emrprofile is None):
                    row[5] = p.emrprofile.birthdate.strftime('%m/%d/%Y')
                    row[6] = p.emrprofile.gender

                self.set_pass(row, 1, p.user.password)

                if not (p.contact is None):
                    p.contact.updateFromUser()
                    row[-3] = p.contact.full_name
                    row[-2] = ""
                    row[-1] = p.contact.emphone

                patients.writerow(row)



    def handle(self, **options):

        self.blankpass = options['blankpass']

        self.handleDoctors('media/csv/doctor_export.csv')
        self.handleNurses('media/csv/nurse_export.csv')
        self.handlePatients('media/csv/patient_export.csv')