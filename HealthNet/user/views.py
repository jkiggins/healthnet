import HealthNet.userauth as userauth
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.views.generic import View
from HealthNet.formhelper import *
from HealthNet.viewhelper import *
from django.core.exceptions import ValidationError


from HealthNet.formhelper import *
from HealthNet.viewhelper import *
from .forms import *
from syslogging.models import *

import json


class Registry(View):

    def filterByUser(self, user, qset):
        if user.getType() == "nurse":
            return qset.filter(hospital=user.hospital)
        elif user.getType() == 'doctor':
            qbuild = None
            for hospital in user.hospitals.all():
                qbuild |= qset.filter(hospital=hospital)

            return qbuild


    def post(self, request):
        cuser = get_user(request)
        if cuser is None:
            return HttpResponseRedirect(reverse('login'))

        pqset = None
        dqset = None
        evqset = None

        if cuser.getType() == "hosAdmin":
            form = HosAdminSearchForm(request.POST)
            form.full_clean()
        else:
            form = SearchForm(request.POST)
            form.full_clean()


        words = form.cleaned_data['keywords'].split(' ')
        patients = Patient.objects.none()
        doctors = Doctor.objects.none()
        events = Event.objects.none()

        if 'patient' in form.cleaned_data['filterBy']:
            if cuser.getType() != 'doctor':
                pqset = cuser.hospital.acceptedPatients()
            else:
                pqset = cuser.acceptedPatients()
            for word in words:
                patients |= pqset.filter(user__first_name__contains=word)
                patients |= pqset.filter(user__last_name__contains=word)
                patients |= pqset.filter(hospital__name__contains=word)

        if 'doctor' in form.cleaned_data['filterBy']:
            dqset = cuser.hospital.doctor_set.filter(user__is_active=True).filter(accepted=True)
            for word in words:
                doctors |= dqset.filter(user__first_name__contains=word)
                doctors |= dqset.filter(user__last_name__contains=word)

        if 'event' in form.cleaned_data['filterBy']:
            evqset = Event.objects.filter(visible=True)
            for word in words:
                events |= evqset.filter(doctor__user__first_name__contains=word)
                events |= evqset.filter(patient__user__last_name__contains=word)
                events |= evqset.filter(patient__user__first_name__contains=word)
                events |= evqset.filter(doctor__user__last_name__contains=word)
                events |= evqset.filter(title__contains=word)
                events |= evqset.filter(description__contains=word)

        if cuser.getType() == "hosAdmin":
            pendingdoc = Doctor.objects.none()
            pendingnur = Nurse.objects.none()
            pendingdoctor = cuser.hospital.doctor_set.filter(user__is_active=True).filter(accepted=False)
            pendingnurse = cuser.hospital.nurse_set.filter(user__is_active=True).filter(accepted=False)
            if 'pending' in form.cleaned_data['filterBy']:
                for word in words:
                    pendingdoc |= pendingdoctor.filter(user__first_name__contains=word)
                    pendingdoc |= pendingdoctor.filter(user__last_name__contains=word)
                    pendingnur |= pendingnurse.filter(user__first_name__contains=word)
                    pendingnur |= pendingnurse.filter(user__last_name__contains=word)
                    pendingnur |= pendingnurse.filter(hospital__name__contains=word)

            nurse = Nurse.objects.none()
            nurses = cuser.hospital.nurse_set.filter(user__is_active=True).filter(accepted=True)
            if 'nurse' in form.cleaned_data['filterBy']:
                for word in words:
                    nurse |= nurses.filter(user__first_name__contains=word).filter(accepted=True)
                    nurse |= nurses.filter(user__last_name__contains=word).filter(accepted=True)
                    nurse |= nurses.filter(hospital__name__contains=word).filter(accepted=True)

        results = getResultsFromModelQuerySet(patients) + getResultsFromModelQuerySet(doctors) \
                    + getResultsFromModelQuerySet(events)


        if cuser.getType() == "hosAdmin":
            results += getResultsFromModelQuerySet(pendingdoc)
            results += getResultsFromModelQuerySet(pendingnur)
            results += getResultsFromModelQuerySet(nurse)


        if cuser.getType() == "hosAdmin":
            return render(request, 'user/registry.html', {'user': cuser, 'results': results, 'search_form': form})
        else:
            return render(request, 'user/registry.html', {'user': cuser, 'results': results, 'search_form': form})


    def get(self, request):
        cuser = get_user(request)
        if cuser is None:
            return HttpResponseRedirect(reverse('login'))

        if not userauth.userCan_Registry(cuser, 'view'):
            return reverse('user:dashboard')

        if cuser.getType() == "hosAdmin":
            form = HosAdminSearchForm()
            return render(request, 'user/registry.html', {'search_form': form, 'user': cuser})
        else:
            form = SearchForm()
            return render(request, 'user/registry.html', {'search_form': form, 'user': cuser})


