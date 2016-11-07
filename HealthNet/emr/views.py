from django.shortcuts import render , get_object_or_404
from django.http import HttpResponse , HttpResponseRedirect
from django.views.generic import DetailView, View
from django.core.urlresolvers import reverse
from user.models import Patient
from user import userauth
from user.viewhelper import get_user
from .models import *
from .forms import *
from .viewhelper import *
from syslogging.models import *


def viewSelfEmr(request):
    cuser = get_user(request)
    if cuser is None:
        return HttpResponseRedirect(reverse('login'))
    return HttpResponseRedirect(reverse('emr:vemr', args=(cuser.pk,)))

def feedBackView(request, *args):
    return HttpResponse("content")


class viewEMR(DetailView):

    model = Patient

    def getPermissionsContext(self, cuser, patient):
        return {'canEdit': userauth.userCan_EMR(cuser, patient, 'edit'),
                'canVitals': userauth.userCan_EMR(cuser, patient, 'vitals'),
                'admit': userauth.userCan_EMR(cuser, patient, 'admit'),
                'canPrescribe': userauth.userCan_EMR(cuser, patient, 'prescribe')}

    def get(self, request, *args, **kwargs):
    #### AUTHORIZE FOR VIEW####
        cuser = get_user(request)
        if cuser is None:
            return HttpResponseRedirect(reverse('login'))

        patient = self.get_object()

        if not userauth.userCan_EMR(cuser, patient, 'view'):
            Syslog.unauth_acess(request)
            return HttpResponseRedirect(reverse('user:dashboard'))
    ############################

        emr = patient.emritem_set.all()

        if not userauth.userCan_EMR(cuser, patient, 'view_full'):
            emr = emr.exclude(emrtest__released=False)

        form = FilterSortForm()

        Syslog.viewEMR(patient,cuser)
        return render(request, 'emr/viewEmr.html', {'EMRItems': emr, 'form': form, 'user': cuser, 'tuser': patient,
                                                    'permissions': self.getPermissionsContext(cuser, patient)})

    def post(self, request, **kwargs):
        cuser = get_user(request)
        if cuser is None:
            return HttpResponseRedirect(reverse('login'))

        patient = self.get_object()

        emr = patient.emritem_set.all()

        if not userauth.userCan_EMR(cuser, patient, 'view_full'):
            emr = emr.exclude(emrtest__released=False)

        form = FilterSortForm(request.POST)

        if form.is_valid():
            if 'sort' in form.cleaned_data:
                if 'date' in form.cleaned_data['sort']:
                    emr = emr.order_by('date_created')
                elif 'priority' in form.cleaned_data['sort']:
                    emr = emr.order_by('-priority')
                elif 'aplph' in form.cleaned_data['sort']:
                    emr = emr.order_by('title')


            if ('filters' in form.cleaned_data) and (form.cleaned_data['filters'] != []):
                build = emr.none()
                if 'prescription' in form.cleaned_data['filters']:
                    build |= emr.exclude(emrprescription=None)
                if 'vitals' in form.cleaned_data['filters']:
                    build |= emr.exclude(emrvitals=None)
                if 'test' in form.cleaned_data['filters']:
                    build |= emr.exclude(emrtest=None)
                if 'pending' in form.cleaned_data['filters']:
                    build |= emr.filter(emrtest__released=False)
                if 'admit' in form.cleaned_data['filters']:
                    pass # TODO: impliment admisson and dishcharge in models
                if 'discharge' in form.cleaned_data['filters']:
                    pass
                emr = build

            if ('keywords' in form.cleaned_data):
                build = emr.none()
                words = form.cleaned_data['keywords'].split(' ')
                for word in words:
                    build |= emr.filter(title__contains=word)
                    build |= emr.filter(content__contains=word)
                    build |= emr.filter(emrvitals__bloodPressure__contains=word)

                    if try_parse(word):
                        num = int(word)
                        build |= emr.filter(priority=num)
                        build |= emr.filter(emrprescription__dosage=num)
                        build |= emr.filter(emrprescription__amountPerDay=num)
                        build |= emr.filter(emrvitals__height=num)
                        build |= emr.filter(emrvitals__weight=num)

                emr=build

        return render(request, 'emr/viewEmr.html', {'EMRItems': emr, 'form': form, 'user': cuser, 'tuser': patient,
                                                    'permissions': self.getPermissionsContext(cuser, patient)})


class EMRItemCreate(View):
    type = None
    pk_url_kwarg = 'pk'

    def getFormFromReqType(self, patient, provider, post=None):
        form = None
        if self.type == 'test':
            if post != None:
                form = TestCreateForm(post)
            else:
                form = TestCreateForm(initial={'emrpatient': patient.pk})
        elif self.type == 'vitals':
            if post != None:
                form = VitalsCreateForm(post, initial={'emrpatient': patient.pk})
            else:
                form = VitalsCreateForm(initial={'emrpatient': patient.pk})
        elif self.type == 'item':
            if post != None:
                form = EMRItemCreateForm(post, initial={'emrpatient': patient.pk})
            else:
                form = EMRItemCreateForm(initial={'emrpatient': patient.pk})
        elif self.type == 'prescription':
            if post != None:
                form = prescriptionCreateForm(post, initial={'emrpatient': patient.pk, 'proivder': provider.user.pk})
            else:
                form = prescriptionCreateForm(initial={'emrpatient': patient.pk, 'proivder': provider.user.pk})


        return form


    def get(self, request, pk=None):
        cuser = get_user(request)
        if cuser is None:
            return HttpResponseRedirect(reverse('login'))

        patient = get_object_or_404(Patient, pk=pk)

        if self.type in ['item', 'test'] and userauth.userCan_EMR(cuser, patient, 'edit'):
            return HttpResponseRedirect(reverse('emr:vemr', args=(patient.pk,)))

        form = self.getFormFromReqType(patient, cuser)

        return render(request, 'emr/emrtest_form.html', {'user': cuser, 'form': form})


    def post(self, request, pk=None):
        cuser = get_user(request)
        if cuser is None:
            return HttpResponseRedirect(reverse('login'))


        print('pk: {0}'.format(pk))
        patient = get_object_or_404(Patient, pk=pk)
        form = self.getFormFromReqType(patient, cuser, post=request.POST)


        if form.is_valid():
            form.save(commit=True, patient=patient)
            return HttpResponseRedirect(reverse('emr:vemr', args=(patient.pk,)))
        else:
            return render(request, 'emr/emrtest_form.html', {'user': cuser, 'form': form})


def viewEMRItem(request, pk):
    pass

