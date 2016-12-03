from django import forms
from .models import *
import logging

from django import forms
from django.contrib.admin import widgets

from HealthNet.formvalid import *
from emr.models import *
from .models import *

# Get an instance of a logger
logger = logging.getLogger(__name__)

def get_dthtml(dt):
    return'{0}-{1:02d}-{2:02d}T{3:02d}:{4:02d}'.format(dt.year, dt.month, dt.day,
                                                               dt.hour, dt.minute)


def getEventFormByUserType(type, **kwargs):
    if type == "patient":
        obj = EventCreationFormPatient
    elif type == "doctor":
        obj = EventCreationFormDoctor
    elif type == 'nurse':
        obj = EventCreationFormNurse
    elif type == 'hosAdmin':
        obj = EventCreationFormHadmin

    if not('mode' in kwargs):
        kwargs['mode'] = 'create'


    return obj(**kwargs)


def doctor_nurse_shared_validation(event_form):
    valid = True

    #TODO: Clerify
    # hours = 1
    # valid &= EventCreationFormValidator.startDateInXhoursFuture(event_form, hours, {
    #     'startTime': "Start Time must be at least "+ str(hours) +" hours in the future"}, {})

    if event_form.mode == 'create':
        valid &= EventCreationFormValidator.eventValidateRequestTimeingOffset(event_form, 2, 0, {'startTime': "Events cannot start in the past"}, {})

    valid &= EventCreationFormValidator.eventPositiveDuration(event_form, datetime.timedelta(minutes=15),
                                                             {'duration': "Duration must be at least 15 minutes"},
                                                             {})
    return valid


class EventForm(forms.ModelForm):
    startTime = forms.SplitDateTimeField(widget=forms.SplitDateTimeWidget(attrs={'id': "dateTimeId"}), initial=timezone.now()+datetime.timedelta(days=1, minutes=30),
                                         label="Start", input_time_formats=['%H:%M', '%I:%M%p', '%I:%M %p', '%H:%M:%S'])
    duration = forms.DurationField(initial=datetime.timedelta(minutes=30), label="Duration")
    description = forms.CharField(widget=forms.Textarea(), label="Description/Comments", required=False)

    mode='create'

    def __init__(self, *args, **kwargs):

        if 'mode' in kwargs:
            self.mode = kwargs['mode']
            kwargs.pop('mode')

        super(EventForm, self).__init__(*args, **kwargs)


    def setStart(self, d):
        self.fields['startTime'].initial = d



    def getModel(self):
        m = self.save(commit=False)
        m.endTime = m.startTime + self.cleaned_data['duration']

        return m


class EventCreationFormPatient(EventForm):

    def __init__(self, *args, **kwargs):
        super(EventCreationFormPatient, self).__init__(*args, **kwargs)
        self.fields['duration'].disabled=True

        self.order_fields(['startTime', 'duration', 'description']) # Change Field order so they are displayed properly

    def getModel(self):
        m = super(EventCreationFormPatient, self).getModel()
        m.appointment = True

        return m


    def is_valid(self):
        valid = super(EventCreationFormPatient, self).is_valid()
        if not valid:
            return valid

        if self.mode == 'create':
            valid &= EventCreationFormValidator.startDateInXhoursFuture(self, 24, {'startTime': "Start Time must be atleast 24 hours in the future"}, {})

        return valid

    class Meta:
        model = Event
        fields = ['startTime', 'description']


class EventCreationFormDoctor(EventForm):

    def __init__(self, *args, **kwargs):
        super(EventCreationFormDoctor, self).__init__(*args, **kwargs)
        self.order_fields(['type', 'patient', 'hospital', 'startTime', 'duration', 'description'])
        self.fields['patient'].widget.attrs = {'onchange': "resolve_pd_dependancy(this)", 'data-key': "patient"}
        self.fields['hospital'].widget.attrs = {'onchange': "resolve_pd_dependancy(this)", 'data-key': "hospital"}

    def getModel(self):
        m = super(EventCreationFormDoctor, self).getModel()
        m.appointment = not(self.fields['patient'] is None)

        return m


    def is_valid(self):
        valid = super(EventCreationFormDoctor, self).is_valid()
        if not valid:
            return valid


        valid &= doctor_nurse_shared_validation(self)
        valid &= EventCreationFormValidator.patientMatchesHospitalDoctor(self,
                                                                   {'hospital': "The patient isn't at that hospital"},
                                                                   {})

        return valid


    def dependantFields(self, pqset, hqset):
        if ('patient' in self.cleaned_data) and ('hospital' in self.cleaned_data):
            if (self.cleaned_data['patient'] is None) and (self.cleaned_data['hospital'] is None):
                self.fields['patient'].queryset = pqset
                self.fields['hospital'].queryset = hqset
            elif not (self.cleaned_data['patient'] is None):
                # TODO: add code to set defualt value of dropdown to the hospital
                self.fields['hospital'].queryset = Hospital.objects.filter(pk=self.cleaned_data['patient'].hospital.pk)
            elif not (self.cleaned_data['hospital'] is None):
                patients = pqset.filter(hospital=self.cleaned_data['hospital'])
                self.fields['patient'].queryset = patients
                self.fields['hospital'].queryset = hqset


    def set_hospital_patient_queryset(self, hqset, pqset):
        self.fields['hospital'].queryset = hqset
        self.fields['patient'].queryset = pqset
        self.fields['hospital'].required = False
        self.fields['patient'].required = False


    class Meta:
        model = Event
        fields = ["patient", "hospital", "startTime", "description"]


