from hospital.models import Hospital
from django import forms
from .models import *

def populateDependantFieldsPD(form, pqset, dqset, hospital):
    if ('patient' in form.cleaned_data) and ('doctor' in form.cleaned_data):
        if (form.cleaned_data['patient'] is None) and (form.cleaned_data['doctor'] is None):
            form.fields['patient'].queryset = pqset
            form.fields['doctor'].queryset = dqset
        elif (form.cleaned_data['doctor'] is None):
            #TODO: add code to set defualt value of dropdown to the doctor
            form.fields['doctor'].queryset = Doctor.objects.filter(pk=form.cleaned_data['patient'].doctor.pk)
        elif (form.cleaned_data['patient'] is None):
            patients = form.cleaned_data['doctor'].patient_set.filter(hospital=hospital)
            form.fields['patient'].queryset = patients


def populateDependantFieldsDH(form, dqset, hqset):
    if ('doctor' in form.cleaned_data) and ('hospital' in form.cleaned_data):
        if (form.cleaned_data['doctor'] is None) and (form.cleaned_data['hospital'] is None):
            form.fields['hospital'].queryset = hqset
            form.fields['doctor'].queryset = dqset
        elif (form.cleaned_data['hospital'] is None):
            print(form.fields['hospital'])
            form.fields['hospital'].queryset = form.cleaned_data['doctor'].hospitals.all()
        elif (form.cleaned_data['doctor'] is None):
            form.fields['doctor'].queryset = form.cleaned_data['hospital'].doctor_set.all()


def populateDependantFieldsPH(form, pqset, hqset):
    if ('patient' in form.cleaned_data) and ('hospital' in form.cleaned_data):
        if (form.cleaned_data['patient'] is None) and (form.cleaned_data['hospital'] is None):
            form.fields['patient'].queryset = pqset
            form.fields['hospital'].queryset = hqset
        elif (form.cleaned_data['hospital'] is None):
            #TODO: add code to set defualt value of dropdown to the hospital
            form.fields['hospital'].queryset = Hospital.objects.filter(pk=form.cleaned_data['patient'].hospital.pk)
        elif (form.cleaned_data['patient'] is None):
            patients = pqset.filter(hospital=form.cleaned_data['hospital'])
            form.fields['patient'].queryset = patients


def setFormDefaultsFromModel(model, form):
    for key in form.fields:
        if hasattr(model, key):
            if isinstance(form.fields[key], forms.ModelChoiceField):
                form.fields[key].initial = getattr(model, key).pk
            else:
                form.fields[key].initial = getattr(model, key)
