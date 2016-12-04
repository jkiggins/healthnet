import csv
from user.models import *
from hospital.models import *
from emr.models import *
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

def makeDjangoUser(username, password, first_name, last_name):
    return User.objects.create_user(username=username,
                                         password=password,
                                         first_name=first_name,
                                         last_name=last_name)


def makeDoctor(user, patientCap):
    return Doctor.objects.get_or_create(user=user,
                                 patientCap=patientCap)[0]

def makeNurse(user, hospital):
    return Nurse.objects.get_or_create(user=user,
                                       hospital=hospital)[0]


def makePatient(*args):
    return Patient.objects.get_or_create(user=args[0],
                                         doctor=args[1],
                                         hospital=args[2],
                                         insuranceNum=args[3],
                                         phone=args[4])[0]

def makeHosAdmin(*args):
    return HospitalAdmin.objects.get_or_create(user=args[0],
                                               hospital=args[1])[0]

def getDoctorByUname(uname):
    user = User.objects.get(username=uname)
    if hasattr(user, 'doctor'):
        return user.doctor

def getHospitalByName(name):
    return Hospital.objects.get(name=name)

def makeHos(name):
    return Hospital.objects.get_or_create(name=name)[0]

def printForTest():
    print("Hospitals: {0}".format(Hospital.objects.all()))
    print("Doctors: {0}".format(Doctor.objects.all()))
    print("Nurse: {0}".format(Nurse.objects.all()))
    print("Patients: {0}".format(Patient.objects.all()))
    print("Hospital Admin: {0}".format(HospitalAdmin.objects.all()))

    for doc in Doctor.objects.all().exclude(nurses=None):
        print("Doctor {0} Trusts: ".format(doc.user.username))
        for nurse in doc.nurses.all():
            print("\t"+nurse.user.username)



class Command(BaseCommand):

    def cleanCSVReader(self, file):
        read = csv.reader(file)
        next(read)
        ret = [[x.strip() for x in row] for row in read]
        return ret

    def handleDoctors(self, mpath):
        with open(mpath) as csvfile:
            """Username,password,first_name,last_name,max_capacity,[phone_number],hospital1,[hospital2, …]"""
            doctors = self.cleanCSVReader(csvfile)

            for row in doctors:
                u = makeDjangoUser(*row[:4])
                u.save()

                pcap = int(row[4])
                d = makeDoctor(u, pcap)
                for hos in row[6:]:
                    d.hospitals.add(makeHos(hos))

                d.save()


    def handleNurses(self, mpath):
        with open(mpath) as csvfile:
            """Username,password,first_name,last_name,hospital,[phone_number],doctor1,[doctor2…]"""
            nurses = self.cleanCSVReader(csvfile)

            for row in nurses:
                u = makeDjangoUser(*row[:4])
                u.save()

                h = makeHos(row[4])

                n = makeNurse(u, h)
                n.accepted = True
                n.save()

                for doc in row[6:]:
                    d = getDoctorByUname(doc)
                    if not(d is None):
                        d.nurses.add(n)
                        d.save()
                    else:
                        print("error adding nurse: {0} to doctor: {1} 's Trusted list, Doctor Doesnt Exist".format(n.user.usernname, doc))


    def handlePatients(self, mpath):
        with open(mpath) as csvfile:
            """patient_email,patient_password,first_name,last_name,insurance_number,birth_date,sex, Doctor,hospital,[phone, address,emergency_contact_first,emergency_contact_last, emergency_contact_phone]"""
            patients = self.cleanCSVReader(csvfile)

            for row in patients:
                u = makeDjangoUser(*row[:4])
                u.save()

                d = getDoctorByUname(row[7])
                d.accepted=True
                d.save()

                h = getHospitalByName(row[8])
                p = makePatient(u, d, h, row[4], row[9])
                p.save()


    def handleHosAdmin(self, mpath):
        with open(mpath) as csvfile:
            """Username,password,first_name,last_name,Hospital"""
            HosAdmins = self.cleanCSVReader(csvfile)

            for row in HosAdmins:
                u = makeDjangoUser(*row[:4])
                u.save()

                h = getHospitalByName(row[4])
                ha = makeHosAdmin(u, h)
                ha.save()


    def handle(self, **options):

        Hospital.objects.all().delete()
        User.objects.all().delete()
        Doctor.objects.all().delete()
        Patient.objects.all().delete()
        Nurse.objects.all().delete()
        HospitalAdmin.objects.all().delete()

        self.handleDoctors('media/csv/doctor.csv')
        self.handleNurses('media/csv/nurse.csv')
        self.handlePatients('media/csv/patient.csv')
        self.handleHosAdmin('media/csv/hosadmin.csv')

        printForTest()




