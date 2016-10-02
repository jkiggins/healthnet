from django import forms
from User.models import *
from hospital.models import *
from django.utils import timezone
import datetime

class EventCreationFormPatient(forms.ModelForm):

    duration = forms.IntegerField(label="Duration (min)", initial=30)

    def save_with_hosptial(self, h, commit=True):
        m = super(EventCreationFormPatient, self).save(commit=False)

        m.endTime = m.startTime + datetime.timedelta(minutes=self.cleaned_data['duration'])
        m.hospital = h

        if commit:
            m.save()
        return m

    class Meta:
        model = Appointment
        # hospital = forms.ModelChoiceField(queryset=Hospital.objects.all())
        # startTime = forms.DateTimeField(initial=timezone.now, label="Start Time")
        # endTime = forms.DateTimeField(label="End Time (min)")
        # description = forms.CharField(max_length=200, label="Description")
        fields = ['description', 'startTime']
        exclude = ['hospital', 'endTime']


class EventCreationFormNurse(forms.ModelForm):
    doctor = forms.ModelChoiceField(queryset=Doctor.objects.all(), required=True)
    patient = forms.ModelChoiceField(queryset=Patient.objects.all(), empty_label="Not an Appointment")

    def save_with_hosptial(self, h, commit=True):
        m = super(EventCreationFormNurse, self).save(commit=False)

        if (self.cleaned_data['patient'] != self.patient.empty_label):
            m.appointment.save()
            self.cleaned_data['doctor'].Calendar.allEvents.add(m.appointment)
            self.cleaned_data['patient'].Calendar.allEvents.add(m.appointment)
            self.cleaned_data['doctor'].Calendar.save()
            self.cleaned_data['patient'].Calendar.save()

            return m.appointment

        if commit:
            m.save()
        return m

    class Meta:
        model = Event
        fields = ['startTime', 'endTime', 'description', 'hospital']