def viewProfileSelf(request):
    cuser = get_user(request)
    if cuser is None:
        return HttpResponseRedirect(reverse('login'))

    if (cuser.getType() == 'patient') and not userauth.userCan_Profile(cuser, cuser, 'view'):
        return HttpResponseRedirect(reverse('user:eProfile' , args={cuser.user.pk}))
    else:
        if cuser.getType() == "nurse":
            context = {'user': cuser,
                       'tuser': cuser,
                       'trustdocs': cuser.doctor_set.all().filter(user__is_active=True).filter(accepted=True),
                       'events': None,
                       'view_calendar': False}
        elif cuser.getType() == "hosAdmin":
            context = {'user': cuser,
                       'tuser': cuser}
        else:
            context = {'user': cuser,
                       'tuser': cuser,
                       'events': getVisibleEvents(cuser),
                       'view_calendar': True}
        return render(request, 'user/viewprofile.html', context)


def viewProfile(request, pk):
    if request.method == "POST":

        user = get_user(request)

        if user is None:
            return HttpResponseRedirect(reverse('login'))

        tuser = get_object_or_404(User, pk=pk)
        tuser = getHealthUser(tuser)

        trustform = TrustedNurses(request.POST)
        trustform.setQuerySet(user.hospital.doctor_set.all().filter(accepted=True).exclude(pk__in = tuser.doctor_set.all()))
        print("hello")
        if trustform.is_valid():
            print("valid")
            if trustform.cleaned_data['docs']:
                trustform.cleaned_data['docs'].nurses.add(tuser)

        return HttpResponseRedirect(reverse('user:vProfile', args=(pk,)))
    else:
        print("hi")
        user = get_user(request)
        tuser = None

        if user is None:
            return HttpResponseRedirect(reverse('login'))


        tuser = get_object_or_404(User, pk=pk)
        tuser = getHealthUser(tuser)

        if not userauth.userCan_Profile(user, tuser, 'view'):
            return HttpResponseRedirect(reverse('user:dashboard'))

        if user.user.pk == tuser.user.pk:
            return HttpResponseRedirect(reverse('user:vProfilec'))

        if tuser.getType() == 'nurse':
            if tuser.accepted:
                if user.getType() == "hosAdmin":
                    trustform = TrustedNurses()
                    trustform.setQuerySet(user.hospital.doctor_set.all().filter(accepted=True).exclude(pk__in = tuser.doctor_set.all()))
                else:
                    trustform = None

        if user.getType() == "hosAdmin":
            if tuser.getType() == "nurse":
                if tuser.accepted:
                    context = {'user': user,
                        'tuser': tuser,
                        'trustdocs': tuser.doctor_set.all().filter(user__is_active=True).filter(accepted=True),
                        'events': None,
                        'view_calendar': False,
                        'trustform': trustform,
                        'accepted': True}
                else:
                    context = {'user': user,
                        'tuser': tuser,
                        'trustdocs': tuser.doctor_set.all().filter(user__is_active=True).filter(accepted=True),
                        'events': None,
                        'view_calendar': False,
                        'accepted': False}
            elif tuser.getType() == "doctor":
                if tuser.accepted:
                    context = {'user': user,
                        'tuser': tuser,
                        'events': getVisibleEvents(tuser),
                        'view_calendar': True,
                        'accepted': True}
                else:
                    context = {'user': user,
                        'tuser': tuser,
                        'events': getVisibleEvents(tuser),
                        'view_calendar': True,
                        'accepted': False}
            else:
                context = {'user': user,
                    'tuser': tuser,
                    'events': getVisibleEvents(tuser),
                    'view_calendar': True}
        else:
            if tuser.getType() == "nurse":
                context = {'user': user,
                    'tuser': tuser,
                    'trustdocs': tuser.doctor_set.all().filter(user__is_active=True).filter(accepted=True),
                    'events': None,
                    'view_calendar': False}
            else:
                context = {'user': user,
                    'tuser': tuser,
                    'events': getVisibleEvents(tuser),
                    'view_calendar': True}

        return render(request, 'user/viewprofile.html', context)


