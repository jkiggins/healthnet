from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, Http404
from syslogging.models import *
from .forms import *
from django.views.generic import View
from logIn.models import *
from .formvalid import *
from django.contrib.auth import logout
from .formhelper import *
from .viewhelper import *
from .userauth import *


#This method determines which type of user is using the app
#It will display the main page depending on which user is active


def patientList(request):
    patientList = request.session['user'].patient_set.all()

    return render(request , 'user/userList.html' , patientList)


def viewProfile(request , ut, pk):
    cuser = get_user(request)

    if cuser is None:
        return HttpResponseRedirect(reverse('login'))

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



    return render(request, 'user/viewprofile.html', {'user': user, 'trusted': trusted, 'events': getVisibleEvents(user).order_by('startTime')})


class EditProfile(View):

    def post(self, request):
        user = get_user(request)

        if user is None:
            return HttpResponseRedirect(reverse('login'))

        form = EditProfileForm(request.POST)

        if form.is_valid():
            form.save_user(user)
            Syslog.editProfile(user)
            return HttpResponseRedirect(reverse('user:dashboard'))
        else:
            return HttpResponseRedirect(reverse('user:eProfile'))

    def get(self, request):
        user = get_user(request)
        if user is None:
            return HttpResponseRedirect(reverse('login'))

        form = EditProfileForm()
        form.set_defaults(user)

        return render(request, 'user/editprofile.html', {'user': user, 'form': form})


class ViewEditEvent(View):

    def post(self, request, pk):
        user = get_user(request)
        if user is None:
            return HttpResponseRedirect(reverse('login'))

        old_event = get_visible_event_or_404(pk)

        event_form = getEventFormByUserType(user.getType(), data=request.POST, mode='update')

        if event_form.is_valid():
            if deleteInPostIsTrue(request.POST):
                old_event.visible = False
                old_event.save()
                return HttpResponseRedirect(reverse('user:dashboard'))

            new_event = event_form.getModel()
            updateEventFromModel(old_event, new_event)

            if addEventConflictMessages(event_form, old_event):
                old_event.save()
                return HttpResponseRedirect(reverse('user:dashboard'))

        context = {'form': event_form, 'event': old_event, 'user': user}

        elevate_if_trusted_event(event_form, user, old_event)
        return render(request, 'user/eventdetail.html', context)


    def get(self, request, pk):
        event = get_visible_event_or_404(pk)

        user = get_user(request)
        if user is None or not userCan_Event(user, event, 'viewedit'):
            return HttpResponseRedirect(reverse('login'))

        form = getEventFormByUserType(user.getType())
        setEventFormFromModel(form, event)
        context = {'form': form, 'event': event, 'user': user}

        elevate_if_trusted_event(form, user, event)
        return render(request, 'user/eventdetail.html', context)

    @staticmethod
    def post_dependant_fields(request, pk):
        event = get_visible_event_or_404(pk)
        if request.method == 'POST':
            user = get_user(request)
            if user is None:
                return HttpResponseRedirect(reverse('login'))

            event_form = getEventFormByUserType(user.getType(), data=request.POST, mode='update')

            if event_form.full_clean():
                populate_dependant_fields(event_form, user)

            elevate_if_trusted(event_form, user)
            return render(request, 'user/eventdetail.html', {'form': event_form, 'user': user, 'event': event})
        else:
            return HttpResponseRedirect(reverse('user:veEvent', args=(pk,)))


class CreateEvent(View):

    def process_patient(self, user, event, form):
        print(user)
        add_dict_to_model({'patient': user, 'doctor': user.doctor, 'hospital': user.hospital, 'appointment': True}, event)

    def process_nurse(self, user, event, form):
        if not(form.cleaned_data['patient'] is None):
            add_dict_to_model({'hospital': form.cleaned_data['patient'].hospital, 'appointment': True}, event)

    def process_doctor(self, user, event):
        pass

    def get(self, request):
        user = get_user(request)
        if user is None:
            return HttpResponseRedirect(reverse('login'))

        event = getEventFormByUserType(user.getType())

        if user.getType() == 'doctor':
            event.set_hospital_patient_queryset(user.hospitals.all(), user.patient_set.all())
        elif user.getType() in ['nurse', 'hadmin']:
            event.set_patient_doctor_queryset(user.hospital.patient_set.all(), user.hospital.doctor_set.all())

        return render(request, 'user/eventhandle.html', {'form': event, 'user': user})


    def post(self, request):
        user = get_user(request)
        if user is None:
            return HttpResponseRedirect(reverse('login'))

        event_form = getEventFormByUserType(user.getType(), request=request)

        # Check For Timing Conflicts
        if event_form.is_valid():
            event = event_form.getModel()

            call = getattr(self, 'process_'+user.getType())
            call(user, event, event_form)

            if addEventConflictMessages(event_form, event):
                event.save()
                return HttpResponseRedirect(reverse('user:dashboard'))

        elevate_if_trusted(event_form, user)
        return render(request, 'user/eventhandle.html', {'form': event_form, 'user': user})

    @staticmethod
    def post_dependant_fields(request):
        if request.method == 'POST':
            user = get_user(request)
            if user is None:
                return HttpResponseRedirect(reverse('login'))

            event_form = getEventFormByUserType(user.getType(), data=request.POST)

            if event_form.full_clean():
                populate_dependant_fields(event_form, user)

            elevate_if_trusted(event_form, user)
            return render(request, 'user/eventhandle.html', {'form': event_form, 'user': user})
        else:
            return HttpResponseRedirect(reverse('user:cEvent'))


def dashboardView(request):
    user = get_user(request)
    if user is None:
        if request.user.is_authenticated():
            return HttpResponseRedirect(reverse('admin:index'))
        else:
            return HttpResponseRedirect(reverse('login'))

    context = {'user': user}

    if(user.getType() != "nurse"):
        events = getVisibleEvents(user).order_by('startTime')
        context['events'] = events
    elif(user.getType() == "doctor"):
        context['patients'] = user.patient_set.all()
        context['hosptials'] = user.hospitals.all()
    elif(user.getType() == "nurse"):
        context['patients'] = user.hospital.patient_set.all()
        context['doctors'] = user.hospital.doctor_set.all()


    return render(request, 'user/dashboard.html', context)