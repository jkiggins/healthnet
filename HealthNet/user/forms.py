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

def getEventFormByUserType(type, request = None):
    if type == "patient":
        if request != None:
            return EventCreationFormPatient(request.POST)

        return EventCreationFormPatient()

    elif type == "doctor":
        if request != None:
            return EventCreationFormDoctor(request.POST)

        return EventCreationFormDoctor()

    else:
        if request != None:
            return EventCreationFormNurse(request.POST)

        return EventCreationFormNurse()

def doctor_nurse_shared_validation(event_form):
    valid = True
    valid &= EventCreationFormValidator.startDateInXhoursFuture(event_form, 24, {
        'startTime': "Start Time must be at least 24 hours in the future"}, {})

    valid &= EventCreationFormValidator.eventPositiveDuration(event_form, 15,
                                                              {'endTime': "Event Must be atleast 15 minuets long"},
                                                              {'startTime': "Alternativley move the start time back"})
    valid &= EventCreationFormValidator.eventNotConflictingType(event_form, '2', {'type': "Type must be appointment"},
                                                                {'patient': "Alternativly, Don't select a patient"})
    return valid


class EventCreationFormPatient(forms.ModelForm):

    startTime = forms.SplitDateTimeField(widget=widgets.AdminSplitDateTime(), initial=timezone.now(),
                                         label="Start Time")
    duration = forms.IntegerField(initial=30, label="Duration (min)")
    description = forms.CharField(widget=forms.Textarea(), label="Description/Comments", required=False)

    def __init__(self, *args, **kwargs):
        super(EventCreationFormPatient, self).__init__(*args, **kwargs)
        self.order_fields(['startTime', 'duration', 'endTime', 'description']) # Change Field order so they are displayed properly


    def is_valid(self):
        valid = super(EventCreationFormDoctor, self).is_valid()
        if not valid:
            return valid

        valid &= EventCreationFormValidator.eventDurationBounded(self, 15, 30, {'duration': "Duration must be between 15 and 30 minutes"},{})
        valid &= EventCreationFormValidator.startDateInXhoursFuture(self, 24, {'startTime': "Start Time must be atleast 24 hours in the future"}, {})

        return valid

    def getModel(self):
        return self.save(commit=False)

    class Meta:
        model = Event
        fields = ['startTime', 'description']


class EventCreationFormDoctor(forms.ModelForm):

    type = forms.ChoiceField(widget=forms.RadioSelect, choices=(('1', 'Generic'), ('2', 'Appointment')))
    startTime = forms.SplitDateTimeField(widget=widgets.AdminSplitDateTime(), initial=timezone.now(),
                                         label="Start Time")
    endTime = forms.SplitDateTimeField(widget=widgets.AdminSplitDateTime,
                                       initial=timezone.now() + datetime.timedelta(minutes=30), label="End Time")
    patient = forms.ModelChoiceField(queryset=Patient.objects.all(), required=False)
    description = forms.CharField(widget=forms.Textarea(), label="Description/Comments", required=False)

    def __init__(self, *args, **kwargs):
        super(EventCreationFormDoctor, self).__init__(*args, **kwargs)
        self.order_fields(['type', 'patient', 'hospital', 'startTime', 'endTime', 'description'])

    def is_valid(self):
        valid = super(EventCreationFormDoctor, self).is_valid()
        if not valid:
            return valid

        valid &= doctor_nurse_time_validation(self)
        valid &= EventCreationFormValidator.patientMatchesHospital(self,
                                                                   {'hospital': "The patient isn't at that hospital"},
                                                                   {})



        return valid

    def set_hospital_patient_queryset(self, hqset, pqset):
        self.fields['hospital'].queryset = hqset
        self.fields['patient'].queryset = pqset

    def getModel(self):
        return self.save(commit=False)

    class Meta:
        model = Event
        fields = ["patient", "hospital", "startTime", "endTime", "description"]


class EventCreationFormNurse(forms.ModelForm):
    type = forms.ChoiceField(widget=forms.RadioSelect, choices=(('1', 'Generic'), ('2', 'Appointment')), disabled=True, required=False, initial='2')
    startTime = forms.SplitDateTimeField(widget=widgets.AdminSplitDateTime(), initial=timezone.now(),
                                         label="Start Time")
    endTime = forms.SplitDateTimeField(widget=widgets.AdminSplitDateTime,
                                       initial=timezone.now() + datetime.timedelta(minutes=30), label="End Time")
    description = forms.CharField(widget=forms.Textarea(), label="Description/Comments", required=False)

    def is_valid(self):
        valid = super(EventCreationFormNurse, self).is_valid()
        if not valid:
            return valid

        valid &= doctor_nurse_shared_validation(self)

        return valid

    def getModel(self):
        return self.save(commit=False)


    def set_patient_doctor_queryset(self, patient_qset, doctor_qset):
        self.fields['patient'].queryset = patient_qset
        self.fields['doctor'].queryset = doctor_qset
        self.elevated = True

    def elevate_to_trusted(self):
        self.fields['patient'].required = False

    class Meta:
        model = Event
        fields = ["patient", "doctor", "startTime", "endTime", "description"]


class EventUpdateForm(forms.ModelForm):

    delete = forms.BooleanField(label="Delete?", initial=False, required=False)

    startTime = forms.DateTimeField(widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}), label='Start Time',
                                    input_formats={'%Y-%m-%dT%H:%M'})

    endTime = forms.DateTimeField(widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}), label='End Time',
                                  input_formats={'%Y-%m-%dT%H:%M'})

    def save(self, commit=False):
        pass

    def set_defaults(self, event):
        self.fields['startTime'].initial = get_dthtml(event.startTime)
        self.fields['endTime'].initial = get_dthtml(event.endTime)
        self.fields['description'].initial = event.description

    def disable_delete(self):
        self.fields['delete'].disabled=True


    def save_with_event(self, old_event):

        if self.cleaned_data['delete']:
            old_event.delete()
            return True

        old_event.startTime = self.cleaned_data['startTime']
        old_event.endTime = self.cleaned_data['endTime']
        old_event.description = self.cleaned_data['description']

        if not validate_event(old_event):
            return False

        old_event.save()
        return True

    class Meta:
        model=Event
        fields = ['startTime', 'endTime', 'description']


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