def approval(request, pk):

    user = get_object_or_404(User, pk=pk)
    user = getHealthUser(user)

    user.accepted = not user.accepted

    if not user.accepted and user.getType()=='doctor':
        user.event_set.all().delete()
        for p in user.patient_set.all():
            p.accepted=False
            p.doctor=None
            p.hospital=None
            p.save()
            Notification.push(p.user, "Your doctor no longer is active. Change doctors", "", 'user:eProfile,{0}'.format(p.user.pk))
        user.nurses = Nurse.objects.none()
    elif not user.accepted and user.getType()=='nurse':
        user.doctor_set.clear()


    user.save()

    return HttpResponseRedirect(reverse('user:vProfile', args=(pk,)))

# class viewProfile(View):
#
#     def post(self, request, **kwargs):
#         tuser = None
#         cuser = get_user(request)
#         if cuser is None:
#             return HttpResponseRedirect(reverse('login'))
#
#         tuser = get_object_or_404(User, pk=kwargs['pk'])
#         tuser = getHealthUser(tuser)
#
#         if not userauth.userCan_Profile(cuser, tuser, 'view'):
#             Syslog.unauth_acess(request)
#             request.session['message']="You are not authorized to view this content."
#             return HttpResponseRedirect(reverse('user:dashboard'))
#             #message = "You are not authorized to view this content."
#             #return render(request, 'user/dashboard.html', {'message': message})
#
#         if cuser.user.pk == tuser.user.pk:
#             return HttpResponseRedirect(reverse('user:vProfilec'))
#
#         if getTypeOfForm(request) == 1:
#             if tuser.accepted:
#                 removeform = RemoveApproval(request.POST)
#                 if removeform.is_valid():
#                     if removeform.cleaned_data['remove']:
#                         tuser.accepted = False
#                         tuser.save()
#                         tuser.user.is_active = False
#                         tuser.user.save()
#                     else:
#                         tuser.user.is_active = True
#                         tuser.user.save()
#                 return HttpResponseRedirect(reverse('user:dashboard'))
#             else:
#                 approveform = ApproveForm(request.POST)
#                 if approveform.is_valid():
#                     if approveform.cleaned_data['approved']:
#                         tuser.accepted = True
#                         tuser.save()
#                     else:
#                         if tuser.getType() != 'patient':
#                             tuser.accepted = False
#                             tuser.save()
#
#                 return HttpResponseRedirect(reverse('user:dashboard'))
#
#         elif getTypeOfForm(request) == 2:
#             trustform = TrustedNurses(request.POST)
#             if trustform.is_valid():
#                 if trustform.cleaned_data['docs']:
#                     trustform.cleaned_data['docs'].nurses.add(tuser)
#
#             return HttpResponseRedirect(reverse('user:dashboard'))
#
#         return HttpResponseRedirect(reverse('user:dashboard'))
#
#
#     def get(self, request, **kwargs):
#         tuser=None
#         form = None
#         cuser = get_user(request)
#         if cuser is None:
#             return HttpResponseRedirect(reverse('login'))
#
#         tuser = get_object_or_404(User, pk=kwargs['pk'])
#         tuser = getHealthUser(tuser)
#
#
#         if not userauth.userCan_Profile(cuser, tuser, 'view'):
#             Syslog.unauth_acess(request)
#             return HttpResponseRedirect(reverse('user:dashboard'))
#
#         if cuser.user.pk == tuser.user.pk:
#             return HttpResponseRedirect(reverse('user:vProfilec'))
#
#         if tuser.getType() == 'doctor' or tuser.getType() == 'nurse':
#             if tuser.accepted:
#                 if cuser.getType() == "hosAdmin":
#                     trustform = TrustedNurses()
#                     trustform.setQuerySet(cuser.hospital.doctor_set.all())
#                 form = RemoveApproval()
#             else:
#                 trustform = None
#                 form = ApproveForm()
#         elif tuser.getType() == 'patient':
#             form = RemoveApproval()
#
#         if cuser.getType() == "hosAdmin":
#             if tuser.getType() == "nurse":
#                 if tuser.accepted:
#                     context = {'user': cuser,
#                         'tuser': tuser,
#                         'trustdocs': tuser.doctor_set.all().filter(user__is_active=True).filter(accepted=True),
#                         'events': None,
#                         'view_calendar': False,
#                         'trustform': trustform,
#                         'form': form}
#                 else:
#                     context = {'user': cuser,
#                         'tuser': tuser,
#                         'trustdocs': tuser.doctor_set.all().filter(user__is_active=True).filter(accepted=True),
#                         'events': None,
#                         'view_calendar': False,
#                         'form': form}
#             elif tuser.getType() == "doctor":
#                 context = {'user': cuser,
#                     'tuser': tuser,
#                     'events': None,
#                     'view_calendar': False,
#                     'form': form}
#             else:
#                 context = {'user': cuser,
#                     'tuser': tuser,
#                     'events': None,
#                     'view_calendar': True,
#                     'form': form}
#         else:
#             if tuser.getType() == "nurse":
#                 context = {'user': cuser,
#                     'tuser': tuser,
#                     'trustdocs': tuser.doctor_set.all().filter(user__is_active=True).filter(accepted=True),
#                     'events': None,
#                     'view_calendar': False}
#             else:
#                 context = {'user': cuser,
#                     'tuser': tuser,
#                     'events': None,
#                     'view_calendar': True}
#
#         return render(request, 'user/viewprofile.html', context)

