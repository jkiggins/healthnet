from django.shortcuts import render, get_object_or_404
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, Http404
from User.models import *
from .forms import *
from django.views.generic import View



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

def viewCalendar(request, ut, pk):
    if ut == "p":
        user = get_object_or_404(Patient, pk=pk)
    elif ut == "d":
        user = get_object_or_404(Doctor, pk=pk)
    else:
        return Http404()

    render(request, 'viewcalendar.html', {'events': user.event_set.all()})

class viewEditEvent(View):

    def post(self, request):
        event = EventUpdateForm(request.POST)

        if event.is_valid():
            event.save(commit=True)
        else:
            return HttpResponseRedirect(reverse('User:dashboard', args=(3,))) # TODO: change from constant

    def get(self, request, pk):
        event = get_object_or_404(Event, pk=pk)

        if(request.group != "nurse" and request.group != "doctor" and request.user != event.patient):
            return HttpResponseRedirect(reverse('User:dashboard', args=(request.user.id,)))

        form = EventUpdateForm()

        context = {'form': form, 'event': event}

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
            e.patient = user
            e.save()

            return True

    def handleNurse(self, request):
        event = EventCreationFormNurse(request.POST)

        if event.is_valid_hospital():
            event.save(commit=True)
            return True
        else:
            return False

    def handleDoctor(self, request, user):
        event = EventCreationFormDoctor(request.POST)

        if event.is_valid():
            event.save_with_doctor(doctor=user, commit=True)
            return True
        else:
            return False


    def get(self, request):

        if(request.user.getType() == "patient"):
            event = EventCreationFormPatient()
        elif(request.user.getType() == "nurse"):
            event = EventCreationFormNurse()
        else:
            event = EventCreationFormDoctor()
            event.fields["patient"].queryset = Patient.objects.filter(doctor__id = request.user.id)


        return render(request, 'User/eventhandle.html', {'form': event, 'user': request.user})


    def post(self, request):
        if (request.user.getType() == "patient"):
            self.handlePatient(request, request.user)
            return HttpResponseRedirect(reverse('User:dashboard', args=(request.user.id,)))

        elif (request.user.getType() == "nurse"):
            if self.handleNurse(request):
                return HttpResponseRedirect(reverse('User:dashboard', args=(3,))) # TODO: change this to not a constant
            else:
                return HttpResponseRedirect(reverse('User:cEvent'))

        else:
            if self.handleDoctor(request, request.user):
                return HttpResponseRedirect(reverse('User:dashboard', args=(3,)))  # TODO: change this to not a constant
            else:
                return HttpResponseRedirect(reverse('User:cEvent'))


def dashboardView(request, pk):
   pt = get_object_or_404(Patient, pk=pk)

   events = pt.event_set.all().order_by('startTime')

   context = { 'user': pt, 'events': events}
   return render(request, 'User/dashboard.html', context)



