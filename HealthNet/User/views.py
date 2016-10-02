from django.shortcuts import render, get_object_or_404
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse
from User.models import User
from User.models import Nurse
from User.models import Doctor
from User.models import Patient

#from Calendar.forms import EventForm


# Create your views here.

#This method determines which type of user is using the app
#It will display the main page depending on which user is active
def index(request, pk):
    pass


def patientList(request):
    patientList = request.session['User'].patient_set.all()

    return render(request , 'User/userList.html' , patientList)


def viewProfile(request , pk):
    patient = get_object_or_404(Patient , pk=pk)

    return render(request, 'User/profile.html', patient)


def eventCreate(request):
    if request.method == 'POST':
        event = EventForm(request.POST)
        if event.is_valid():
            return HttpResponseRedirect(reverse('User:index'))
    else:
        event = EventForm()

    return render(request , 'html name')


def dashboardView(request, pk):
   pt = get_object_or_404(Patient, pk=pk)

   events = pt.Calendar.allEvents.all().order_by('startTime')

   context = { 'user': pt, 'events': events}
   return render(request, 'User/dashboard.html', context)



