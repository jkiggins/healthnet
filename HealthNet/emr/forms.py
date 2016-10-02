from django import forms
from django.utils import timezone
from emr.models import EMRVitals, EMRNote, EMRTrackedMetric

"""This is for making a new EMR vitals model"""
class EMRVitalsForm(forms.ModelForm):
    class Meta:
        model = EMRVitals
        dateCreated = forms.DateTimeField()
        restingBPM = forms.IntegerField()
        bloodPressure = forms.CharField()
        height = forms.FloatField()
        weight = forms.FloatField()
        comments = forms.CharField()
        fields = ['dateCreated', 'restingBPM', 'bloodPressure', 'height', 'weight', 'comments']