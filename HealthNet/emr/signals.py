# Notification Signals
from django.db.models.signals import post_delete, pre_save, post_save
from django.dispatch import receiver
from user.models import Notification

from emr.models import *

@receiver(post_delete, sender=EMRItem)
def notePostSave(sender, instance, *args, **kwargs):
    new = 'emritem_ptr' in instance.changed_fields
    emritem = instance.emritem
    patient = emritem.patient

    link = 'vemri,{0}'.format(instance.pk)
    if new:
        Notification.push(patient.user, "Note added to your EMR", "", link)
    else:
        Notification.push(patient.user, "A note in your EMR was updated", "", link)

@receiver(post_save, sender=EMRVitals)
def vitalsPostSave(sender, instance, *args, **kwargs):
    new = 'emritem_ptr' in instance.changed_fields
    emritem = instance.emritem
    patient = emritem.patient

    Notification.push(patient.user, "Your {0}'s have been updated in the emr".format(instance.getTitle()), "",
                      'vemri,{0}'.format(instance.pk))
    Notification.push(patient.doctor.user,
                      "New {0}'s your patient, {1}".format(instance.getTitle(), patient.user.get_full_name()), "",
                      'vemri,{0}'.format(instance.pk))


@receiver(post_save, sender=EMRPrescription)
def prescriptionPostSave(sender, instance, *args, **kwargs):
    new = 'emritem_ptr' in instance.changed_fields
    emritem = instance.emritem
    patient = emritem.patient

    med = "Medication: {0}".format(instance.medication)
    Notification.push(instance.emrpatient.user,
                      "You have a new {0} from DR {1}".format(instance.getTitle(),instance.provider.user.get_full_name()), med,
                      'vemri,{0}'.format(instance.pk))

    if instance.provider != patient.doctor:
        Notification.push(patient.user, "{0} has written a prescription for you Patient {1}".format(
           instance.provider.user.get_full_name(),instance.emrpatient),
                          med,
                          'vemri,{0}'.format(instance.pk))


@receiver(post_save, sender=EMRAdmitStatus)
def emradmitPostSave(sender, instance, *args, **kwargs):
    new = 'emritem_ptr' in instance.changed_fields
    emritem = instance.emritem
    patient = emritem.patient

    status = ""
    status = "Discharged From"
    if instance.admit:
        status = "Admitted to"

    Notification.push(patient.doctor.user,
                      "Your patient {0}, has been {1} {2}".format(instance.getTitle(), status, instance.hospital), "",
                      'vemri,{0}'.format(instance.pk))



@receiver(post_save, sender=EMRTest)
def emrtestPostSave(sender, instance, *args, **kwargs):
    new = 'emritem_ptr' in instance.changed_fields
    emritem = instance.emritem
    patient = emritem.patient
    
    link = 'vemri,{0}'.format(instance.pk)
    if new:
        Notification.push(patient.user, "A {0} was added to your emr".format(instance.getTitle()), "", link)
    else:
        Notification.push(patient.user, "A {0} was updated in your emr".format(instance.getTitle()), "", link)

    if not instance.released:
        Notification.push(patient.doctor.user,
                          "Test Results for {0} require your approval".format(patient.user.get_full_name()), "", link)

@receiver(post_save, sender=EMRProfile)
def emrprofilePostSave(sender, instance, *args, **kwargs):
    Notification.push(instance.patient.user,
                      "Your Basic Medical Info has been updated", "",
                      'vemr,{0}'.format(instance.patient.pk))

    Notification.push(instance.patient.doctor.user,
                      "{0}'s Medical Info has been updated".format(instance.patient.user.get_full_name()), "",
                      'vemr,{0}'.format(instance.patient.pk))




