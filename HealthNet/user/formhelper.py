from hospital.models import Hospital
from .models import Doctor

def populate_dependant_fields(form, user):

    if user.getType() == 'doctor':
        if not(form.cleaned_data['patient'] is None) and (form.cleaned_data['hospital'] is None):
            #TODO: add code to set defualt value of dropdown to the hospital
            form.fields['hospital'].queryset = Hospital.objects.filter(pk=form.cleaned_data['patient'].hospital.pk)
        elif not(form.cleaned_data['hospital'] is None) and (form.cleaned_data['patient'] is None):
            patients = user.patient_set.filter(hospital=form.cleaned_data['hospital'])
            form.fields['patient'].queryset = patients
        else:
            return False

    elif user.getType() == 'nurse':
        if not(form.cleaned_data['patient'] is None) and (form.cleaned_data['doctor'] is None):
            #TODO: add code to set defualt value of dropdown to the doctor
            form.fields['doctor'].queryset = Doctor.objects.filter(pk=form.cleaned_data['patient'].doctor.pk)
        elif not(form.cleaned_data['doctor'] is None) and (form.cleaned_data['patient'] is None):
            patients = form.cleaned_data['doctor'].patient_set.filter(hospital=user.hospital)
            form.fields['patient'].queryset = patients
        else:
            return False

    return True
