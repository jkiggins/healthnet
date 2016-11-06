def getAttrIfExists(obj, attr):
    if hasattr(obj, attr):
        return getattr(obj, attr)
    return None

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
        auth |= user == event.doctor
        auth |= user == event.patient

        if utype == 'nurse':
            auth |= (user in event.doctor.nurses.all())
        elif utype == 'hosAdmin':
            auth |= (user.hospital in event.doctor.hospitals.all())

    if 'create' in actions:
        if utype == 'patient':
            auth |= not(user.doctor is None) and not(user.hospital is None)

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
        elif (tutype == 'patient' and utype == 'doctor'):
            auth |= (tuser.hospital in cuser.hospitals.all())
        elif (tutype == 'patient'):
            auth |= not((tuser.hospital is None) or (tuser.doctor is None))

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
    auth = False
    utype = cuser.getType()

    if 'view' in actions:
        if utype == 'patient':
            return False
        elif utype == 'doctor':
            auth |= patient in cuser.patient_set.all()
            auth |= patient.hospital in cuser.hospitals.all()
        elif utype == 'nurse':
            auth |= patient.hospital == cuser.hospital

        auth |= utype == 'hosAdmin'

    if 'view_hidden' in actions:
        if utype == 'patient':
            return False

    if 'edit' in actions:
        if utype == 'doctor':
            auth |= patient.hospital in cuser.hospitals.all()
        elif utype == 'nurse':
            auth |= nurseIsTrusted(cuser, patient.doctor)
        else:
            auth |= (cuser.getType() == 'hosAdmin') and (cuser.hospital == patient.hospital)

    if 'vitals' in actions:
        if utype == 'patient':
            auth |= (patient == cuser)

    if 'admit' in actions:
        if utype == 'doctor':
            auth |= patient.hospital in cuser.hospitals.all()
        elif utype in ['nurse', 'hosAdmin']:
            auth |= patient.hospital == cuser.hospital

    return auth



