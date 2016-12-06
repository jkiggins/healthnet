from django import forms
from .models import *
from django.contrib.auth.models import User
import HealthNet.formvalid as formvalid


class FilterSortForm(forms.ModelForm):

    keywords = forms.CharField(widget=forms.TextInput(attrs={'class': "toolbar_searchbar", 'placeholder': "Keywords..."}), required=False)

    filter_choices = (
        ('prescription', 'Prescriptions'),
        ('vitals', 'Vitals'),
        ('test', 'Test Results'),
        ('pending', 'Pending Test Results'),
        ('admit', 'Admissions'),
        ('discharge', 'Discharges'),
    )


    filters_l = forms.MultipleChoiceField(required=False, choices=filter_choices, widget=forms.CheckboxSelectMultiple(attrs={'class': 'toolbar_item_checkbox'}))
    quick_filters = forms.HiddenInput(attrs={'id': 'form_filter'})

    sort_choices = (
        ('date', 'Date'),
        ('alph', 'Aplhabetical'),
        ('priority', 'Priority')
    )

    sort = forms.ChoiceField(required=False, choices=sort_choices, widget=forms.RadioSelect(attrs={'class': 'toolbar_item_checkbox'}))


    def __init__(self, *args, **kwargs):
        super(FilterSortForm, self).__init__(*args, **kwargs)

        if 'instance' in kwargs:
            self.initial['filters_l'] = kwargs['instance'].filters.split(",")

    def save(self, commit=False):
        m = super(FilterSortForm, self).save(commit=False)

        str = ""
        for f in self.cleaned_data['filters_l']:
            str += f + ","

        str = str[:-1]

        m.filters = str

        if commit:
            m.save()
        return m

    class Meta:
        model = FilterForm
        fields = ['keywords', 'sort']


class EMRItemCreateForm(forms.ModelForm):

    priority = forms.ChoiceField(choices=EMRItem.PRIORITY_CHOICES, initial=1)
    content = forms.CharField(widget=forms.Textarea(), label="Comments")
        

    def save(self, **kwargs):
        m = super(EMRItemCreateForm, self).save(commit=False)

        if 'update' in kwargs:
            m = self.saveToModel(kwargs['update'])
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

    def saveToModel(self, model):
        for key in self.cleaned_data:
            if not self.fields[key].disabled:
                if hasattr(model, key):
                    setattr(model, key, self.cleaned_data[key])
        return model


    class Meta:
        model = EMRItem
        fields = ['content', 'priority']


class TestCreateForm(EMRItemCreateForm):

    images = forms.FileField(widget=forms.FileInput(), required=False)

    def defaults(self, model):
        super(TestCreateForm, self).defaults(model)
        if hasattr(model, 'emrtest'):
            self.populateFromModel(model.emrtest)

    def save(self, **kwargs):
        m = super(TestCreateForm, self).save(**kwargs)

        if 'update' in kwargs:
            if self.cleaned_data['images'] is None:
                del self.cleaned_data['images']

            self.saveToModel(kwargs['update'].emrtest)

        if 'commit' in kwargs:
            if kwargs['commit']:
                m.save()
                m.emrtest.save()
        return m


    class Meta:
        model = EMRTest
        fields = ['images', 'released', 'content', 'priority']


class VitalsCreateForm(EMRItemCreateForm):

    height = forms.IntegerField(label="Height (inches)")
    weight = forms.IntegerField(label="Weight (LBS)")

    def defaults(self, model):
        super(VitalsCreateForm, self).defaults(model)
        if hasattr(model, 'emrvitals'):
            self.populateFromModel(model.emrvitals)

    def save(self, **kwargs):
        commit = kwargs['commit']
        kwargs['commit'] = False
        m = super(VitalsCreateForm, self).save(**kwargs)

        if 'update' in kwargs:
            self.saveToModel(m.emrvitals)

        if commit:
            m.emrvitals.save()
            m.save()

        return m

    class Meta:
        model = EMRVitals
        fields = ['restingBPM', 'bloodPressure', 'height', 'weight','content', 'priority']


class prescriptionCreateForm(EMRItemCreateForm):

    amountPerDay = forms.CharField(label="Doses Per Day")
    dosage = forms.CharField(label="Dosage(mg)")
    def save(self, **kwargs):
        commit = kwargs['commit']
        kwargs['commit'] = False
        m = super(prescriptionCreateForm, self).save(**kwargs)

        if 'update' in kwargs:
            self.saveToModel(m.emrprescription)

        if commit:
            m.emrprescription.save()
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
        fields = ['medication', 'dosage', 'amountPerDay', 'startDate', 'endDate', 'content', 'priority']


class ProfileCreateForm(forms.ModelForm):

    def save(self, **kwargs):
        model = None
        if 'model' in kwargs:
            model = kwargs['model']
            for key in self.cleaned_data:
                if hasattr(model, key):
                    setattr(model, key, self.cleaned_data[key])

        else:
            model = super(ProfileCreateForm, self).save(commit=False)

        if 'commit' in kwargs:
            if kwargs['commit']:
                model.save()

        return model


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


class AdmitDishchargeForm(EMRItemCreateForm):

    def save(self, **kwargs):
        commit = kwargs['commit']
        kwargs['commit'] = False
        m = super(AdmitDishchargeForm, self).save(**kwargs)

        if 'update' in kwargs:
            self.saveToModel(m.emradmitstatus)

        if commit:
            m.emradmitstatus.save()
            m.save()
        return m


    def lockField(self, field, value):
        if field in self.fields:
            if value is None:
                del self.fields[field]
            else:
                self.fields[field].initial = value
                self.fields[field].disabled = True
                self.fields[field].required = False
                print("hello")

    def defaults(self, model):
        super(AdmitDishchargeForm, self).defaults(model)
        if hasattr(model, 'emradmitstatus'):
            self.populateFromModel(model.emradmitstatus)

    class Meta:
        model=EMRAdmitStatus
        fields = ['hospital', 'priority', 'content']