class EventCreationFormNurse(EventForm):

    def __init__(self, *args, **kwargs):
        super(EventCreationFormNurse, self).__init__(*args, **kwargs)
        self.elevated = False
        self.fields['patient'].widget.attrs = {'onchange': "resolve_pd_dependancy(this)"}
        self.fields['doctor'].widget.attrs = {'onchange': "resolve_pd_dependancy(this)"}
        self.fields['patient'].required = False
        self.fields['doctor'].required = False


    def dependantFields(self, dqset, pqset, hospital):
        if ('patient' in self.cleaned_data) and ('doctor' in self.cleaned_data):
            if (self.cleaned_data['patient'] is None) and (self.cleaned_data['doctor'] is None):
                self.fields['patient'].queryset = pqset
                self.fields['doctor'].queryset = dqset
            elif not (self.cleaned_data['patient'] is None):
                # TODO: add code to set defualt value of dropdown to the doctor
                self.fields['doctor'].queryset = Doctor.objects.filter(pk=self.cleaned_data['patient'].doctor.pk)
            elif not (self.cleaned_data['doctor'] is None):
                patients = self.cleaned_data['doctor'].patient_set.filter(hospital=hospital, accepted=True)
                self.fields['patient'].queryset = patients


    def getModel(self):
        m = super(EventCreationFormNurse, self).getModel()
        m.appointment = not(self.fields['patient'] is None)

        return m


    def is_valid(self):
        valid = super(EventCreationFormNurse, self).is_valid()
        if not valid:
            return valid

        valid &= doctor_nurse_shared_validation(self)
        if not self.elevated:
            valid &= EventCreationFormValidator.eventIsAppointment(self, {'patient': "This field is required"}, {})

        return valid


    def set_patient_doctor_queryset(self, patient_qset, doctor_qset):
        self.fields['patient'].queryset = patient_qset
        self.fields['doctor'].queryset = doctor_qset


    def elevate_permissions(self):
        self.elivated = True

    class Meta:
        model = Event
        fields = ["patient", "doctor", "startTime", "description"]


class EventCreationFormHadmin(EventForm):
    type = forms.ChoiceField(widget=forms.RadioSelect, choices=(('1', 'Generic'), ('2', 'Appointment')))

    def set_patient_doctor_queryset(self, patient_qset, doctor_qset):
        self.fields['patient'].queryset = patient_qset
        self.fields['doctor'].queryset = doctor_qset
        self.fields['patient'].required = False
        self.fields['doctor'].required = False
        self.fields['patient'].widget.attrs = {'onchange': "resolve_pd_dependancy(this)"}
        self.fields['doctor'].widget.attrs = {'onchange': "resolve_pd_dependancy(this)"}

    class Meta:
        model = Event
        fields = ["patient", "doctor", "startTime", "description"]


class EditProfileForm(forms.Form):
    first_name = forms.CharField(max_length=20, required=False)
    last_name = forms.CharField(max_length=20, required=False)
    email = forms.CharField(max_length=50, required=False)
    phone = forms.CharField(max_length=10, label="Phone Number", required=False)
    address = forms.CharField(max_length=50, label="Your Address", required=False)

    doctor = forms.ModelChoiceField(queryset=Doctor.objects.all(), required=False)
    hospital = forms.ModelChoiceField(queryset=Hospital.objects.all(), required=False)

    emuser = forms.ModelChoiceField(queryset=User.objects.all(), required=False)
    full_name = forms.CharField(max_length=50, required=False)
    emphone = forms.CharField(max_length=10, label="Phone Number", required=False)

    def filterUserQuerySet(self, user):
        self.fields['emuser'].queryset = User.objects.all().exclude(pk = user.pk)

    def is_valid(self):
        self.fields['doctor'].required = True
        self.fields['hospital'].required = True
        valid = super(EditProfileForm, self).is_valid()
        if not valid:
            return valid

        if self.cleaned_data['emuser'] is None:
            valid &= not((self.cleaned_data['full_name'] is None) or (self.cleaned_data['phone'] is None))
            if not valid:
                EventCreationFormValidator.add_messages(self, {'full_name': "Field Required", 'phone': "Field Required"}, {'user': "alternativly select a user from the system"})

        return valid

    def __init__(self, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.fields['doctor'].widget.attrs = {'onchange': "resolve_pd_dependancy(this)"}
        self.fields['hospital'].widget.attrs = {'onchange': "resolve_pd_dependancy(this)"}


class HosAdminSearchForm(forms.Form):
    keywords = forms.CharField(max_length=50, label="Keywords", required=False)
    choices = (('event', 'Events'), ('patient', 'Patients'), ('doctor', 'Doctors'), ('nurse', 'Nurses'), ('pending', 'Pending Staff'))
    filterBy = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple(), choices=choices, required=False, label="")


class SearchForm(forms.Form):
    keywords = forms.CharField(max_length=50, label="Keywords", required=False)
    choices = (('event', 'Events'), ('patient', 'Patients'), ('doctor', 'Doctors'))
    filterBy = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple(), choices=choices, required=False, label="")

    def setSearchForm(self, utype):
        if utype == 'doctor':
            choices = (
                ('event', 'Events'),
                ('patient', 'Patients'),
                ('doctor', 'Doctors'),
                ('mpatient', 'My Patients')
            )


class ApproveForm(forms.Form):
    approved = forms.BooleanField(label="Approved")


class RemoveApproval(forms.Form):
    remove = forms.BooleanField(label="Remove From Hospital")


class TrustedNurses(forms.Form):
    docs = forms.ModelChoiceField(queryset=Doctor.objects.none(), label="Doctors")

    def setQuerySet(self , qset):
        self.fields['docs'].queryset = qset


class EditProfileHelper:
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