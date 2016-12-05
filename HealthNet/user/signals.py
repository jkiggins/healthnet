# Notification Signals
from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver
from user.models import *



# Event Signals
@receiver(pre_save, sender=Event)
def eventPreSave(sender, instance, *args, **kwargs):
    pass
    new = instance.pk is None

    nbody = 'Starts at: {0} and lasts for: {1} minutes'.format(instance.startTime, (instance.endTime - instance.startTime).seconds / 60)
    title = ""
    if not (instance.patient is None):
        title = "Appointment Updated"
        if new:
            title = "New Appointment"
        Notification.push(instance.patient.user, title, nbody, 'user:vEvent,{0}'.format(instance.pk))
    else:
        title = "Event Updated"
        if new:
            title = "New Event"

    Notification.push(instance.doctor.user, title, nbody, 'user:vEvent,{0}'.format(instance.pk))


@receiver(post_delete, sender=Event)
def eventPostDel(sender, instance, *args, **kwargs):
    nbody = 'Started at: {0} and lasted for: {1} minutes'.format(instance.startTime,
                                                               (instance.endTime - instance.startTime).seconds/60)
    type = "Appointment"
    if not instance.appointment:
        type = "Event"
    else:
        Notification.push(instance.patient.user, "Your {0} has been cancled".format(type), nbody, "")

    Notification.push(instance.doctor.user, "Your {0} has been cancled".format(type), nbody, "")
