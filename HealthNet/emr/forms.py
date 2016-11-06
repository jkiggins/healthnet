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



