# Notification Signals
from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver
from user.models import *



# Event Signals
@receiver(pre_save, sender=Event)
def eventPreSave(sender, instance, *args, **kwargs):
    eventNotify(instance, instance.pk is None)



def eventNotify(event, new):
    nbody = 'Starts at: {0} and lasts for: {1} minutes'.format(event.startTime, (event.endTime - event.startTime).minutes)

    if not (event.patient is None):
        title = "Appointment Updated"
        if new:
            title = "New Appointment"
        Notification.push(event.patient, title, nbody, 'vevent,{0}'.format(event.pk))
        Notification.push(event.doctor, "New Appointment", nbody, 'vevent,{0}'.format(event.pk))
    else:
        title = "Event Updated"
        if new:
            title = "New Event"
        Notification.push(event.patient, "New Event", nbody, 'vevent,{0}'.format(event.pk))