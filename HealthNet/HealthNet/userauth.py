from emr.models import *
from .viewhelper import *

def getAttrIfExists(obj, attr):
    if hasattr(obj, attr):
        return getattr(obj, attr)
    return None


def nurseIsTrusted(nurse, doctor):
    return (nurse in doctor.nurses.all())


def userCanMessage(user):
    if user.getType() == 'patient':
        return False
    return True


def userCan_Event(user, event, *actions):

    auth = True
    utype = user.getType()

    if 'view' in actions:
        if utype == 'patient' and user.accepted == False:
            print(0)
            return False

        auth |= user == event.patient
        auth |= user == event.doctor

        if utype == 'doctor' and not(event.patient is None):
            auth |= event.patient.hospital in user.hospitals.all()
            auth |= event.patient.admittedHospital() in user.hospitals.all()  # Admission
        if utype in ['nurse', 'hosAdmin']:
            auth |= event.hospital == user.hospital
            auth |= event.patient.admittedHospital() == user.hospital  # Admission

            if utype == 'hosAdmin':
                auth |= (user.hospital in event.doctor.hospitals.all())


    if 'edit' in actions:
        auth_l = False

        if isPatient(user) and user.accepted == False:
            print(1)
            return False

        auth_l |= user == event.doctor
        auth_l |= user == event.patient


        if utype == 'nurse':
            auth |= (user in event.doctor.nurses.all()) or not(event.patient is None)
        elif utype == 'hosAdmin':
            auth |= (user.hospital in event.doctor.hospitals.all())

        if utype != 'hosadmin' and auth_l:
            auth_l &= (timezone.now() - event.startTime) < datetime.timedelta(minutes=0)

        print("edit")
        auth &= auth_l


    if 'create' in actions:
        auth_l = True
        print(utype)
        print(user.accepted)
        if utype == 'patient' and user.accepted == False:
            print(2)
            return False
        elif utype == 'patient':
            auth |= True
        else:
            auth_l = True
        print("create")
        auth &= auth_l


    if 'cancel' in actions:
        auth_l = False

        if isPatient(user):
            auth_l |= (event.startTime - timezone.now()) < datetime.timedelta(hours=48)
            auth_l &= user.accepted

        elif not('edit' in actions):
            auth_l = userCan_Event(user, event, 'edit')
        else:
            auth_l = True
        print("cancel")
        auth &= auth_l

    return auth


def userCan_Profile(cuser, tuser, *actions):

    auth_l = False
    utype = cuser.getType()
    tutype = tuser.getType()



    if 'view' in actions:


        if(utype == 'nurse' and tutype == 'doctor'):
            auth_l |= (cuser.hospital in tuser.hospitals.all())
        elif (tutype == 'nurse' and utype == 'doctor'):
            auth_l |= (tuser.hospital in cuser.hospitals.all())
        elif (tutype == 'doctor' and utype == 'doctor'):
            auth_l |= (tuser.hospitals.all() & cuser.hospitals.all()).count() > 0
        elif (tutype == 'nurse' and utype == 'nurse'):
            auth_l |= (tuser.hospital == cuser.hospital)
        elif (tutype == 'patient' and utype == 'doctor'):
            auth_l |= (tuser.hospital in cuser.hospitals.all()) or (tuser.admittedHospital() in cuser.hospitals.all()) # Admission
        elif (tuser.user.pk==cuser.user.pk):
            auth_l |= True

        auth_l |= (utype == 'hosAdmin')

    if 'edit' in actions:
        auth_l |= (utype == 'hosAdmin')
        auth_l |= (utype == 'patient') and (cuser.user.pk == tuser.user.pk)

        if not ('view' in actions):
            auth_l &= userCan_Profile(cuser, tuser, 'view')

    return auth_l


def userCan_Registry(user, *actions):
    auth = False

    if 'view' in actions:
        auth |= (user.getType() != 'patient')

    return auth


def isHAdmin(user):
    return user.getType() == 'hosAdmin'


def userCan_EMR(cuser, patient, *actions):
    auth = True
    utype = cuser.getType()

    if 'view' in actions:
        auth_l = False
        if utype == 'patient' and not cuser.accepted:
            return False
        elif utype == 'patient' and cuser.accepted:
            return True
        elif utype == 'doctor':
            auth_l |= patient.hospital in cuser.hospitals.all()
            auth_l |= patient.admittedHospital() in cuser.hospitals.all() # Admission
        elif utype == 'nurse':
            auth_l |= patient.hospital == cuser.hospital
            auth_l |= patient.admittedHospital() == cuser.hospital
        auth_l |= (utype == 'hosAdmin')
        auth &= auth_l

    if 'prescribe' in actions:
        auth_l = False
        if utype == 'doctor':
            auth_l |= patient.hospital in cuser.hospitals.all()
            auth_l |= patient.admittedHospital() in cuser.hospitals.all()  # Admission
        elif utype == 'hosAdmin':
            auth_l |= patient.hospital == cuser.hospital
            auth_l |= patient.admittedHospital() == cuser.hospital
        auth &= auth_l

    if 'view_hidden' in actions:
        if utype == 'patient':
            return False
        elif not ('view' in actions):
            auth &= userCan_EMR(cuser, patient, 'view')

    if 'edit' in actions:
        if utype != 'patient' and not('view' in actions):
            auth &= userCan_EMR(cuser, patient, 'view')
        else:
            return False


    if 'vitals' in actions:
        auth_l=userCan_EMR(cuser, patient, 'edit')
        if utype == 'patient' and cuser.accepted == False:
            return False
        elif utype == 'patient':
            auth_l |= (patient == cuser)
        auth &= auth_l

    if 'admit' in actions:
        auth_l=False
        if utype == 'doctor':
            auth_l |= patient.hospital in cuser.hospitals.all()
            auth_l |= patient.admittedHospital() in cuser.hospitals.all()
        elif utype in ['nurse', 'hosAdmin']:
            auth_l |= patient.hospital == cuser.hospital
        auth &= auth_l

    if 'dishcharge' in actions:
        auth_l=False
        if utype in ['doctor', 'hosAdmin']:
            auth_l = userCan_EMR(cuser, patient, 'admit')
        elif utype == 'nurse':
            return False

    return auth


def userCan_EMRItem(cuser, item, *actions):
    auth = True

    if 'view' in actions:
        auth_l = False

        if cuser.getType() == 'patient' and cuser.accepted == False:
            return False
        elif cuser.getType() == 'doctor':
            auth_l |= item.patient.hospital in cuser.hospitals.all()
        elif cuser.getType() == 'patient':
            if isTest(item):
                auth_l |= item.emrtest.released
            else:
                auth_l = True
        elif cuser.getType() == 'nurse':
            auth_l |= item.patient.hospital == cuser.hospital
        auth &= auth_l

    if 'edit' in actions:
        auth_l = False
        if cuser.getType() == 'patient':
            return False
        else:
            auth_l = True
        auth_l &= userCan_EMRItem(cuser, item, 'view')
        auth &= auth_l

    return auth


def userCan_stats(user, *actions):
    auth = True

    if 'view' in actions:
        auth &= not isPatient(user)

    return auth
