from django import forms
from user.models import *
from user.formvalid import dict_has_keys
from hospital.models import *
import re
from django.contrib.auth.models import User



class RegistrationForm(forms.Form):

    insuranceNum = forms.CharField(max_length=12, label='Insurance Number')

    def is_valid(self):
        valid = super(RegistrationForm, self).is_valid()
        if not valid:
            return valid

        pattern = re.compile('^[A-Z]([a-zA-Z]|[0-9]+){11}$')

        if not pattern.match(self.cleaned_data['insuranceNum']):
            FormValid.add_messages(self, {'insuranceNum': "Insurance Number must start with an upper case letter followed by 11 alphanumeric characters"}, {})
            valid = False


        return valid


class RegistrationFormFull(RegistrationForm):
    username = forms.CharField(max_length=30, label='User Name', required=True)
    password1 = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs=dict(required=True, max_length=30, render_value=False)), label="Password")
    password2 = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs=dict(required=True, max_length=30, render_value=False)),
        label="Password (again)")

    def is_valid(self):
        valid = super(RegistrationFormFull, self).is_valid()
        if not valid:
            return valid

        valid &= FormValid.usernameIsUnique(self, {'username': "This username is already in use"}, {})
        valid &= FormValid.passwordsMatch(self, {'password2': "Passwords Don't match"}, {})

        return valid

class StaffRegistrationForm(forms.Form):
    username = forms.CharField(max_length=30, label='User Name', required=True)
    password1 = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs=dict(required=True, max_length=30, render_value=False)), label="Password")
    password2 = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs=dict(required=True, max_length=30, render_value=False)),
        label="Password (again)")
    firstName = forms.CharField(max_length=30, required=True)
    lastName = forms.CharField(max_length=30, required=True)
    email =forms.EmailField(required=True)

    def is_valid(self):
        valid = super(StaffRegistrationForm, self).is_valid()
        if not valid:
            return valid

        valid &= FormValid.usernameIsUnique(self, {'username': "This username is already in use"}, {})
        valid &= FormValid.passwordsMatch(self, {'password2': "Passwords Don't match"}, {})

        return valid

class DoctorRegistrationForm(StaffRegistrationForm):
    hospitals = forms.ModelMultipleChoiceField(Hospital.objects.all(), label="Hospital Selection", required=True, widget=forms.CheckboxSelectMultiple())

class NurseRegistrationForm(StaffRegistrationForm):
    hospital = forms.ModelChoiceField(Hospital.objects.all(), label="Hospital Selection", required=True)

class UserSelectForm(forms.Form):
    typeOfUser = forms.MultipleChoiceField(choices=(('doctor', 'Doctor'), ('nurse', 'Nurse')), required=True, label="Are you a doctor or a nurse?")

class LoginForm(forms.Form):
    username = forms.CharField(max_length=30, required=True, label="Username")
    password = forms.CharField(widget=forms.PasswordInput(attrs=dict(required=True, max_length=30, render_value=False)), label="Password")


class FormValid:

    @staticmethod
    def add_messages(form, error, help):
        for key in error:
            form.add_error(key, error[key])

        for key in help:
            form.fields[key].help_text = help[key]

    @staticmethod
    def registerFormHasAllFields(form):
        for key in ['username', 'password1', 'password2']:
            if not(key in form.cleaned_data):
                return False
        return True

    @staticmethod
    def usernameIsUnique(form, error, help):
        if not dict_has_keys(['username'], form.cleaned_data):
            return False

        if User.objects.filter(username=form.cleaned_data['username']).count() > 0:
            FormValid.add_messages(form, error, help)
            return False
        return True

    @staticmethod
    def passwordsMatch(form, error, help):
        if not dict_has_keys(['password1', 'password2'], form.cleaned_data):
            return False

        if form.cleaned_data['password1'] != form.cleaned_data['password2']:
            FormValid.add_messages(form, error, help)
            return False
        return True