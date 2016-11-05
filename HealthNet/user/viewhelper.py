from .formvalid import *
from .models import *
from .forms import *
from django.shortcuts import get_object_or_404
from django.http import Http404
from django.core.urlresolvers import reverse

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
            if (key in ['doctor', 'patient', 'hospital']) and not (getattr(model, key) is None):
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

class EditProfileHelper:
    @staticmethod
    def getFormByPostData(post):
        print(post)
        if dict_has_keys(['medical'], post):
            return EditProfileForm_medical(post)
        elif dict_has_keys(['basic'], post):
            return EditProfileForm_basic(post)
        elif dict_has_keys(['emergency'], post):
            return EditProfileForm_emergency(post)

    @staticmethod
    def getContextFromForm(form):
        ctx = {}
        if 'medical' in form.fields:
            ctx['form_medical']=form
        elif 'emergency' in form.fields:
            ctx['form_emergency']=form
        elif 'basic' in form.fields:
            ctx['form_basic']=form

        return ctx

    @staticmethod
    def updateUserProfile(form, user):
        if 'medical' in form.fields:
            user.hospital = form.cleaned_data['hospital']
            user.doctor = form.cleaned_data['doctor']
            user.save()
        elif 'emergency' in form.fields:
            contact = None
            if user.contact is None:
                contact = Contact(full_name="filler", phone="filler")
                contact.save()
                user.contact = contact
                user.save()
            else:
                contact = user.contact

            if form.cleaned_data['user'] is None:
                contact.full_name = form.cleaned_data['full_name']
                contact.phone = form.cleaned_data['phone']
            else:
                contact.user = form.cleaned_data['user']
                contact.updateFromUser()

            contact.save()

        elif 'basic' in form.fields:
            for key in form.cleaned_data:
                if not(form.cleaned_data[key] is None):
                    if hasattr(user, key):
                        setattr(user, key, form.cleaned_data[key])
                    elif hasattr(user.user, key):
                        setattr(user.user, key, form.cleaned_data[key])

            user.user.save()
            user.save()


def getResultFromModel(model):
    if isinstance(model, Event):
        return [{'type': 'Event'},{'url': reverse('user:vEvent', args=(model.id,)), 'label': model.title},
                {'url': reverse('user:eEvent', args=(model.id,)), 'label': "edit"}]

    if isinstance(model, Patient):
        return [{'type': 'patient'},
                {'url': reverse('user:vProfile', args=(model.user.id,)), 'label': model.user.get_full_name()},
                {'url': reverse('emr:index', args=(model.user.id,)), 'label': "EMR"}]

    if isinstance(model, Doctor):
        return [{'type': 'Doctor'}, {'url': reverse('user:vProfile', args=(model.user.id,)), 'label': model.user.get_full_name()}]


def getResultsFromModelQuerySet(qset):
    results = []

    for q in qset:
        results.append(getResultFromModel(q))

    return results
