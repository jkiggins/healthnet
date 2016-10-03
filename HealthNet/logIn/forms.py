from django import forms
from User.models import *
import re
from django.contrib.auth.models import User



class RegistrationForm(forms.Form):

    username = forms.CharField(max_length=30, label='User Name')
    insuranceNum = forms.CharField(max_length=12, label='Insurance Number')
    password1 = forms.CharField(widget=forms.PasswordInput(attrs=dict(required=True, max_length=30, render_value=False)), label="Password")
    password2 = forms.CharField(widget=forms.PasswordInput(attrs=dict(required=True, max_length=30, render_value=False)), label="Password (again)")

    def is_valid(self):
        valid = super(RegistrationForm, self).is_valid()
        if not valid:
            return valid

        pattern = re.compile('^([A-Z]|[a-z]|[0-9]+)$')


        return (self.cleaned_data['password1'] == self.cleaned_data['password2']) and pattern.match(self.cleaned_data['insuranceNum'])


class LoginForm(forms.Form):
    username = forms.CharField(max_length=30, required=True, label="Username")
    password = forms.CharField(widget=forms.PasswordInput(attrs=dict(required=True, max_length=30, render_value=False)), label="Password")