def editProfile(request, pk):

    if not request.method == "POST":
        user = get_user(request)
        tuser = None

        if user is None:
            return HttpResponseRedirect(reverse('login'))


        tuser = get_object_or_404(User, pk=pk)
        tuser = getHealthUser(tuser)

        if not userauth.userCan_Profile(user, tuser, 'edit'):
            return HttpResponseRedirect(reverse('user:dashboard'))

        form = EditProfileForm()
        form.filterUserQuerySet(user)

        setEditFormDefault(tuser, form)

        return render(request, 'user/editprofile.html', {'user': user, 'tuser': tuser, 'form': form})
    else:
        user = get_user(request)
        if user is None:
            return HttpResponseRedirect(reverse('login'))

        form = EditProfileForm(request.POST)

        # turns true if the form fails
        failed = False

        if form.is_valid():
            tuser = get_object_or_404(User, pk=pk)
            tuser = getHealthUser(tuser)
            updateUserProfile(form, tuser)
            Syslog.editProfile(user)
            return HttpResponseRedirect(reverse('user:vProfilec'))
        else:
            failed = True

        if failed:
            return render(request, 'user/editprofile.html', {'form': form})


def getEventTitle(event):
    title = "Event Details"
    if not (event.patient is None):
        title = "Appointment Details"

    return title


def editEvent(request, pk, depend=False):
    user = get_user(request)
    if user is None:
        return HttpResponseRedirect(reverse('login'))
    event = get_object_or_404(Event, pk=pk)
    if not userauth.userCan_Event(user, event, 'edit'):
        return unauth(request)

    event_form = None

    if isPatient(user):
        if request.method == "POST":
            event_form = EventCreationFormPatient(data=request.POST, instance=event)
        else:
            event_form = EventCreationFormPatient(instance=event)
    elif isDoctor(user):
        if request.method == "POST":
            if depend:
                #AJAX response
                event_form.set_hospital_patient_queryset(user.hospitals.all(), user.acceptedPatients())
                event_form.full_clean()
                populateDependantFieldsPH(event_form, user.acceptedPatients(), user.hospitals.all())
                return render(request, 'user/render_form.html', {'form': event_form})
            else:
                event_form = EventCreationFormDoctor(data=request.POST, instance=event)
        else:
            event_form = EventCreationFormDoctor(instance=event)

        event_form.set_hospital_patient_queryset(user.hospitals.all(), user.patient_set.all())

    elif isNurse(user):
        if request.method == "POST":
            if depend:
                # Handle ajax post
                event_form.set_patient_doctor_queryset(user.hospital.acceptedPatients(), user.hospital.doctor_set.all())
                event_form.full_clean()
                populateDependantFieldsPD(event_form, user.hospital.acceptedPatients(), user.hospital.doctor_set.all(), user.hospital)
                return render(request, 'user/render_form.html', {'form': event_form})
            else:
                event_form = EventCreationFormNurse(data=request.POST, instance=event)

            if not (event_form.cleaned_data['doctor'] is None):
                if user in event_form.cleaned_data['doctor'].nurses:
                    event_form.elevated = True
        else:
            event_form = EventCreationFormNurse(instance=event)

        event_form.set_patient_doctor_queryset(user.hospital.patient_set.all(), user.hospital.doctor_set.all())


    if request.method == "POST":
        event_form.full_clean()

        if event_form.is_valid():

            new_event = event_form.save(commit=False)

            if addEventConflictMessages(event_form, new_event):
                new_event.save()
                Syslog.modifyEvent(new_event, user)
                return HttpResponseRedirect(reverse('user:dashboard'))


    return render(request, 'user/eventdetail.html', getBaseContext(request, user, form=event_form, event=event, title=getEventTitle(event)))


