from django.shortcuts import render, get_object_or_404
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse
from User.models import *
from .forms import *
from django.views.generic import View

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

def viewCalendar(request, pk):
    calendar = get_object_or_404(Calendar, pk=pk)
    context = {'events': calendar.allEvents}

    render(request, 'viewcalendar.html', context)

def viewEvent(request, pk):
    event = get_object_or_404(Event, pk=pk)
    users = []

    for cal in event.calendar_set.all():
        if hasattr(cal, 'nurse'):
            users.append(cal.nurse)
        elif hasattr(cal, 'patient'):
            users.append(cal.patient)
        elif hasattr(cal, 'doctor'):
            users.append(cal.doctor)

    context = {'event': event, 'users': users}

    if ('User' in request.session):
        context['user'] = request.session['User']
    else:
        context['user'] = Patient.objects.all()[0] # TODO: remove this before release

    return render(request, 'User/eventdetail.html', context)


class CreateEvent(View):

    def handlePatient(self, request, user):
        event = EventCreationFormPatient(request.POST)
        if event.is_valid():
            e = event.save_with_hosptial(user.hospital)

            user.Calendar.allEvents.add(e)
            user.doctor.Calendar.allEvents.add(e)
            user.Calendar.save()
            user.doctor.Calendar.save()
            return True

    def handleNurse(self, request, user):
        event = EventCreationFormNurse(request.POST)

        if event.is_valid():
            event.save(commit=True)
            return True
        else:
            return False


    def get(self, request):
        # user = Patient.objects.get(pk=3)  # TODO: delete this after login works
        user = Nurse.objects.get(pk=1)

        if(user.getType() == "patient"):
            event = EventCreationFormPatient()
        elif(user.getType() == "nurse"):
            event = EventCreationFormNurse()


        return render(request, 'User/eventhandle.html', {'form': event, 'user': user})


    def post(self, request):
        # user = Patient.objects.get(pk=3)  # TODO: delete this after login works
        user = Nurse.objects.get(pk=1)
        if (user.getType() == "patient"):
            self.handlePatient(request, user)
            return HttpResponseRedirect(reverse('User:dashboard', args=(user.id,)))

        elif (user.getType() == "nurse"):
            print("######AT NURSE POST#####")
            if self.handleNurse(request, user):
                return HttpResponseRedirect(reverse('User:dashboard', args=(3,))) # TODO: change this to not a constant
            else:
                return HttpResponseRedirect(reverse('User:cEvent'))




def editEvent(request, pk):
    pass


def dashboardView(request, pk):
   pt = get_object_or_404(Patient, pk=pk)

   events = pt.Calendar.allEvents.all().order_by('startTime')

   context = { 'user': pt, 'events': events}
   return render(request, 'User/dashboard.html', context)



