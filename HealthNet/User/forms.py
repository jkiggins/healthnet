from django import forms
from User.models import *
from hospital.models import *
from django.utils import timezone
from syslogging.models import *
import datetime
import logging
from emr.models import *

# Get an instance of a logger
logger = logging.getLogger(__name__)


def validate_event(m):
    if (m.doctor.event_set.filter(startTime__lte=m.endTime).filter(startTime__gte=m.startTime).count() != 0) or (m.doctor.event_set.filter(endTime__lte=m.endTime).filter(endTime__gte=m.startTime).count() != 0):
        return False

    if m.appointment:
        if (m.patient.event_set.filter(startTime__lte=m.endTime).filter(startTime__gte=m.startTime).count() != 0) or (m.patient.event_set.filter(endTime__lte=m.endTime).filter(endTime__gte=m.startTime).count() != 0):
            return False

    return True

def get_dthtml(dt):
    return'{0}-{1:02d}-{2:02d}T{3:02d}:{4:02d}'.format(dt.year, dt.month, dt.day,
                                                               dt.hour, dt.minute)



"""This will create and update a user profile
class ProfileForm(forms.ModelForm):
    first_name = forms.CharField(initial="")
    last_name = forms.CharField(initial="")
    email = forms.EmailField()

    def save(self, commit=True):
        m=super(ProfileForm, self).save(commit=False)
        m.user.first_name = self.cleaned_data['first_name']
        m.user.last_name = self.cleaned_data['last_name']
        m.user.email = self.cleaned_data['email']
        m.user.save()
        m.save()

    class Meta:
        model = Patient
        #first_name = forms.CharField()
        #last_name = forms.CharField()
        #hospital = forms.ModelChoiceField()
        #doctor = forms.ModelChoiceField()
        address = forms.CharField()
        #email = forms.CharField()
        phone = forms.CharField()
        fields = ['address', 'phone']"""



class EventCreationFormPatient(forms.ModelForm):

    duration = forms.IntegerField(label="Duration (min)", initial=30)

    startTime = forms.DateTimeField(widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}), label='Start Time',
                                    initial=get_dthtml(timezone.now()), input_formats={'%Y-%m-%dT%H:%M'})

    def save_with_patient(self, p, commit=True):
        m = super(EventCreationFormPatient, self).save(commit=False)

        m.appointment = True
        m.endTime = m.startTime + datetime.timedelta(minutes=self.cleaned_data['duration'])
        m.hospital = p.hospital
        m.patient = p
        m.doctor = p.doctor
        m.patient = p

        if not validate_event(m):
            return False

        Syslog.createEvent(m, p)
        m.save()
        return True

    class Meta:
        model = Event
        fields = ['description', 'startTime']
        exclude = ['hospital', 'endTime']


class EventCreationFormNurse(forms.ModelForm):
    doctor = forms.ModelChoiceField(queryset=Doctor.objects.all(), required=False)
    patient = forms.ModelChoiceField(queryset=Patient.objects.all(), required=False, empty_label="Not an Appointment")

    startTime = forms.DateTimeField(widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}), label='Start Time',
                                    initial=get_dthtml(timezone.now()), input_formats={'%Y-%m-%dT%H:%M'})

    endTime = forms.DateTimeField(widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}), label='End Time',
                                  initial=get_dthtml(timezone.now()+datetime.timedelta(minutes=30)),
                                  input_formats={'%Y-%m-%dT%H:%M'})

    def save(self, commit=True):
        m = super(EventCreationFormNurse, self).save(commit=False)

        m.doctor = self.cleaned_data['doctor']
        m.hospital = self.cleaned_data['hospital']

        if (m.doctor.hospitals.all().filter(pk=m.hospital.id).count() == 0):
            return False

        if (self.cleaned_data['patient'] != None):
            if(m.doctor.hospitals.all().filter(pk=self.cleaned_data['patient'].hospital.id).count() == 0):
                return False
            m.appointment = True
            m.patient = self.cleaned_data['patient']

        if not validate_event(m):
            return False

        Syslog.createEvent(m, m.patient)
        m.save()
        return True

    class Meta:
        model = Event
        fields = ['startTime', 'endTime', 'description', 'hospital']


class EventCreationFormDoctor(forms.ModelForm):
    patient = forms.ModelChoiceField(queryset=Patient.objects.all(), empty_label="Not an Appointment", required=False)

    startTime = forms.DateTimeField(widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}), label='Start Time',
                                    initial=get_dthtml(timezone.now()), input_formats={'%Y-%m-%dT%H:%M'})

    endTime = forms.DateTimeField(widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}), label='End Time',
                                  initial=get_dthtml(timezone.now() + datetime.timedelta(minutes=30)),
                                  input_formats={'%Y-%m-%dT%H:%M'})

    def set_defaults(self, doct):
        self.fields['hospital'].queryset = doct.hospitals.all()

    def save_with_doctor(self, doctor, commit=True):
        m = super(EventCreationFormDoctor, self).save(commit=False)

        m.doctor = doctor

        if(self.cleaned_data['patient'] != None):
            m.appointment = True
            m.patient = self.cleaned_data['patient']
            m.doctor = doctor
            m.save()

        if not validate_event(m):
            return False

        Syslog.createEvent(m, doctor)
        m.save()
        return True

    class Meta:
        model=Event
        fields = ['startTime', 'endTime', 'description', 'hospital']


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

    height = forms.IntegerField(label="Height in Inches", required=False)
    weight = forms.IntegerField(label="Weight in Lbs", required=False)
    age = forms.IntegerField(label="Age in Years", required=False)
    restingBpm = forms.IntegerField(label="Usual Resting BPM", required=False)
    bloodPressure = forms.CharField(max_length=20, label="Blood pressure (###/###)", required=False)
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

