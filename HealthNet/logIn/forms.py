from django import forms
from User.models import *


class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        #from User class
        UserName = forms.CharField()
        Password = forms.CharField()
        firstName = forms.CharField()
        lastName = forms.CharField()
        # from patient class
        insuranceNum = forms.CharField() # TODO: Check valid
        address = forms.CharField()
        email = forms.CharField() # TODO: check valid
        phone = forms.CharField()
        fields = ['UserName', 'Password', 'firstName', 'lastName', 'insuranceNum', 'address', 'email', 'phone']
