from .viewhelper import *


def emrNotify(user, item, new):
    if isNote(item):
        link = 'vemr,{0}'.format(item.patient.pk)
        if new:
            Notification.push(item.patient.user, "Note added to your EMR", "", link)
        else:
            Notification.push(item.patient.user, "A note in your EMR was updated", "", link)
    elif isTest(item):
        link = 'vemr,{0}'.format(item.patient.pk)
        if new:
            Notification.push(item.patient.user, "A {0} was added to your emr".format(item.getTitle()), "", link)
        else:
            Notification.push(item.patient.user, "A {0} was updated in your emr".format(item.getTitle()), "", link)

        if not item.released:
            Notification.push(item.patient.doctor.user, "Test Results for {0} require your approval".format(item.patient.user.get_full_name()), "", link)

    elif isVital(item):
        Notification.push(item.patient.user, "Your {0}'s have been updated in the emr".format(item.getTitle()), "", 'vemr,{0}'.format(item.patient.pk))
        Notification.push(item.patient.doctor.user, "New {0}'s your patient, {1}".format(item.getTitle(), item.patient.user.get_full_name()), "", 'vemr,{0}'.format(item.patient.pk))


    elif isAdmit(item):
        status = ""
        status = "Discharged From"
        if item.admit:
            status = "Admitted to"

        Notification.push(item.patient.doctor.user, "Your patient {0}, has been {1} {2}".format(item.getTitle(), status, item.hospital), "", 'vemr,{0}'.format(item.patient.pk))

    elif isPrescription(item):
        med = "Medication: {0}".format(item.medication)
        Notification.push(item.emritem.patient.user, "You have a new {0} from DR {1}".format(item.getTitle(), item.provider.user.get_full_name()), med,
                          'vemr,{0}'.format(item.patient.pk))

        if item.provider != item.patient.doctor:
            Notification.push(item.patient.user, "{0} has written a prescription for you Patient {1}".format(item.provider.user.get_full_name(), item.emritem.patient),
                              med,
                              'vemr,{0}'.format(item.patient.pk))