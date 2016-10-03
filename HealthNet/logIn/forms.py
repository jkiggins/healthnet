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

    def is_valid(self):
        valid = super(RegistrationForm, self).is_valid()
        if not valid:
            return valid

        return self.cleaned_data['password1'] == self.cleaned_data['password2']


class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        # from patient class
        insuranceNum = forms.CharField() # TODO: Check valid
        fields = ['insuranceNum']


class LoginForm(forms.Form):
    username = forms.CharField(max_length=30, required=True, label="Username")
    password = forms.CharField(widget=forms.PasswordInput(attrs=dict(required=True, max_length=30, render_value=False)), label="Password")