def viewEvent(request, pk):
    user = get_user(request)
    if user is None:
        return HttpResponseRedirect(reverse('login'))

    event = get_object_or_404(Event, pk=pk)

    if userauth.userCan_Event(user, event, 'view'):

        permissions = {'can_edit': userauth.userCan_Event(user, event, 'edit'),
                       'can_cancle': userauth.userCan_Event(user, event, 'cancle')}


        return render(request, 'user/eventdetail.html', getBaseContext(request, user, permissions=permissions, title=getEventTitle(event), event=event))
    else:
        return unauth(request)


def createEvent(request, depend=False):
    user = get_user(request)
    if user is None:
        return unauth(request)
    elif not userauth.userCan_Event(user, None, 'create'):
        pass
    process_event = False
    d = timezone.now().replace(hour=6, minute=0) + datetime.timedelta(days=1)

    if request.method == "POST":
        if 'json' in request.POST:
            jdict = json.loads(request.POST['json'])
            d = datetime.datetime.strptime(jdict['moment'], "%Y-%m-%dT%H:%M:%S");
        else:
            process_event = True


    event_form = None
    my_events = None
    other_events = None
    title="Create a new Event or Appointment"

    if isPatient(user):

        my_events = getVisibleEvents(user)

        if process_event:
            event_form = EventCreationFormPatient(request.POST)
            if event_form.is_valid():
                event = event_form.save(commit=False)
                add_dict_to_model({'patient': user, 'doctor': user.doctor, 'hospital': user.hospital, 'appointment': True},
                              event)

                if addEventConflictMessages(event_form, event):
                    event.save()
                    request.session['message'] = "Event created successfully."
                    Syslog.createEvent(event, user)
                    return HttpResponseRedirect(reverse('user:dashboard'))
        else:
            event_form = EventCreationFormPatient()

        my_events = getVisibleEvents(user)
        other_events = user.doctor.event_set.all()
        title = "Create a new Appointment with DR {0}".format(user.doctor.user.get_full_name())


    elif isDoctor(user):
        if process_event:
            event_form = EventCreationFormDoctor(request.POST)

            if depend:
                #AJAX response
                event_form.set_hospital_patient_queryset(user.hospitals.all(), user.acceptedPatients())
                event_form.full_clean()
                populateDependantFieldsPH(event_form, user.acceptedPatients(), user.hospitals.all())
                return render(request, 'user/render_form.html', {'form': event_form})

            elif event_form.is_valid():
                event = event_form.save(commit=False)

                event.doctor = user
                event.appointment = not (event_form.cleaned_data['patient'] is None)

                if addEventConflictMessages(event_form, event):
                    event.save()
                    request.session['message'] = "Event created successfully."
                    Syslog.createEvent(event, user)
                    return HttpResponseRedirect(reverse('user:dashboard'))
        else:
            event_form = EventCreationFormDoctor()
            event_form.set_hospital_patient_queryset(user.hospitals.all(), user.acceptedPatients())

        my_events = getVisibleEvents(user)


    elif isNurse(user) or isHosadmin(user):
        if process_event:
            event_form = EventCreationFormNurse(request.POST)

            if depend:
                # Handle ajax post
                event_form.set_patient_doctor_queryset(user.hospital.acceptedPatients(), user.hospital.doctor_set.all())
                event_form.full_clean()
                populateDependantFieldsPD(event_form, user.hospital.acceptedPatients(), user.hospital.doctor_set.all(), user.hospital)
                return render(request, 'user/render_form.html', {'form': event_form})

            elif event_form.is_valid():
                event = event_form.save(commit=False)

                if not (event_form.cleaned_data['patient'] is None):
                    add_dict_to_model({'hospital': event_form.cleaned_data['patient'].hospital, 'appointment': True}, event)

                if addEventConflictMessages(event_form, event):
                    event.save()
                    request.session['message'] = "Event created successfully."
                    Syslog.createEvent(event, user)
                    return HttpResponseRedirect(reverse('user:dashboard'))
        else:
            event_form = EventCreationFormNurse()
            event_form.set_patient_doctor_queryset(user.hospital.acceptedPatients(), user.hospital.doctor_set.all())

    # TODO: hosAdmin

    event_form.setStart(d)

    ctx = getBaseContext(request, user, otherEvents=other_events, events=my_events, form=event_form, title=title)

    return render(request, 'user/eventhandle.html', ctx)


