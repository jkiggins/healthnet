from .formvalid import *
from .models import *
from .forms import *
from django.shortcuts import get_object_or_404
from django.http import Http404

def augmentEventCreationFormForUpdate(form, augment=None):
    form.fields['delete'] = forms.BooleanField(label="Delete?", initial=False, widget=forms.CheckboxInput(), required=False)

    if not(augment is None):
        augment(form)

def disableAllFields(form):
    for key in form.fields:
        form.fields[key].disabled=True

def deleteInPostIsTrue(post):
    if 'delete' in post:
        if post['delete']:
            return True
    return False

def get_visible_event_or_404(pk):
    event = get_object_or_404(Event, pk=pk)
    if event.visible:
        return event
    raise Http404()



def getVisibleEvents(user):
    return user.event_set.all().filter(visible=True)


def dict_from_url_kvp(kvp):
    kvp_arr = kvp.split('/')

    dict = {}

    for i in range(0, len(kvp_arr)-1, 2):
        dict[kvp_arr[i]] = int(kvp_arr[i+1])

    return dict

def healthUserFromDjangoUser(user):
    if hasattr(user, 'patient'):
        return user.patient
    elif hasattr(user, 'doctor'):
        return user.doctor
    elif hasattr(user, 'nurse'):
        return user.nurse
    elif hasattr(user, 'hospitaladmin'):
        return user.hospitaladmin

def get_user(request):
    if (request.user.is_authenticated()):
        return healthUserFromDjangoUser(request.user)
    return None



def add_dict_to_model(dict, event):
    for key in dict:
        setattr(event, key, dict[key])


def elevate_if_trusted(form, user):
    if user.getType() == 'nurse':
        if not (form.cleaned_data['doctor'] is None):
            if user in form.cleaned_data['doctor'].nurses.all():
                form.elevate_permissions()


def elevate_if_trusted_event(form, user, event):
    if (user.getType() == 'nurse') and (user in event.doctor.nurses.all()):
        form.elevate_permissions()
        augmentEventCreationFormForUpdate(form)

    elif (user.getType() == 'doctor'):
        augmentEventCreationFormForUpdate(form)


def setEventFormFromModel(form, model):
    for key in form.fields:
        if hasattr(model, key):
            if key in ['doctor', 'patient', 'hospital']:
                form.fields[key].initial = getattr(model, key).pk
            else:
                form.fields[key].initial = getattr(model, key)

    form.duration = model.endTime - model.startTime

    return form


def updateEventFromModel(old_event, new_event):
    for key in old_event.__dict__:
        if hasattr(new_event, key) and not(getattr(new_event, key) is None):
            setattr(old_event, key, getattr(new_event, key))



def addEventConflictMessages(event_form, event):
    conflicts = event.conflicts()

    if conflicts == 0:
        return True
    elif conflicts == 1:
        EventCreationFormValidator.add_messages(event_form,
                                                {'duration': "Duration is too long and extends into another event"},
                                                {'startTime': "Alternatively Move Start Time back"})
    elif conflicts == 2:
        EventCreationFormValidator.add_messages(event_form, {'startTime': "Start Time is During another event"},
                                                {'startTime': "Remember a buffer of " + str(
                                                    Event.APP_BUFFER.seconds / 60) + " Minuets is required between Appointments"})

    return False


