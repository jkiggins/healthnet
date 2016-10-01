from django.shortcuts import render, get_object_or_404
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from User.models import User
from User.models import Nurse
from User.models import Doctor
from User.models import Patient
#from Calendar.forms import EventForm

# Create your views here.

#This method determines which type of user is using the app
#It will display the main page depending on which user is active
def index(request, pk):
    type = request.session['User'].getType

    if type == "nurse":
        return render(request , 'User/nurseIndex.html')
    elif type == "patient":
        patient = get_object_or_404(Patient, pk=pk)
        return render(request , 'User/patientIndex.html', {'patient': patient})
    elif type == "doctor":
        return render(request , 'User/doctorIndex.html')


def patientList(request):
    patientList = request.session['User'].patient_set.all()

    return render(request , 'User/patientList.html' , patientList)


def viewProfile(request , pk):
    patient = get_object_or_404(Patient , pk=pk)

    return render(request , 'User/profile.html' , patient)


def eventCreate(request):
    if request.method == 'POST':
        event = EventForm(request.POST)
        if event.is_valid():
            return HttpResponseRedirect(reverse('User:index'))
    else:
        event = EventForm()

    return render(request , 'html name')