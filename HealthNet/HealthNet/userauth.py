from emr.models import *

def getAttrIfExists(obj, attr):
    if hasattr(obj, attr):
        return getattr(obj, attr)
    return None


def patientHasCompletedProfile(user):
    if user.getType() == "patient":
        auth=True
        auth &= not((user.hospital is None) or (user.doctor is None))
        auth &= (user.user.get_full_name() != '') and (user.phone != '') and (user.address != '')
        auth &= not(user.contact is None)

        return auth

    return True


def nurseIsTrusted(nurse, doctor):
    return (nurse in doctor.nurses.all())


def userCan_Event(user, event, *actions):

    auth = False
    utype = user.getType()

    if 'view' in actions:
        auth |= user == event.patient
        auth |= user == event.doctor

        if utype == 'doctor' and not(event.patient is None):
            auth |= event.patient.hospital in user.hospitals.all()
        if utype in ['nurse', 'hosAdmin']:
            auth |= event.hospital == user.hospital

            if utype == 'hadmin':
                auth |= (user.hospital in event.doctor.hospitals.all())

    if 'edit' in actions:
        auth_l = False
        auth_l |= user == event.doctor
        auth_l |= user == event.patient

        if utype == 'nurse':
            auth |= (user in event.doctor.nurses.all())
        elif utype == 'hosAdmin':
            auth |= (user.hospital in event.doctor.hospitals.all())

        if utype != 'hosadmin':
            auth_l &= (timezone.now() - event.startTime) < datetime.timedelta(minutes=15)

        auth &= auth_l

    if 'create' in actions:
        if utype == 'patient':
            auth |= patientHasCompletedProfile(user)
        else:
            auth = True

    return auth


def userCan_Profile(cuser, tuser, *actions):

    auth = False
    utype = cuser.getType()
    tutype = tuser.getType()

    if 'view' in actions:
        if(utype == 'nurse' and tutype == 'doctor'):
            auth |= (cuser.hospital in tuser.hospitals.all())
        elif (tutype == 'nurse' and utype == 'doctor'):
            auth |= (tuser.hospital in cuser.hospitals.all())
        elif (tutype == 'doctor' and utype == 'doctor'):
            auth |= (tuser.hospitals.all() & cuser.hospitals.all()).count() > 0
        elif (tutype == 'nurse' and utype == 'nurse'):
            auth |= (tuser.hospital == cuser.hospital)
        elif (tutype == "patient" and utype == "doctor"):
            auth |= (tuser.hospital in cuser.hospitals.all()) or (tuser.admittedHospital() in cuser.hospitals.all())
        elif (tuser.pk==cuser.pk):
            auth |= patientHasCompletedProfile(tuser)

        auth |= (utype == 'hosAdmin')

    if 'edit' in actions:
        auth |= (utype == 'hosAdmin')
        auth |= (utype == 'patient') and (cuser.user.pk == tuser.user.pk)

    return auth


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
        if utype == 'patient':
            return patientHasCompletedProfile(cuser)
        elif utype == 'doctor':
            auth_l |= patient in cuser.patient_set.all().filter(accepted=True)
            auth_l |= patient.hospital in cuser.hospitals.all()
        elif utype == 'nurse':
            auth_l |= patient.hospital == cuser.hospital
        auth_l |= (utype == 'hosAdmin')
        auth &= auth_l

    if 'prescribe' in actions:
        auth_l = False
        if utype == 'doctor':
            auth_l |= patient.hospital in cuser.hospitals.all()
        elif utype == 'hosAdmin':
            auth_l |= patient.hospital == cuser.hospital
        auth &= auth_l

    if 'view_hidden' in actions:
        if utype == 'patient':
            return False

    if 'edit' in actions:
        auth_l=False
        if utype == 'doctor':
            auth_l |= patient.hospital in cuser.hospitals.all()
        elif utype == 'nurse':
            auth_l |= nurseIsTrusted(cuser, patient.doctor)
        else:
            auth_l |= (cuser.getType() == 'hosAdmin') and (cuser.hospital == patient.hospital)
        auth &= auth_l

    if 'vitals' in actions:
        auth_l=False
        if utype == 'patient':
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

        if cuser.getType() == 'doctor':
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


