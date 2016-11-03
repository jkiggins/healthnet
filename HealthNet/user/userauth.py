def getAttrIfExists(obj, attr):
    if hasattr(obj, attr):
        return getattr(obj, attr)
    return None

def nurseIsTrusted(nurse, doctor):
    return (nurse in doctor.nurses.all())


def can_viewedit(user, event, utype):
    auth = False
    auth |= user == event.patient
    auth |= user == event.doctor

    if utype in ['nurse', 'hadmin']:
        auth |= event.hospital == user.hospital

        if utype == 'hadmin':
            auth |= (user.hospital in event.doctor.hospitals.all())

    if utype != 'hadmin':
        auth &= event.visible

    return auth


def userCan_Event(user, event, *actions):

    auth = True
    utype = user.getType()

    perm_map = {'viewedit': can_viewedit}

    for action in actions:
        if action in perm_map:
            auth &= perm_map[action](user, event, utype)
        else:
            raise NotImplementedError("This permission isn't implimented")

    return auth


    # def can_view(user, event, utype):
    #    return (event.patient == user) \
    #                 or (utype == 'nurse' and event.hospital == user.hospital) \
    #                 or (event.doctor == user)





