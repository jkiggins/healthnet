from django import forms
from .models import *
from django.contrib.auth.models import User
import emr.formvalid as formvalid


class FilterSortForm(forms.Form):

    keywords = forms.CharField(widget=forms.TextInput(attrs={'class': "emr_toolbox_serchbar", 'placeholder': "Keywords..."}), required=False)

    filter_choices = (
        ('prescription', 'Prescriptions'),
        ('vitals', 'Vitals'),
        ('test', 'Test Results'),
        ('pending', 'Pending Test Results'),
        ('admit', 'Admissions'),
        ('discharge', 'Discharges'),
    )


    filters = forms.MultipleChoiceField(required=False, choices=filter_choices, widget=forms.CheckboxSelectMultiple(attrs={'class': 'emr_toolbox_checkbox'}))
    quick_filters = forms.HiddenInput(attrs={'id': 'form_filter'})

    sort_choices = (
        ('date', 'Date'),
        ('alph', 'Aplhabetical'),
        ('priority', 'Priority')
    )

    sort = forms.ChoiceField(required=False, choices=sort_choices, widget=forms.RadioSelect(attrs={'class': 'emr_toolbox_checkbox'}))


class EMRItemCreateForm(forms.ModelForm):

    emrpatient = forms.ModelChoiceField(disabled=True, queryset=Patient.objects.all(), required=False, label="Patient")

    def save(self, **kwargs):
        m = super(EMRItemCreateForm, self).save(commit=False)

        m.date_created = timezone.now()
        m.patient = kwargs['patient']


        if ('commit' in kwargs) and kwargs['commit']:
            m.save()
        return m


    class Meta:
        model = EMRItem
        fields = ['title', 'content', 'priority']


class TestCreateForm(EMRItemCreateForm):

    images = forms.FileField(widget=forms.ClearableFileInput(), required=False)

    class Meta:
        model = EMRTest
        fields = ['title', 'content', 'priority', 'images', 'released']


class VitalsCreateForm(EMRItemCreateForm):
    class Meta:
        model = EMRVitals
        fields = ['title', 'content', 'priority', 'restingBPM', 'bloodPressure', 'height', 'weight', 'patient']


class prescriptionCreateForm(EMRItemCreateForm):

    proivder = forms.ModelChoiceField(disabled=True, queryset=Doctor.objects.all())

    def save(self, commit=False):
        m = super(prescriptionCreateForm, self).save(commit=False)
        m.deactivated = False

        if commit:
            m.save()

        return m

    def is_valid(self):
        valid = super(prescriptionCreateForm, self).is_valid()
        if not valid:
            return valid

        valid &= formvalid.prescriptionTimeIsPositive(self, datetime.timedelta(days=1), {'endTime': "Prescriptions must be valid for atleast 1 day"}, {})

        return valid


    class Meta:
        model = EMRPrescription
        fields = ['title', 'content', 'priority', 'dosage', 'amountPerDay', 'startDate', 'endDate', 'patient']


class ProfileCreateForm(EMRItemCreateForm):
    def save(self, commit=False, patient=None, doctor=None):
        m = super(ProfileCreateForm, self).save(commit=False)

        m.title = "Profile"

        if commit:
            m.save()

        return m

    def is_valid(self):
        valid = super(ProfileCreateForm, self).is_valid()
        if not valid:
            return valid

        valid &= formvalid.birthdayInPast(self, {'birthday': "your birthday must be in the past"}, {})
        valid &= formvalid.ageIsLessThan(self, 140, {'birthday': "You aren't > 140 years old, come on"})

        return valid


    class Meta:
        model = EMRProfile
        fields = ['content', 'birthdate', 'gender', 'blood_type', 'patient']