def cancleEvent(request, pk):
    user = get_user(request)
    event = get_object_or_404(Event, pk=pk)
    if user is None:
        return unauth(request)
    elif not userauth.userCan_Event(user, event, 'cancle'):
        return unauth(request)

    event.visible = False
    event.save()

    return HttpResponseRedirect(reverse('user:dashboard'))


def dashboardView(request):
    user = get_user(request)
    if user is None:
        if request.user.is_authenticated():
            return HttpResponseRedirect(reverse('admin:index'))
        else:
            return HttpResponseRedirect(reverse('login'))

    context = {'user': user}


    if isPatient(user):
        context['events'] = getVisibleEvents(user).order_by('startTime')
        if user.accepted:
            context['other_events'] = user.doctor.event_set.all().order_by('startTime')
            context['calendarView'] = "month"
    elif(user.getType() == "doctor"):
        context['patients'] = user.patient_set.all()
        context['hosptials'] = user.hospitals.all()
        context['events'] = getVisibleEvents(user).order_by('startTime')
        context['calendarView'] = "agendaDay"
    elif(user.getType() == "nurse"):
        return HttpResponseRedirect(reverse('user:nurseDash'))
    elif(user.getType() == "hosAdmin"):
        return HttpResponseRedirect(reverse('user:hosDash', args={user.user.pk}))

    context['tuser'] = user #TODO: Remove once nurse has searchable columns
    context['title'] = "Dashboard"
    if ('message' in request.session):
        message = request.session.pop('message')
        context['message'] = message
    return render(request, 'user/dashboard.html', context)


def nurseDashView(request):
    user = get_user(request)

    if user is None:
        if request.user.is_authenticated():
            return HttpResponseRedirect(reverse('admin:index'))
        else:
            return HttpResponseRedirect(reverse('login'))

    context = {'user': user}
    context['trustdocs'] = user.doctor_set.all().filter(accepted=True)
    context['patients'] = user.hospital.patient_set.all().filter(hospital=user.hospital)
    context['title'] = "Dashboard"
    return render(request, 'user/dashboard.html', context)

def hosAdDashView(request, pk):
    user = get_user(request)

    if user is None:
        if request.user.is_authenticated():
            return HttpResponseRedirect(reverse('admin:index'))
        else:
            return HttpResponseRedirect(reverse('login'))

    tuser = get_object_or_404(User, pk=pk)
    tuser = getHealthUser(tuser)

    context = {'user': user}
    if not isHosadmin(tuser) and not isNurse(tuser):
        context['events'] = getVisibleEvents(tuser).order_by('startTime')
    context['patients'] = user.hospital.patient_set.all().filter(hospital=user.hospital)
    context['doctors'] = user.hospital.doctor_set.all().filter(accepted=True).filter(hospitals=user.hospital)
    context['nurses'] = user.hospital.nurse_set.all().filter(accepted=True).filter(hospital=user.hospital)
    context['admittedpatients'] = user.hospital.patient_set.all().filter(emrprofile__admit_status=True)
    context['search_form'] = HosAdminSearchForm()
    context['tuser'] = user
    context['title'] = "Dashboard"
    context['calendarView'] = "agendaWeek"
    context['key'] = pk
    context['hospital'] = user.hospital
    return render(request, 'user/dashboard.html', context)


