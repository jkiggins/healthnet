from django import forms
from User.models import *
from django.contrib.auth.models import User



class RegistrationForm(forms.Form):

    username = forms.CharField(max_length=30)
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)
    email = forms.EmailField(widget=forms.TextInput(attrs=dict(required=True, max_length=30)), label="Email address")
    password1 = forms.CharField(widget=forms.PasswordInput(attrs=dict(required=True, max_length=30, render_value=False)), label="Password")
    password2 = forms.CharField(widget=forms.PasswordInput(attrs=dict(required=True, max_length=30, render_value=False)), label="Password (again)")


class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        # from patient class
        insuranceNum = forms.CharField() # TODO: Check valid
        fields = ['insuranceNum']

