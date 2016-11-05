from django import forms
from .models import EMRVitals

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
        fields = ['restingBPM', 'bloodPressure', 'height', 'weight']