from django import forms
from .models import *
from hospital.models import *
from django.utils import timezone
from syslogging.models import *
import datetime
import logging
from emr.models import *
from django.contrib.admin import widgets
from .formvalid import *


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
    startTime = forms.SplitDateTimeField(widget=widgets.AdminSplitDateTime(), initial=timezone.now()+datetime.timedelta(days=1, minutes=30),
                                         label="Start Time")
    duration = forms.DurationField(initial=datetime.timedelta(minutes=30), label="Duration")
    description = forms.CharField(widget=forms.Textarea(), label="Description/Comments", required=False)

    def __init__(self, *args, **kwargs):

        if 'mode' in kwargs:
            self.mode = kwargs['mode']
            kwargs.pop('mode')

        super(EventForm, self).__init__(*args, **kwargs)




    def getModel(self):
        m = self.save(commit=False)
        m.endTime = m.startTime + self.cleaned_data['duration']

        return m


class EventCreationFormPatient(EventForm):

    def __init__(self, *args, **kwargs):
        super(EventCreationFormPatient, self).__init__(*args, **kwargs)
        self.order_fields(['startTime', 'duration', 'endTime', 'description']) # Change Field order so they are displayed properly

    def getModel(self):
        m = super(EventCreationFormPatient, self).getModel()
        m.appointment = True

        return m


    def is_valid(self):
        valid = super(EventCreationFormPatient, self).is_valid()
        if not valid:
            return valid

        valid &= EventCreationFormValidator.eventDurationBounded(self, 15, 30, {'duration': "Duration must be between 15 and 30 minutes"},{})

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
        self.fields['patient'].widget.attrs = {'onchange': "resolve_dependancy(this)"}
        self.fields['hospital'].widget.attrs = {'onchange': "resolve_dependancy(this)"}

    def getModel(self):
        m = super(EventCreationFormDoctor, self).getModel()
        m.appointment = not(self.fields['patient'] is None)

        return m


    def is_valid(self):
        valid = super(EventCreationFormDoctor, self).is_valid()
        if not valid:
            return valid

        print(self.mode)
        valid &= doctor_nurse_shared_validation(self)
        valid &= EventCreationFormValidator.patientMatchesHospital(self,
                                                                   {'hospital': "The patient isn't at that hospital"},
                                                                   {})

        return valid


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
        self.fields['patient'].widget.attrs = {'onchange': "resolve_dependancy(this)"}
        self.fields['doctor'].widget.attrs = {'onchange': "resolve_dependancy(this)"}
        self.fields['patient'].required = False
        self.fields['doctor'].required = False


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
        self.fields['patient'].widget.attrs = {'onchange': "resolve_dependancy(this)"}
        self.fields['doctor'].widget.attrs = {'onchange': "resolve_dependancy(this)"}

    class Meta:
        model = Event
        fields = ["patient", "doctor", "startTime", "description"]


class EditProfileForm(forms.Form):
    first_name = forms.CharField(max_length=20, required=False)
    last_name = forms.CharField(max_length=20, required=False)
    email = forms.CharField(max_length=50, required=False)
    doctor = forms.ModelChoiceField(queryset=Doctor.objects.all(), required=False)
    phone = forms.CharField(max_length=10, label="Phone Number", required=False)
    address = forms.CharField(max_length=50, label="Your Address", required=False)
    emergency = forms.CharField(max_length=10, label="Emergency", required=False)

    height = forms.IntegerField(label="Height in Inches", initial=0, required=False)
    weight = forms.IntegerField(label="Weight in Lbs", initial=0,required=False)
    age = forms.IntegerField(label="Age in Years", initial=0,required=False)
    restingBpm = forms.IntegerField(label="Usual Resting BPM",initial=0, required=False)
    bloodPressure = forms.CharField(max_length=20, initial=0, label="Blood pressure (###/###)", required=False)
    comments = forms.CharField(label="Comments", widget=forms.Textarea(), required=False)

    def save(self, commit=True):
        pass

    def set_defaults(self, user):
        self.fields['first_name'].initial = user.user.first_name
        self.fields['last_name'].initial = user.user.last_name
        self.fields['email'].initial = user.user.email

        if(user.doctor != None):
            self.fields['doctor'].initial = user.doctor
            self.fields['doctor'].disabled=True

        self.fields['phone'].initial = user.phone
        self.fields['address'].initial = user.address

        if(user.emr.emergency != None):
            self.fields['emergency'].initial = user.emr.emergency


    def save_user(self, m):
        m.user.first_name = self.cleaned_data['first_name']
        m.user.last_name = self.cleaned_data['last_name']
        m.user.email = self.cleaned_data['email']

        if m.doctor == None:
            m.doctor = self.cleaned_data['doctor']

        m.address = self.cleaned_data['address']
        m.phone = self.cleaned_data['phone']
        m.emr.emergency = self.cleaned_data['emergency']
        m.emr.save()
        m.user.save()
        m.save()

        emrItem = EMRVitals.objects.create(emr = m.emr,
                                           height=self.cleaned_data['height'],
                                           weight=self.cleaned_data['weight'],
                                           age=self.cleaned_data['age'],
                                           bloodPressure=self.cleaned_data['bloodPressure'],
                                           restingBPM=self.cleaned_data['restingBpm'],
                                           comments=self.cleaned_data['comments']
        )

