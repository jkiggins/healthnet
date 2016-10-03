from django import forms
from User.models import *
from hospital.models import *
from django.utils import timezone
import datetime

import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)

class EventCreationFormPatient(forms.ModelForm):

    duration = forms.IntegerField(label="Duration (min)", initial=30)

    def save_with_hosptial(self, h, commit=True):
        m = super(EventCreationFormPatient, self).save(commit=False)

        m.appointment = True
        m.endTime = m.startTime + datetime.timedelta(minutes=self.cleaned_data['duration'])
        m.hospital = h

        if commit:
            m.save()
        return m

    class Meta:
        model = Event
        # hospital = forms.ModelChoiceField(queryset=Hospital.objects.all())
        # startTime = forms.DateTimeField(initial=timezone.now, label="Start Time")
        # endTime = forms.DateTimeField(label="End Time (min)")
        # description = forms.CharField(max_length=200, label="Description")
        fields = ['description', 'startTime']
        exclude = ['hospital', 'endTime']


class EventCreationFormNurse(forms.ModelForm):
    doctor = forms.ModelChoiceField(queryset=Doctor.objects.all(), required=True)
    patient = forms.ModelChoiceField(queryset=Patient.objects.all(), required=False, empty_label="Not an Appointment")

    def save_with_hosptial(self, h, commit=True):
        m = super(EventCreationFormNurse, self).save(commit=False)

        if (self.cleaned_data['patient'] != None):
            m.appointment = True
            m.save()
            p = Patient.objects.get(pk=self.cleaned_data['patient'])
            p.Calendar.allEvents.add(m)
            p.save()
        elif commit:
            m.save()

        return m

    class Meta:
        model = Event
        fields = ['startTime', 'endTime', 'description', 'hospital']


class EventCreationFormDoctor(forms.ModelForm):
    patient = forms.ModelChoiceField(queryset=Patient.objects.all(), empty_label="Not an Appointment", required=False)

    def save_with_doctor(self, doctor, commit=True):
        m = super(EventCreationFormDoctor, self).save(commit=False)

        if(self.cleaned_data['patient'] != None):
            m.appointment = True
            m.save()
            doctor.Calendar.allEvents.add(m)
            doctor.Calendar.save()
            self.cleaned_data['patient'].Calendar.allEvents.add(m)
            self.cleaned_data['patient'].Calendar.save()
        elif commit:
            m.save()
        return m

    class Meta:
        model=Event
        fields = ['startTime', 'endTime', 'description', 'hospital']
