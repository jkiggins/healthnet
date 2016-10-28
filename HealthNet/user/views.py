from django.shortcuts import render, get_object_or_404
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, Http404
from syslogging.models import *
from .forms import *
from django.views.generic import View
from logIn.models import *
from .formvalid import *
from django.contrib.auth import logout


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


def add_dict_to_model(dict, event):
    for key in dict:
        setattr(event, key, dict[key])


def index(request, pk):
    pass


def patientList(request):
    patientList = request.session['user'].patient_set.all()

    return render(request , 'user/userList.html' , patientList)


def viewProfile(request , ut, pk):
    cuser = get_user_or_404(request, ("nurse", "doctor"))
    trusted = True
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



    return render(request, 'user/viewprofile.html', {'user': user, 'trusted': trusted, 'events': user.event_set.all()})


class EditProfile(View):

    def post(self, request):
        user = get_user_or_404(request, ("patient"))
        form = EditProfileForm(request.POST)

        if form.is_valid():
            form.save_user(user)
            Syslog.editProfile(user)
            return HttpResponseRedirect(reverse('user:dashboard'))
        else:
            return HttpResponseRedirect(reverse('user:eProfile'))

    def get(self, request):
        user = get_user_or_404(request, ("patient"))
        form = EditProfileForm()
        form.set_defaults(user)

        return render(request, 'user/editprofile.html', {'user': user, 'form': form})


class ViewEditEvent(View):

    def post(self, request, pk):
        event = EventUpdateForm(request.POST)
        old_event = get_object_or_404(Event, pk=pk)

        evpu = ""
        if old_event.patient != None:
            evpu = old_event.patient.user.username

        user = get_user_or_404(request, (evpu, "doctor", "nurse"))


        event.is_valid()
        if event.save_with_event(old_event):
            Syslog.modifyEvent(old_event, user)
            return HttpResponseRedirect(reverse('user:dashboard'))
        else:
            return HttpResponseRedirect(reverse('user:veEvent', args=(old_event.id,)))


    def get(self, request, pk):
        event = get_object_or_404(Event, pk=pk)

        evpu = "-1"
        if event.patient != None:
            evpu = event.patient.user.username

        user = get_user_or_404(request, (evpu, "doctor", "nurse")) # TODO: fix no doctor bug

        form = EventUpdateForm()
        form.set_defaults(event)

        if user.getType() == "nurse":
            form.disable_delete()

        context = {'form': form, 'event': event, 'user': user}

        return render(request, 'user/eventdetail.html', context)


class CreateEvent(View):

    def handle_patient(self, request, user, event_form):
        event = event_form.getModel()
        # Add fields that weren't included in the form and validate the model
        et = event.startTime + datetime.timedelta(minutes=event_form.cleaned_data['duration'])
        add_dict_to_model({'hospital': user.hospital, 'doctor': user.doctor, 'patient': user, 'endTime':et}, event)

        conflicts = event.conflicts()

        if conflicts == 0:
            event.save()
            return HttpResponseRedirect(reverse('user:dashboard'))
        elif conflicts == 1:
            EventCreationFormValidator.add_messages(event_form, {'duration': "Duration is too long"}, {'startTime': "Alternatively Move Start Time back"})
        elif conflicts == 2:
            EventCreationFormValidator.add_messages(event_form, {'startTime': "Start Time is During another event"}, {'startTime': "Remember a buffer of " + str(Event.APP_BUFFER.seconds / 60) + " Minuets is required between Appointments"})


        return render(request, 'user/eventhandle.html', {'form': event_form, 'user': user})


    def handle_nurse(self, request, user, event_form):

        event = event_form.getModel()
        conflicts = event.conflicts()

        if conflicts == 0:
            event.save()
            return HttpResponseRedirect(reverse('user:dashboard'))
        elif conflicts == 1:
            EventCreationFormValidator.add_messages(event_form, {'endTime': "End Time is during another event"},
                                                    {'startTime': "Consider shifting your event back",
                                                     'endTime': "Remember a buffer of " +
                                                     str(Event.APP_BUFFER.seconds/60) +
                                                     " Minuets is required between Appointments"})
        elif conflicts == 2:
            EventCreationFormValidator.add_messages(event_form, {'startTime': "Start Time is During another event"},
                                                    {'startTime': "Remember a buffer of " +
                                                    str(Event.APP_BUFFER.seconds/60) +
                                                    " Minuets is required between Appointments"})
        return render(request, 'user/eventhandle.html', {'form': event_form, 'user': user})



    def handle_doctor(self, request, user, event_form):
        event = event_form.getModel()
        event.doctor = user

        conflicts = event.conflicts()

        if conflicts == 0:
            event.save()
            return HttpResponseRedirect(reverse('user:dashboard'))

        elif conflicts == 1:
            EventCreationFormValidator.add_messages(event_form, {'endTime': "Event extends into another",
                                                            'startTime': "Alternatively Move Start Time back"})

        elif conflicts == 2:
            EventCreationFormValidator.add_messages(event_form, {'startTime': "Start Time is During another event"},
                                                    {'startTime': "Remember a buffer of " +
                                                            str(Event.APP_BUFFER.seconds/60) +
                                                            " Minuets is required between Appointments"})

        return render(request, 'user/eventhandle.html', {'form': event_form, 'user': user})



    def get(self, request):
        user = get_user_or_404(request, ("patient", "doctor", "nurse"))

        event = getEventFormByUserType(user.getType())

        if user.getType() == 'doctor':
            event.set_hospital_patient_queryset(user.hospitals.all(), user.patient_set.all())
        if user.getType() == 'nurse':
            event.set_patient_doctor_queryset(user.hospital.patient_set.all(), user.hospital.doctor_set.all())

        return render(request, 'user/eventhandle.html', {'form': event, 'user': user})


    def post(self, request):
        user = get_user_or_404(request, ("patient", "doctor", "nurse"))

        event = getEventFormByUserType(user.getType(), request=request)

        if not event.is_valid():
            return render(request, 'user/eventhandle.html', {'form': event, 'user': user})

        call = getattr(self, "handle_" + user.getType())
        return call(request, user, event)


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


    return render(request, 'user/dashboard.html', context)