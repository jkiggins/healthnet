from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from User.models import Patient

# Create your views here.

def patientIndex(request):
    patientInfo = Patient.objects.all()