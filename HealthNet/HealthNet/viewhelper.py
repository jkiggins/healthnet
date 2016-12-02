from HealthNet.formvalid import *
from user.models import *
from django import forms
from django.shortcuts import get_object_or_404
from django.http import Http404, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.views.generic import View
from user.forms import *

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


def getHealthUser(user):
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
        return getHealthUser(request.user)
    return None

def unauth(request):
    return HttpResponseRedirect(reverse('user:dashboard'))


def add_dict_to_model(dict, model):
    for key in dict:
        if hasattr(model, key):
            setattr(model, key, dict[key])


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
        if dict_has_keys(['doctor'], post):
            return EditProfileForm_medical(post)
        elif dict_has_keys(['first_name'], post):
            return EditProfileForm_basic(post)
        elif dict_has_keys(['user'], post):
            return EditProfileForm_emergency(post)

    @staticmethod
    def getContextWithPopulatedForm(post):
        ret = {'form_medical': EditProfileForm_medical(), 'form_emergency': EditProfileForm_emergency(), 'form_basic': EditProfileForm_basic()}

        if dict_has_keys(['doctor'], post):
            ret['form_medical'] = EditProfileForm_medical(post)
        elif dict_has_keys(['first_name'], post):
            ret['form_basic'] = EditProfileForm_basic(post)
        elif dict_has_keys(['user'], post):
            ret['form_emergency'] = EditProfileForm_emergency(post)

        return ret


    @staticmethod
    def getContextFromForm(form):
        ctx = {}
        if 'doctor' in form.fields:
            ctx['form_medical']=form
        elif 'user' in form.fields:
            ctx['form_emergency']=form
        elif 'first_name' in form.fields:
            ctx['form_basic']=form

        return ctx

    @staticmethod
    def updateUserProfile(form, user):
        if 'doctor' in form.fields:
            user.hospital = form.cleaned_data['hospital']
            user.doctor = form.cleaned_data['doctor']
            user.save()
        elif 'user' in form.fields:
            contact = None
            if user.contact is None:
                contact = Contact(full_name="filler", phone="filler")
                contact.save()
            else:
                contact = user.contact

            if form.cleaned_data['user'] is None:
                contact.full_name = form.cleaned_data['full_name']
                contact.phone = form.cleaned_data['emphone']
            else:
                contact.user = form.cleaned_data['user']
                contact.updateFromUser()

            contact.save()
            user.contact = contact
            user.save()
        elif 'first_name' in form.fields:
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

    if isinstance(model, Nurse):
        return [{'type': 'Nurse'}, {'url': reverse('user:vProfile', args=(model.user.id,)), 'label': model.user.get_full_name()}]

    if isinstance(model, Patient):
        label = model.user.get_full_name()
        if label == "":
            label = model.user.username
        return [{'type': 'Patient'},
                {'url': reverse('user:vProfile', args=(model.user.id,)), 'label': model.user.get_full_name()},
                {'url': reverse('emr:vemr', args=(model.id,)), 'label': "EMR"}]

    if isinstance(model, Doctor):
        return [{'type': 'Doctor'}, {'url': reverse('user:vProfile', args=(model.user.id,)), 'label': model.user.get_full_name()}]


def getResultsFromModelQuerySet(qset):
    results = []

    for q in qset:
        results.append(getResultFromModel(q))

    return results


def getTypeOfForm(request):
    remform = RemoveApproval(request.POST)
    appform = ApproveForm(request.POST)
    truform = TrustedNurses(request.POST)

    if remform.is_valid() or appform.is_valid():
        return 1
    elif truform.is_valid():
        return 2
    else:
        return 3


def try_parse(s):
    try:
        int(s)
        return True
    except ValueError:
        return False


def isAdmitted(patient):
    if patient.admittedHospital() is None:
        return False
    return True


class HealthView(View):
    """Generic View extension customized for healthnet
        Depending on the user type a different method is called
        setup and respond methods exists so no code is copied
    """
    POST = None

    def doctor(self, request, user):
        pass

    def nurse(self, request, user):
        pass

    def patient(self, request, user):
        pass

    def hosAdmin(self, request, user):
        pass

    def setup(self, request, user, **kwargs):
        pass

    def respond(self, request, user):
        pass

    def unauthorized(self, request, **kwargs):
        return HttpResponseRedirect(reverse('user:dashboard'))


    def get(self, request, **kwargs):
        pk = None
        user = get_user(request)

        if user is None:
            self.unauthorized(request, **kwargs);
        elif user.getType() in ['patient', 'doctor', 'nurse', 'hosAdmin']:
            self.setup(request, user, **kwargs)
            call = getattr(self, user.getType())
            if callable(call):
                return call(request, user)


    def post(self, request, **kwargs):
        self.POST=request.POST
        return self.get(request, **kwargs)


def getVisibleEMR(patient):
    """Returns a queryset of the EMR items that are released"""
    return patient.emritem_set.all().exclude(emrtest__released=False)

############ NOTIFICATION HELPERS ###############
def eventNotify(event):
    nbody = 'Starts at: {0} and lasts for: {1} minutes'.format(event.startTime, (event.endTime - event.startTime).minutes)
    if not (event.patient is None):
        Notification.push(event.patient, "New Appointment", nbody, 'vevent,{0}'.format(event.pk))
        Notification.push(event.doctor, "New Appointment", nbody, 'vevent,{0}'.format(event.pk))
    else:
        Notification.push(event.patient, "New Event", nbody, 'vevent,{0}'.format(event.pk))

def emrNotify(item):
    if isNote(item):
        Notification.push(item.patient, "New EMR Note", "", 'vemr,{0}'.format(item.patient.pk))
    elif isTest(item):
        Notification.push(item.patient, "New {0}".format(item.getTitle()), "", 'vemr,{0}'.format(item.patient.pk))
    elif isTest(item):
        Notification.push(item.patient, "New {0}".format(item.getTitle()), "", 'vemr,{0}'.format(item.patient.pk))


############# RESOLVE USER TYPE #################
def isPatient(user):
    return user.getType() == "patient"

def isDoctor(user):
    return user.getType() == "patient"

def isHosadmin(user):
    return user.getType() == "hosAdmin"

def isNurse(user):
    return user.getType() == "nurse"

########## REDIRECT HELPER METHODS #################
def toEmr(request, pk):
    return HttpResponseRedirect(reverse('emr:vemr', args=(pk,)))

def toLastPage(request):
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))



