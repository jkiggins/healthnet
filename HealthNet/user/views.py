from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.views.generic import View
from .formhelper import *
from .viewhelper import *

import user.userauth as userauth


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

            print(pqset)

        if 'doctor' in form.cleaned_data['filterBy']:
            dqset = Doctor.objects.filter(user__is_active=True).filter(accepted=True)
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

            nurses = Nurse.objects.none()
            if 'nurse' in form.cleaned_data['filterBy']:
                for word in words:
                    nurses |= Nurse.objects.filter(user__first_name__contains=word).filter(accepted=True)
                    nurses |= Nurse.objects.filter(user__last_name__contains=word).filter(accepted=True)
                    nurses |= Nurse.objects.filter(hospital__name__contains=word).filter(accepted=True)

        results = getResultsFromModelQuerySet(patients) + getResultsFromModelQuerySet(doctors) \
                    + getResultsFromModelQuerySet(events)


        if cuser.getType() == "hosAdmin":
            results += getResultsFromModelQuerySet(pendingdoc)
            results += getResultsFromModelQuerySet(pendingnur)
            results += getResultsFromModelQuerySet(nurses)


        if cuser.getType() == "hosAdmin":
            return render(request, 'user/dashboard.html', {'user': cuser, 'results': results, 'search_form': form})
        else:
            return render(request, 'user/registry.html', {'user': cuser, 'results': results, 'search_form': form})


    def get(self, request):
        cuser = get_user(request)
        if cuser is None:
            return HttpResponseRedirect(reverse('login'))

        if not userauth.userCan_Registry(cuser, 'view'):
            return reverse('user:dashboard')

        form = SearchForm()

        if cuser.getType() == "hosAdmin":
            return render(request, 'user/dashboard.html', {'search_form': form, 'user': cuser})
        else:
            return render(request, 'user/registry.html', {'search_form': form, 'user': cuser})


def viewProfileSelf(request):
    cuser = get_user(request)
    if cuser is None:
        return HttpResponseRedirect(reverse('login'))

    if (cuser.getType() == 'patient') and not userauth.userCan_Profile(cuser, cuser, 'view'):
        return HttpResponseRedirect(reverse('user:eProfile'))
    else:
        return render(request, 'user/viewprofile.html', {'user': cuser, 'tuser': cuser})


