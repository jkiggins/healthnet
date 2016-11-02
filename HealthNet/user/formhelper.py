from hospital.models import Hospital
from .models import *

def populate_dependant_fields(form, user):

    if user.getType() == 'doctor':
        if (form.cleaned_data['patient'] is None) and (form.cleaned_data['hospital'] is None):
            form.fields['patient'] = user.patient_set.all()
            form.fields['hospital'] = user.hospitals.all()
        elif not(form.cleaned_data['patient'] is None):
            #TODO: add code to set defualt value of dropdown to the hospital
            form.fields['hospital'].queryset = Hospital.objects.filter(pk=form.cleaned_data['patient'].hospital.pk)
        elif not(form.cleaned_data['hospital'] is None):
            patients = user.patient_set.filter(hospital=form.cleaned_data['hospital'])
            form.fields['patient'].queryset = patients

    elif user.getType() == 'nurse':
        if (form.cleaned_data['patient'] is None) and (form.cleaned_data['doctor'] is None):
            form.fields['patient'] = user.hospital.patient_set.all()
            form.fields['hospital'] = user.hospital.doctor_set.all()
        elif not(form.cleaned_data['patient'] is None) and (form.cleaned_data['doctor'] is None):
            #TODO: add code to set defualt value of dropdown to the doctor
            form.fields['doctor'].queryset = Doctor.objects.filter(pk=form.cleaned_data['patient'].doctor.pk)
        elif not(form.cleaned_data['doctor'] is None) and (form.cleaned_data['patient'] is None):
            patients = form.cleaned_data['doctor'].patient_set.filter(hospital=user.hospital)
            form.fields['patient'].queryset = patients

# def populate_dependant_fields(form, kvp_dict, user):
#
#     model_map = {'p': Patient, 'd': Doctor, 'h': Hospital}
#     parsed_models = {'p': None, 'd': None, 'h': None}
#
#
#     for key in kvp_dict:
#         if key in model_map:
#             models = model_map[key].objects.filter(pk=kvp_dict[key])
#
#             if models.count() > 0:
#                 parsed_models[key] = models[0]
#
#
#
#     if user.getType() == 'doctor':
#         if (parsed_models['p'] is None) and (parsed_models['h'] is None):
#             form.fields['hospital'].queryset = user.hospitals.all()
#             form.fields['patient'] = user.patient_set.all()
#         elif (parsed_models['h'] is None):
#             #TODO: add code to set defualt value of dropdown to the parsed_models['h']
#             form.fields['hospital'].queryset = Hospital.objects.filter(pk=parsed_models['p'].hospital.pk)
#         elif (parsed_models['p'] is None):
#             patients = user.patient_set.filter(hospital=parsed_models['h'])
#             form.fields['patient'].queryset = patients
#         else:
#             return False
#
#     elif user.getType() == 'nurse':
#         if (parsed_models['p'] is None) and (parsed_models['d'] is None):
#             form.fields['patient'].queryset = user.hospital.patient_set.all()
#             form.fields['doctor'].queryset = user.hospital.doctor_set.all()
#         elif (parsed_models['d'] is None):
#             #TODO: add code to set defualt value of dropdown to the parsed_models['d']
#             form.fields['doctor'].queryset = parsed_models['d'].objects.filter(pk=parsed_models['p'].doctor.pk)
#         elif (parsed_models['p'] is None):
#             patients = parsed_models['d'].patient_set.filter(hospital=user.hospital)
#             form.fields['patient'].queryset = patients
#         else:
#             return False
#
#     return True
