from django import forms
#from User.models import Patient, Doctor


#class EventForm(forms.Form):
#    patient = forms.ModelChoiceField(queryset=Patient.objects.all(), error_messages={'required':'Please select patient'}, required= True, empty_label=None)
#    doctor = forms.ModelChoiceField(queryset=Doctor.objects.all(), error_messages={'required':'Please select doctor'}, required= True, empty_label=None)
#    hospital = forms.ModelChoiceField(queryset=Hospital.objects.all(), error_messages={'required':'Please select hospital'}, required= True, empty_label=None)
#    startTime = forms.DateTimeField(error_messages={'required':'Select start time'}, required=True)
#    endTime = forms.DateTimeField(error_messages={'required':'Select end time'}, required = True)
#    fields = ['patient', 'doctor', 'hospital', 'startTime', 'endTime']