class viewProfile(View):

    def post(self, request, **kwargs):
        tuser = None
        cuser = get_user(request)
        if cuser is None:
            return HttpResponseRedirect(reverse('login'))

        tuser = get_object_or_404(User, pk=kwargs['pk'])
        tuser = healthUserFromDjangoUser(tuser)

        if not userauth.userCan_Profile(cuser, tuser, 'view'):
            Syslog.unauth_acess(request)
            request.session['message']="You are not authorized to view this content."
            return HttpResponseRedirect(reverse('user:dashboard'))
            #message = "You are not authorized to view this content."
            #return render(request, 'user/dashboard.html', {'message': message})

        if cuser.user.pk == tuser.user.pk:
            return HttpResponseRedirect(reverse('user:vProfilec'))

        if getTypeOfForm(request) == 1:
            if tuser.accepted:
                removeform = RemoveApproval(request.POST)
                if removeform.is_valid():
                    if removeform.cleaned_data['remove']:
                        tuser.accepted = False
                        tuser.save()
                        tuser.user.is_active = False
                        tuser.user.save()
                    else:
                        tuser.user.is_active = True
                        tuser.user.save()
                return HttpResponseRedirect(reverse('user:dashboard'))
            else:
                approveform = ApproveForm(request.POST)
                if approveform.is_valid():
                    if approveform.cleaned_data['approved']:
                        tuser.accepted = True
                        tuser.save()
                    else:
                        if tuser.getType() != 'patient':
                            tuser.accepted = False
                            tuser.save()

                return HttpResponseRedirect(reverse('user:dashboard'))

        elif getTypeOfForm(request) == 2:
            trustform = TrustedNurses(request.POST)
            if trustform.is_valid():
                if trustform.cleaned_data['docs']:
                    trustform.cleaned_data['docs'].nurses.add(tuser)

            return HttpResponseRedirect(reverse('user:dashboard'))

        return HttpResponseRedirect(reverse('user:dashboard'))


    def get(self, request, **kwargs):
        tuser=None
        form = None
        cuser = get_user(request)
        if cuser is None:
            return HttpResponseRedirect(reverse('login'))

        tuser = get_object_or_404(User, pk=kwargs['pk'])
        tuser = healthUserFromDjangoUser(tuser)

        if not userauth.userCan_Profile(cuser, tuser, 'view'):
            Syslog.unauth_acess(request)
            return HttpResponseRedirect(reverse('user:dashboard'))

        if cuser.user.pk == tuser.user.pk:
            return HttpResponseRedirect(reverse('user:vProfilec'))

        if tuser.getType() == 'doctor' or tuser.getType() == 'nurse':
            if tuser.accepted:
                if cuser.getType() == "hosAdmin":
                    trustform = TrustedNurses()
                    trustform.setQuerySet(cuser.hospital.doctor_set.all())
                form = RemoveApproval()
            else:
                trustform = None
                form = ApproveForm()
        elif tuser.getType() == 'patient':
            form = RemoveApproval()

        if cuser.getType() == "hosAdmin":
            if tuser.getType() == "nurse":
                if tuser.accepted:
                    context = {'user': cuser,
                        'tuser': tuser,
                        'trustdocs': tuser.doctor_set.all().filter(user__is_active=True).filter(accepted=True),
                        'events': None,
                        'view_calendar': False,
                        'trustform': trustform,
                        'form': form}
                else:
                    context = {'user': cuser,
                        'tuser': tuser,
                        'trustdocs': tuser.doctor_set.all().filter(user__is_active=True).filter(accepted=True),
                        'events': None,
                        'view_calendar': False,
                        'form': form}
            elif tuser.getType() == "doctor":
                context = {'user': cuser,
                    'tuser': tuser,
                    'events': None,
                    'view_calendar': False,
                    'form': form}
            else:
                context = {'user': cuser,
                    'tuser': tuser,
                    'events': None,
                    'view_calendar': True,
                    'form': form}
        else:
            if tuser.getType() == "nurse":
                context = {'user': cuser,
                    'tuser': tuser,
                    'trustdocs': tuser.doctor_set.all().filter(user__is_active=True).filter(accepted=True),
                    'events': None,
                    'view_calendar': False}
            else:
                context = {'user': cuser,
                    'tuser': tuser,
                    'events': None,
                    'view_calendar': True}

        return render(request, 'user/viewprofile.html', context)


class EditProfile(View):

    @staticmethod
    def dependand_post(request, **kwargs):
        if request.method == "POST":
            user = get_user(request)
            tuser = None

            if user is None:
                return HttpResponseRedirect(reverse('login'))

            if 'pk' in kwargs:
                if kwargs['pk'] == user.pk:
                    return HttpResponseRedirect(reverse('user:eProfile'))
                else:
                    tuser = get_object_or_404(User, pk=kwargs['pk'])
                    tuser = healthUserFromDjangoUser(tuser)

                    if not userauth.userCan_Profile(user, tuser, 'edit'):
                        return HttpResponseRedirect('user:dashboard')
            else:
                tuser = user

            ctx = EditProfileHelper.getContextWithPopulatedForm(request.POST)

            ctx['form_medical'].full_clean()
            populateDependantFieldsDH(ctx['form_medical'], Doctor.objects.all(), Hospital.objects.all())

            ctx['user'] = user
            ctx['tuser'] = user

            return render(request, 'user/editprofile.html', ctx)



    def post(self, request, **kwargs):
        user = get_user(request)
        if user is None:
            return HttpResponseRedirect(reverse('login'))

        form = EditProfileHelper.getFormByPostData(request.POST)

        if form.is_valid():
            if 'pk' in kwargs:
                tuser = get_object_or_404(User, pk=kwargs['pk'])
                tuser = healthUserFromDjangoUser(tuser)
                EditProfileHelper.updateUserProfile(form, tuser)
                Syslog.editProfile(user)
                return HttpResponseRedirect(reverse('user:vProfile'), args=(kwargs['pk']))
            else:
                EditProfileHelper.updateUserProfile(form, user)
                Syslog.editProfile(user)
                return HttpResponseRedirect(reverse('user:vProfilec'))
        else:
            ctx = EditProfileHelper.getContextFromForm(form)
            return render(request, 'user/editprofile.html', ctx)


    def get(self, request, **kwargs):
        user = get_user(request)
        tuser = None

        if user is None:
            return HttpResponseRedirect(reverse('login'))

        if 'pk' in kwargs:
            if kwargs['pk'] == user.pk:
                return HttpResponseRedirect(reverse('user:eProfile'))
            else:
                tuser = get_object_or_404(User, pk=kwargs['pk'])
                tuser = healthUserFromDjangoUser(tuser)

                if not userauth.userCan_Profile(user, tuser, 'edit'):
                    return HttpResponseRedirect('user:dashboard')
        else:
            tuser=user


        form_medical = None

        if (tuser.hospital is None) or userauth.isHAdmin(user):
            form_medical = EditProfileForm_medical()

        form_basic = EditProfileForm_basic()
        form_emergency = EditProfileForm_emergency()

        setFormDefaultsFromModel(tuser, form_basic)
        setFormDefaultsFromModel(tuser.user, form_basic)

        return render(request, 'user/editprofile.html', {'user': user, 'tuser': tuser, 'form_basic': form_basic, 'form_medical': form_medical, 'form_emergency': form_emergency})


