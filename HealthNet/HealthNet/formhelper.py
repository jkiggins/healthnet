from hospital.models import Hospital
from django import forms
from user.models import *

def populateDependantFieldsPD(form, pqset, dqset, hospital):
    if ('patient' in form.cleaned_data) and ('doctor' in form.cleaned_data):
        if (form.cleaned_data['patient'] is None) and (form.cleaned_data['doctor'] is None):
            form.fields['patient'].queryset = pqset
            form.fields['doctor'].queryset = dqset
        elif not (form.cleaned_data['patient'] is None):
            #TODO: add code to set defualt value of dropdown to the docto
            form.fields['doctor'].queryset = Doctor.objects.filter(pk=form.cleaned_data['patient'].doctor.pk)
        elif not(form.cleaned_data['doctor'] is None):
            patients = form.cleaned_data['doctor'].patient_set.filter(hospital=hospital)
            form.fields['patient'].queryset = patients


def populateDependantFieldsDH(form, dqset, hqset):
    if ('doctor' in form.cleaned_data) and ('hospital' in form.cleaned_data):
        if (form.cleaned_data['doctor'] is None) and (form.cleaned_data['hospital'] is None):
            form.fields['hospital'].queryset = hqset
            form.fields['doctor'].queryset = dqset
        elif not(form.cleaned_data['doctor'] is None):
            form.fields['hospital'].queryset = form.cleaned_data['doctor'].hospitals.all()
        elif not(form.cleaned_data['hospital'] is None):
            form.fields['doctor'].queryset = form.cleaned_data['hospital'].doctor_set.all()


def populateDependantFieldsPH(form, pqset, hqset):
    if ('patient' in form.cleaned_data) and ('hospital' in form.cleaned_data):
        if (form.cleaned_data['patient'] is None) and (form.cleaned_data['hospital'] is None):
            form.fields['patient'].queryset = pqset
            form.fields['hospital'].queryset = hqset
        elif not(form.cleaned_data['patient'] is None):
            #TODO: add code to set defualt value of dropdown to the hospital
            form.fields['hospital'].queryset = Hospital.objects.filter(pk=form.cleaned_data['patient'].hospital.pk)
        elif not(form.cleaned_data['hospital'] is None):
            patients = pqset.filter(hospital=form.cleaned_data['hospital'])
            form.fields['patient'].queryset = patients
            form.fields['hospital'].queryset = hqset


def setFormDefaultsFromModel(model, form):
    for key in form.fields:
        if hasattr(model, key):
            if isinstance(form.fields[key], forms.ModelChoiceField):
                form.fields[key].initial = getattr(model, key).pk
            else:
                form.fields[key].initial = getattr(model, key)


def setEditFormDefault(user, form):
    form.fields['first_name'].initial = getattr(user.user, 'first_name')
    form.fields['last_name'].initial = getattr(user.user, 'last_name')
    form.fields['email'].initial = getattr(user.user, 'email')

    if user is not None:
        form.fields['phone'].initial = getattr(user, 'phone')
        form.fields['address'].initial = getattr(user, 'address')
        form.fields['doctor'].initial = getattr(user, 'doctor')
        form.fields['hospital'].initial = getattr(user, 'hospital')

    if user.contact is not None:
        if user.contact.emuser is not None:
            form.fields['emuser'].initial = user.contact.emuser.pk
        form.fields['full_name'].initial = getattr(user.contact, 'full_name')
        form.fields['emphone'].initial = getattr(user.contact, 'emphone')
