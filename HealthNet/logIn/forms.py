from django import forms
from User.models import *


class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        #from User class
        UserName = forms.CharField()
        Password = forms.CharField()
        # from patient class
        insuranceNum = forms.CharField() # TODO: Check valid
        fields = ['UserName', 'Password', 'insuranceNum']