class EditEvent(View):

    def post(self, request, pk):
        user = get_user(request)
        if user is None:
            return HttpResponseRedirect(reverse('login'))

        old_event = get_visible_event_or_404(pk)

        event_form = getEventFormByUserType(user.getType(), data=request.POST, mode='update')

        if event_form.is_valid():
            if deleteInPostIsTrue(request.POST): # deleting event
                old_event.visible = False
                old_event.save()
                Syslog.deleteEvent(old_event,user)
                return HttpResponseRedirect(reverse('user:dashboard'))

            new_event = event_form.getModel()
            updateEventFromModel(old_event, new_event)

            if addEventConflictMessages(event_form, old_event):
                old_event.save()
                Syslog.modifyEvent(new_event,user)
                return HttpResponseRedirect(reverse('user:dashboard'))

        context = {'form': event_form, 'event': old_event, 'user': user}

        elevate_if_trusted_event(event_form, user, old_event)
        return render(request, 'user/eventdetail.html', context)


    def get(self, request, pk):
        event = get_visible_event_or_404(pk)

        user = get_user(request)
        if user is None or not userauth.userCan_Event(user, event, 'edit'):
            return HttpResponseRedirect(reverse('user:dashboard'))

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
            event_form.full_clean()


            if user.getType() == 'doctor':
                populateDependantFieldsPH(event_form, user.patient_set.all(), user.hospitals.all())
            if user.getType() == 'nurse':
                populateDependantFieldsPD(event_form, user.hospital.patient_set.all(), user.hospital.doctor_set.all(), user.hospital)

            elevate_if_trusted(event_form, user)
            return render(request, 'user/eventdetail.html', {'form': event_form, 'user': user, 'event': event})
        else:
            return HttpResponseRedirect(reverse('user:eEvent', args=(pk,)))


def viewEvent(request, pk):
    user = get_user(request)
    if user is None:
        return HttpResponseRedirect(reverse('login'))

    event = get_object_or_404(Event, pk=pk)

    if userauth.userCan_Event(user, event, 'view'):
        can_edit = userauth.userCan_Event(user, event, 'edit')
        return render(request, 'user/eventdetail.html', {'user': user, 'event': event, 'can_edit': can_edit})
    else:
        return HttpResponseRedirect(reverse('user:dashboard'))