def dismissNote(request, pk):
    user = get_user(request)
    if user is None:
        return HttpResponse("Access Denied")

    obj = get_object_or_404(Notification, pk=pk)
    obj.delete()

    return HttpResponse("EMPTY")


def viewNote(request, pk):
    user = get_user(request)
    if user is None:
        return HttpResponse("Access Denied")

    note = get_object_or_404(Notification, pk=pk)
    url = note.link.split(',')

    redir = None

    try:
        redir = reverse(url[0], args=tuple(url[1:]))
    except NoReverseMatch:
        if 'HTTP_REFERER' in request.META:
            redir = request.META['HTTP_REFERER']
        else:
            redir = reverse('user:dashboard')

    return HttpResponseRedirect(redir)


class sendMessage(View):


    def get(self, request):
        """ displays a messaging page """

        form = messagingForm()
        currentUser = get_user(request)

        if not userauth.userCanMessage(currentUser):
            return HttpResponseRedirect(reverse('user:dashboard'))

        form.staff_queryset(User.objects.all().exclude(username=currentUser.user.username).filter(patient=None))
        # all_users = #ONLY ONES WHO CAN MESSAGE
        context = {'user': currentUser,
                   'messaging_form': form,
                   'title': 'Send Another Health Care Professional A Message:'}

        return render(request, 'user/sendMessage.html', context)

    def post(self, request):
        """ sends a message generates a notification"""
        currentUser = get_user(request)
        form = messagingForm(request.POST)
        form.staff_queryset(User.objects.all().exclude(username=currentUser.user.username).filter(patient=None))

        if not form.is_valid():
            return HttpResponseRedirect(reverse('user:sendMessage'))
        form.full_clean()
        recipient = form.cleaned_data['userTO']
        message = form.cleaned_data['messageContent']
        sentdialog = 'Message to '+ recipient.first_name +" sent successfully!"
        namesender = currentUser.user.get_full_name()
        #Generate/Push Notification
        n = Notification.push(recipient, "New Message from: " + namesender, message, '') # TODO WILL NEED A PK IN THE URL
        n.link = 'user:viewMessage,'+ str(n.pk)
        n.save()

        #system log of message
        Syslog.sentmessage(currentUser,recipient,message)

        context = {'user': currentUser,
                   'messaging_form': form,
                   'title': 'Message Sent!',
                   'recipient': recipient.first_name, # remove
                   'message': sentdialog
                   }
        # also syslog item with from, to, time, and content
        return render(request, 'user/sendMessage.html', context)


def viewMessage(request, pk):

    notification = get_object_or_404(Notification, pk=pk)
    message = notification.content
    sender = notification.title
    context = {'user': get_user(request),
               'from': sender,
               'messagetext': message}

    return render(request, 'user/viewMessage.html', context)


def viewStats(request):
    """
        number of patients visiting the hospital
        average number of visits per patient
        average length of stay (from admission to discharge)
        most common reasons for being admitted to the hospital
        prescription statistics
    """
    user = get_user(request)
    if user is None:
        return unauth(request, "You must be logged in to view this page")
    if not userauth.userCan_stats(user, 'view'):
        return unauth(request, "You must be a Nurse, Doctor, or Hospital Administrator to view this page")

    form = None
    if request.method == "POST":
        form = statsForm(request.POST)
        if form.is_valid():
            resolution = 10
            start = form.cleaned_data['start']
            end = form.cleaned_data['end']
            kw = form.cleaned_data['keywords']

            pstats = [{}]
            if isDoctor(user):
                for p in user.patients.all():
                    visits = p.event_set.all().filter(starttime__geq=start, starttime__leq=end).count
                    admission = p.emritem_set.all().exclude(emradmitstatus=None).order_by('date_created')

                    # calculate average stay per patient
                    avg_stay=0
                    i = 0
                    while i < (len(avg_stay) / 2)*2:
                        avg_stay += admission(i+1).date_created - admission(i).date_created
                        i += 2
                    avg_stay /= len(admission)/2




                    visits += admission.filter(emradmitstatus__admit=True).count()
                    pstats.append({'patient': p})

    else:
        form = statsForm()

    return render(request, 'user/stats.html', getBaseContext(request, user, form=form, title="Statistics"))
