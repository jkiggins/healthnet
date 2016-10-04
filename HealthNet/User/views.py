from django.shortcuts import render, get_object_or_404
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, Http404
from User.models import *
from syslogging.models import *
from .forms import *
from django.views.generic import View
from logIn.models import *
from django.contrib.auth import logout
#from Calendar.forms import EventForm


# Create your views here.

#This method determines which type of user is using the app
#It will display the main page depending on which user is active

def get_user_or_404(request, requiredType):
    """Returns the user if they are logged in and their type is part of the requiredType tuple, if no a 404 is raised"""
    if request.user.is_authenticated():
        if hasattr(request.user, 'patient'):
            ut = 'patient'
        elif hasattr(request.user, 'nurse'):
            ut = 'nurse'
        elif hasattr(request.user, 'doctor'):
            ut = 'doctor'

        if (ut in requiredType) or (request.user.username in requiredType):
            return getattr(request.user, ut)
    Syslog.unauth_acess(request)
    raise Http404()


def index(request, pk):
    pass


def patientList(request):
    patientList = request.session['User'].patient_set.all()

    return render(request , 'User/userList.html' , patientList)


def viewProfile(request , ut, pk):
    cuser = get_user_or_404(request, ("nurse", "doctor"))
    trusted = False
    user = None
    if ut == "patient":
        user = get_object_or_404(Patient, pk=pk)
        trusted = True
    elif ut == "doctor":
        user = get_object_or_404(Doctor, pk=pk)
        if cuser.getType() == "nurse":
            if cuser.trusted.all().filter(pk=user.id).count() == 1:
                trusted = True
    else:
        return Http404()



    return render(request, 'User/viewprofile.html', {'user': user, 'trusted': trusted, 'events': user.event_set.all()})


class EditProfile(View):

    def post(self, request):
        user = get_user_or_404(request, ("patient"))
        form = EditProfileForm(request.POST)

        if form.is_valid():
            form.save_user(user)
            Syslog.editProfile(user)
            return HttpResponseRedirect(reverse('User:dashboard'))
        else:
            return HttpResponseRedirect(reverse('User:eProfile'))

    def get(self, request):
        user = get_user_or_404(request, ("patient"))
        form = EditProfileForm()
        form.set_defaults(user)

        return render(request, 'User/editprofile.html', {'user': user, 'form': form})


class ViewEditEvent(View):

    def post(self, request, pk):
        event = EventUpdateForm(request.POST)
        old_event = get_object_or_404(Event, pk=pk)

        evpu = ""
        if old_event.patient != None:
            evpu = old_event.patient.user.username

        user = get_user_or_404(request, (evpu, old_event.doctor.user.username))


        event.is_valid()
        if event.save_with_event(old_event):
            Syslog.modifyEvent(old_event, user)
            return HttpResponseRedirect(reverse('User:dashboard'))
        else:
            return HttpResponseRedirect(reverse('User:veEvent', args=(old_event.id,)))


    def get(self, request, pk):
        event = get_object_or_404(Event, pk=pk)

        evpu = "-1"
        if event.patient != None:
            evpu = event.patient.user.username

        user = get_user_or_404(request, (evpu, event.doctor.user.username)) # TODO: fix no doctor bug

        form = EventUpdateForm()
        form.set_defaults(event)
        context = {'form': form, 'event': event, 'user': user}

        return render(request, 'User/eventdetail.html', context)


class CreateEvent(View):

    def handlePatient(self, request, user):
        event = EventCreationFormPatient(request.POST)
        return event.save_with_patient(user)

    def handleNurse(self, request):
        event = EventCreationFormNurse(request.POST)
        return event.save(commit=True)


    def handleDoctor(self, request, user):
        event = EventCreationFormDoctor(request.POST)

        return event.save_with_doctor(doctor=user, commit=True)


    def get(self, request):
        user = get_user_or_404(request, ("patient", "doctor", "nurse"))

        if(user.getType() == "patient"):
            event = EventCreationFormPatient()
        elif(user.getType() == "nurse"):
            event = EventCreationFormNurse()
        else:
            event = EventCreationFormDoctor()
            event.fields["patient"].queryset = Patient.objects.filter(doctor__id = user.id)


        return render(request, 'User/eventhandle.html', {'form': event, 'user': user})


    def post(self, request):
        user = get_user_or_404(request, ("patient", "doctor", "nurse"))

        if (user.getType() == "patient"):
            if self.handlePatient(request, user):
                return HttpResponseRedirect(reverse('User:dashboard'))
            else:
                return HttpResponseRedirect(reverse('User:cEvent'))

        elif (user.getType() == "nurse"):
            if self.handleNurse(request):
                return HttpResponseRedirect(reverse('User:dashboard'))
            else:
                return HttpResponseRedirect(reverse('User:cEvent'))

        else:
            if self.handleDoctor(request, user):
                return HttpResponseRedirect(reverse('User:dashboard'))
            else:
                return HttpResponseRedirect(reverse('User:cEvent'))


def dashboardView(request):
    user = get_user_or_404(request, ("doctor", "patient", "nurse"))

    context = {'user': user}

    if(user.getType() != "nurse"):
        events = user.event_set.all().order_by('startTime')
        context['events'] = events
    elif(user.getType() == "doctor"):
        context['patients'] = user.patient_set.all()
        context['hosptials'] = user.hospitals.all()
    elif(user.getType() == "nurse"):
        context['patients'] = user.hospital.patient_set.all()
        context['doctors'] = user.hospital.doctor_set.all()


    return render(request, 'User/dashboard.html', context)