class CreateEvent(View):

    def process_patient(self, user, event, form):
        print(user)
        add_dict_to_model({'patient': user, 'doctor': user.doctor, 'hospital': user.hospital, 'appointment': True}, event)

    def process_nurse(self, user, event, form):
        if not(form.cleaned_data['patient'] is None):
            add_dict_to_model({'hospital': form.cleaned_data['patient'].hospital, 'appointment': True}, event)

    def process_doctor(self, user, event, form):
        event.doctor = user
        event.appointment = not(form.cleaned_data['patient'] is None)

    def get(self, request):
        user = get_user(request)
        if user is None:
            return HttpResponseRedirect(reverse('login'))

        if not userauth.userCan_Event(user, None, 'create'):
            return HttpResponseRedirect(reverse('user:dashboard'))

        if not user.getType() in ['nurse', 'hosAdmin']:
            myEvents = getVisibleEvents(user)
        otherEvents = None
        eventForm = getEventFormByUserType(user.getType())
        if user.getType() == 'patient':
            otherEvents = getVisibleEvents(user.doctor).exclude(patient = user)
        elif user.getType() in ['nurse', 'hadmin']:
            eventForm.set_patient_doctor_queryset(user.hospital.patient_set.all(), user.hospital.doctor_set.all())
        elif user.getType() == 'doctor':
            eventForm.set_hospital_patient_queryset(user.hospitals.all(), user.patient_set.all())

        if not user.getType() in ['nurse', 'hosAdmin']:
            return render(request, 'user/eventhandle.html', {'form': eventForm, 'user': user, 'events': myEvents, 'otherEvents': otherEvents, 'canAccessDay': True})
        else:
            return render(request, 'user/eventhandle.html', {'form': eventForm, 'user': user, 'otherEvents': otherEvents, 'canAccessDay': True})

    def post(self, request):
        user = get_user(request)
        if user is None:
            return HttpResponseRedirect(reverse('login'))

        myEvents = getVisibleEvents(user)

        otherEvents = None

        event_form = getEventFormByUserType(user.getType(), data=request.POST)

        # Check For Timing Conflicts
        if event_form.is_valid():
            event = event_form.getModel()

            call = getattr(self, 'process_'+user.getType())
            call(user, event, event_form)

            if addEventConflictMessages(event_form, event):
                event.save()
                Syslog.createEvent(event,user)
                return HttpResponseRedirect(reverse('user:dashboard'))

        if user.getType() == 'patient':
            otherEvents = getVisibleEvents(user.doctor).exclude(patient = user)

        if user.getType() == 'doctor' and getVisibleEvents(event_form.cleaned_data['patient']) is not None:
            otherEvents = getVisibleEvents(event_form.cleaned_data['patient']).exclude(doctor = user)
            event_form.set_hospital_patient_queryset(user.hospitals.all(), user.patient_set.all())

        elevate_if_trusted(event_form, user)
        return render(request, 'user/eventhandle.html', {'form': event_form, 'user': user, 'events': myEvents, 'otherEvents': otherEvents, 'canAccessDay': True})

    @staticmethod
    def post_dependant_fields(request):
        if request.method == 'POST':
            user = get_user(request)
            myEvents = getVisibleEvents(user)
            if user is None:
                return HttpResponseRedirect(reverse('login'))

            event_form = getEventFormByUserType(user.getType(), data=request.POST)
            otherEvents = Event.objects.none()

            event_form.full_clean()

            if user.getType() == 'doctor':
                populateDependantFieldsPH(event_form, user.patient_set.all(), user.hospitals.all())
            elif user.getType() == 'nurse':
                populateDependantFieldsPD(event_form, user.hospital.patient_set.all(),
                                          user.hospital.doctor_set.all(), user.hospital)

            elevate_if_trusted(event_form, user)

            if event_form.cleaned_data["patient"] is not None:
                otherEvents = getVisibleEvents(event_form.cleaned_data["patient"]).exclude(doctor = user)

            return render(request, 'user/eventhandle.html', {'form': event_form, 'user': user, 'events': myEvents, 'otherEvents': otherEvents, 'canAccessDay': True})
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

    if(user.getType() != "nurse" and user.getType() != "hosAdmin"):
        events = getVisibleEvents(user).order_by('startTime')
        context['events'] = events
    elif(user.getType() == "doctor"):
        context['patients'] = user.patient_set.all()
        context['hosptials'] = user.hospitals.all()
    elif(user.getType() == "nurse"):
        context['patients'] = user.hospital.patient_set.all()
        context['doctors'] = user.hospital.doctor_set.all()
    elif(user.getType() == "hosAdmin"):
        context['patients'] = user.hospital.patient_set.all()
        context['doctors'] = user.hospital.doctor_set.all()
        context['search_form'] = HosAdminSearchForm()

    context['tuser'] = user #TODO: Remove once nurse has searchable columns

    return render(request, 'user/dashboard.html', context)