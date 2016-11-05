from hospital.models import Hospital
from django import forms
from .models import *

def populate_dependant_fields(form, user):

    if user.getType() == 'doctor':
        if (form.cleaned_data['patient'] is None) and (form.cleaned_data['hospital'] is None):
            form.fields['patient'].queryset = user.patient_set.all()
            form.fields['hospital'].queryset = user.hospitals.all()
        elif not(form.cleaned_data['patient'] is None):
            #TODO: add code to set defualt value of dropdown to the hospital
            form.fields['hospital'].queryset = Hospital.objects.filter(pk=form.cleaned_data['patient'].hospital.pk)
        elif not(form.cleaned_data['hospital'] is None):
            patients = user.patient_set.filter(hospital=form.cleaned_data['hospital'])
            form.fields['patient'].queryset = patients

    elif user.getType() == 'nurse':
        if (form.cleaned_data['patient'] is None) and (form.cleaned_data['doctor'] is None):
            form.fields['patient'].queryset = user.hospital.patient_set.all()
            form.fields['doctor'].queryset = user.hospital.doctor_set.all()
        elif not(form.cleaned_data['patient'] is None) and (form.cleaned_data['doctor'] is None):
            #TODO: add code to set defualt value of dropdown to the doctor
            form.fields['doctor'].queryset = Doctor.objects.filter(pk=form.cleaned_data['patient'].doctor.pk)
        elif not(form.cleaned_data['doctor'] is None) and (form.cleaned_data['patient'] is None):
            patients = form.cleaned_data['doctor'].patient_set.filter(hospital=user.hospital)
            form.fields['patient'].queryset = patients


def setFormDefaultsFromModel(model, form):
    for key in form.fields:
        if hasattr(model, key):
            if isinstance(form.fields[key], forms.ModelChoiceField):
                form.fields[key].initial = getattr(model, key).pk
            else:
                form.fields[key].initial = getattr(model, key)
