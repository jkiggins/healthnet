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

        if 'update' in kwargs:
            model = kwargs['update']
            for key in self.cleaned_data:
                if hasattr(model, key):
                    setattr(model, key, self.cleaned_data[key])
            model.save()
        else:
            m.date_created = timezone.now()
            m.patient = kwargs['patient']


            if ('commit' in kwargs) and kwargs['commit']:
                m.save()

        return m

    def populateFromModel(self, model):
        for key in self.fields:
            if hasattr(model, key):
                self.fields[key].initial = getattr(model, key)

    def defaults(self, model):
        self.populateFromModel(model)



    class Meta:
        model = EMRItem
        fields = ['title', 'content', 'priority']


class TestCreateForm(EMRItemCreateForm):

    images = forms.FileField(widget=forms.ClearableFileInput(), required=False)

    def defaults(self, model):
        super(TestCreateForm, self).defaults(model)
        if hasattr(model, 'emrtest'):
            self.populateFromModel(model.emrtest)

    class Meta:
        model = EMRTest
        fields = ['title', 'content', 'priority', 'images', 'released']


class VitalsCreateForm(EMRItemCreateForm):

    def defaults(self, model):
        super(VitalsCreateForm, self).defaults(model)
        if hasattr(model, 'emrvitals'):
            self.populateFromModel(model.emrvitals)

    class Meta:
        model = EMRVitals
        fields = ['title', 'content', 'priority', 'restingBPM', 'bloodPressure', 'height', 'weight']


class prescriptionCreateForm(EMRItemCreateForm):

    proivder = forms.ModelChoiceField(disabled=True, queryset=User.objects.all().filter(patient=None).filter(nurse=None))

    def save(self, **kwargs):
        commit = kwargs['commit']
        kwargs['commit'] = False
        m = super(prescriptionCreateForm, self).save(**kwargs)
        m.deactivated = False
        m.provider = kwargs['provider']

        if commit:
            m.save()

        return m

    def is_valid(self):
        valid = super(prescriptionCreateForm, self).is_valid()
        if not valid:
            return valid

        valid &= formvalid.prescriptionTimeIsPositive(self, datetime.timedelta(days=1), {'endTime': "Prescriptions must be valid for atleast 1 day"}, {})

        return valid

    def defaults(self, model):
        super(prescriptionCreateForm, self).defaults(model)
        if hasattr(model, 'emrprescription'):
            self.populateFromModel(model.emrprescription)

    class Meta:
        model = EMRPrescription
        fields = ['title', 'content', 'priority', 'dosage', 'amountPerDay', 'startDate', 'endDate', 'proivder']


class ProfileCreateForm(forms.ModelForm):

    emrpatient = forms.ModelChoiceField(queryset=Patient.objects.all(), required=False, disabled=True, label="Patient")

    def save(self, **kwargs):
        model = kwargs['patient'].emrprofile

        if model is None:
            m = super(ProfileCreateForm, self).save(commit=False)
            m.patient = kwargs['patient']
            m.save()
        else:
            for key in self.cleaned_data:
                if hasattr(model, key):
                    setattr(model, key, self.cleaned_data[key])

            model.save()

    def is_valid(self):
        valid = super(ProfileCreateForm, self).is_valid()
        if not valid:
            return valid

        valid &= formvalid.birthdayInPast(self, {'birthday': "your birthday must be in the past"}, {})
        valid &= formvalid.ageIsLessThan(self, 140, {'birthday': "You aren't > 140 years old, come on"}, {})

        return valid

    def defaults(self, model):
        for key in model.__dict__:
            if key in self.fields:
                self.fields[key].initial = model.__dict__[key]


    class Meta:
        model = EMRProfile
        fields = ['birthdate', 'gender', 'blood_type', 'family_history', 'comments']

