from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from User.models import Patient

# Create your views here.

# This will display the patient's main view
# This will include a link to add an appointment,
# Change an appointment, or access their EMR info.
# Also this will display the hospital and doctor assigned to them
def patientIndex(request):
    patientInfo = Patient.objects.all()
    return render(request, 'Patient/index.html', {'patientInfo' : patientInfo})