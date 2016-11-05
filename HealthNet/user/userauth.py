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
            auth |= list(set(tuser.hospitals.all()) & set(cuser.hospitals.all())).count() > 0
        elif (tutype == 'nurse' and utype == 'nurse'):
            auth |= (tuser.hospital == cuser.hospital)
        elif (tutype == 'patient' and utype == 'doctor'):
            auth |= (cuser == tuser.doctor)
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


