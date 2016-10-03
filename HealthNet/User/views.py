from django.shortcuts import render, get_object_or_404
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, Http404
from User.models import *
from syslogging.models import *
from .forms import *
from django.views.generic import View
#from Calendar.forms import EventForm


# Create your views here.

#This method determines which type of user is using the app
#It will display the main page depending on which user is active

def get_user_or_404(request, requiredType):
    """Returns the user if they are logged in and their type is part of the requiredType tuple, if no a 404 is raised"""
    if request.user.is_authenticated():
        if (request.session['user_type'] in requiredType) or (request.user.username in requiredType):
            return getattr(request.user, request.session['user_type'])
    raise Http404()


def index(request, pk):
    pass


def patientList(request):
    patientList = request.session['User'].patient_set.all()

    return render(request , 'User/userList.html' , patientList)


def viewProfile(request , pk):
    patient = get_object_or_404(Patient , pk=pk)

    return render(request, 'User/dashboard.html', patient)


def viewCalendar(request, ut, pk):
    if ut == "p":
        user = get_object_or_404(Patient, pk=pk)
    elif ut == "d":
        user = get_object_or_404(Doctor, pk=pk)
    else:
        return Http404()

    render(request, 'viewcalendar.html', {'events': user.event_set.all()})


class EditProfile(View):

    def post(self, request):
        user=get_user_or_404(request, ("patient"))
        form = EditProfileForm(request.POST)

        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('User:dashboard'))
        else:
            return HttpResponseRedirect(reverse('User:eProfile'))

    def get(self, request):
        form = EditProfileForm()
        user = get_user_or_404(request, ("patient"))

        return render(request, 'User/editprofile.html', {'user': user, 'form': form})


class ViewEditEvent(View):

    def post(self, request, pk):
        event = EventUpdateForm(request.POST)
        old_event = get_object_or_404(Event, pk=pk)

        evpu = "-1"
        if old_event.patient != None:
            evpu = old_event.patient.user.username

        user = get_user_or_404(request, (evpu, old_event.doctor.user.username))


        if event.is_valid():
            if self.cleaned_data['delete']:
                Syslog.deleteEvent(old_event, user)
                old_event.delete()

            old_event = Events.objects.get(pk=pk)
            old_event.startTime = event.cleaned_data['startTime']
            old_event.endTime = event.cleaned_data['endTime']
            old_event.description = "This is a new description"
            old_event.save(force_update=True)

            return HttpResponseRedirect(reverse('User:dashboard'))
        else:
            return HttpResponseRedirect(reverse('User:dashboard'))


    def get(self, request, pk):
        event = get_object_or_404(Event, pk=pk)

        evpu = "-1"
        if event.patient != None:
            evpu = event.patient.user.username

        user = get_user_or_404(request, (evpu, event.doctor.user.username)) # TODO: fix no doctor bug

        form = EventUpdateForm(initial=event.__dict__)
        context = {'form': form, 'event': event, 'user': user}

        return render(request, 'User/eventdetail.html', context)


class CreateEvent(View):

    def handlePatient(self, request, user):
        event = EventCreationFormPatient(request.POST)

        if event.is_valid():
            e = event.save_with_patient(user)
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
            self.handlePatient(request, user)
            return HttpResponseRedirect(reverse('User:dashboard'))

        elif (user.getType() == "nurse"):
            if self.handleNurse(request):
                return HttpResponseRedirect(reverse('User:dashboard')) # TODO: change this to not a constant
            else:
                return HttpResponseRedirect(reverse('User:cEvent'))

        else:
            if self.handleDoctor(request, user):
                return HttpResponseRedirect(reverse('User:dashboard'))  # TODO: change this to not a constant
            else:
                return HttpResponseRedirect(reverse('User:cEvent'))


def dashboardView(request):
   pt = get_user_or_404(request, ("doctor", "patient", "nurse"))

   events = pt.event_set.all().order_by('startTime')

   context = { 'user': pt, 'events': events}
   return render(request, 'User/dashboard.html', context)

"""responsible for updating a patient profile
class UpadateProfile(UpdateView):

    model = Patient

    template_name = 'User/userForm.html'

    form_class = ProfileForm"""