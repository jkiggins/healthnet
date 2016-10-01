from django import forms
from Calendar.models import Event


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        patient = forms.ModelForm()
        doctor = forms.ModelForm()
        hosptial = forms.ModelForm()
        startTime = forms.TimeField
        endTime = forms.TimeField
        fields = ['patient', 'doctor', 'hospital', 'startTime', 'endTime']
