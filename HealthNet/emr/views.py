from PIL import Image
from django.core.urlresolvers import reverse
from django.http import HttpResponse , HttpResponseRedirect
from django.shortcuts import render , get_object_or_404
from django.views.generic import DetailView, View
import HealthNet.viewhelper as viewhelper


from HealthNet import userauth
from syslogging.models import *
from user.models import *
from django.core.urlresolvers import reverse
from .forms import *
import json


def viewSelfEmr(request):
    cuser = viewhelper.get_user(request)
    if cuser is None:
        return HttpResponseRedirect(reverse('login'))
    return HttpResponseRedirect(reverse('emr:vemr', args=(cuser.pk,)))

def feedBackView(request, *args):
    return HttpResponse("content")


def editEmrProfile(request, pk):
    user = viewhelper.get_user(request)
    if user is None:
        viewhelper.unauth(request)

    patient = get_object_or_404(Patient, pk=pk)

    if not userauth.userCan_EMR(user, patient, 'vitals'):
        return viewhelper.unauth(request)

    form = None

    if request.method == "GET":
        form = ProfileCreateForm()
        if hasattr(patient, 'emrprofile'):
            form.defaults(patient.emrprofile)
    elif request.method == "POST":
        form = ProfileCreateForm(request.POST)

        if form.is_valid():
            m = None
            if hasattr(patient, 'emrprofile'):
                m = form.save(commit=False, model=patient.emrprofile)
            else:
                m = form.save(commit=False)

            m.patient = patient
            m.save()
            return HttpResponseRedirect(reverse('emr:vemr', args=(pk,)))

    return render(request, 'emr/emritem_edit.html', {'user': user, 'form': form})


def emrItemAjax(request, pk):
    pkdict = json.loads(request.body.decode("utf-8"))
    item = get_object_or_404(EMRItem, pk=pkdict['emrpk'])
    return render(request, 'emr/view_emr_item.html', {'item': item})


class viewEMR(viewhelper.HealthView):

    emr_patient = None
    emr = None

    def getPermissionsContext(self, cuser, patient):
        return {'canEdit': userauth.userCan_EMR(cuser, patient, 'edit'),
                'canVitals': userauth.userCan_EMR(cuser, patient, 'vitals'),
                'canAdmit': userauth.userCan_EMR(cuser, patient, 'admit'),
                'canPrescribe': userauth.userCan_EMR(cuser, patient, 'prescribe')}


    def setup(self, request, user, **kwargs):
        if 'pk' in kwargs:
            self.emr_patient = get_object_or_404(Patient, pk=kwargs['pk'])

            if not userauth.userCan_EMR(user, self.emr_patient, 'view'):
                Syslog.unauth_acess(request)
                return HttpResponseRedirect(reverse('user:dashboard'))

    def patient(self, request, user):
        self.emr = viewhelper.getVisibleEMR(self.emr_patient).order_by('-date_created')
        return self.respond(request, user)

    def doctor(self, request, user):
        self.emr = self.emr_patient.emritem_set.all().order_by('-date_created')
        return self.respond(request, user)

    def nurse(self, request, user):
        self.doctor(request, user)
        return self.respond(request, user)

    def hosAdmin(self, request, user):
        self.doctor(request, user)
        return self.respond(request, user)

    def respond(self, request, user):
        if self.POST is None:
            form = FilterSortForm()

        else:
            form = FilterSortForm(self.POST)
            if form.is_valid():
                if ('filters' in form.cleaned_data) and (form.cleaned_data['filters'] != []):
                    build = self.emr.none()
                    if 'prescription' in form.cleaned_data['filters']:
                        build |= self.emr.exclude(emrprescription=None)
                    if 'vitals' in form.cleaned_data['filters']:
                        build |= self.emr.exclude(emrvitals=None)
                    if 'test' in form.cleaned_data['filters']:
                        build |= self.emr.exclude(emrtest=None)
                    if 'pending' in form.cleaned_data['filters']:
                        build |= self.emr.filter(emrtest__released=False)
                    if 'admit' in form.cleaned_data['filters']:
                        pass  # TODO: impliment admisson and dishcharge in models
                    if 'discharge' in form.cleaned_data['filters']:
                        pass
                    self.emr = build

                if ('keywords' in form.cleaned_data):
                    build = self.emr.none()
                    words = form.cleaned_data['keywords'].split(' ')
                    for word in words:
                        build |= self.emr.filter(title__contains=word)
                        build |= self.emr.filter(content__contains=word)
                        build |= self.emr.filter(emrvitals__bloodPressure__contains=word)

                        if viewhelper.try_parse(word):
                            num = int(word)
                            build |= self.emr.filter(priority=num)
                            build |= self.emr.filter(emrprescription__dosage=num)
                            build |= self.emr.filter(emrprescription__amountPerDay=num)
                            build |= self.emr.filter(emrvitals__height=num)
                            build |= self.emr.filter(emrvitals__weight=num)

                    self.emr = build

                if 'sort' in form.cleaned_data:
                    if 'date' in form.cleaned_data['sort']:
                        self.emr = self.emr.order_by('-date_created')
                    elif 'priority' in form.cleaned_data['sort']:
                        self.emr = self.emr.order_by('-priority')
                    elif 'aplph' in form.cleaned_data['sort']:
                        self.emr = self.emr.order_by('title')


        ctx = {'EMRItems': self.emr, 'form': form, 'user': user, 'tuser': self.emr_patient,
               'permissions': self.getPermissionsContext(user, self.emr_patient),
               'admit': viewhelper.isAdmitted(self.emr_patient)}

        if ctx['admit']:
            ctx['hospital'] = self.emr_patient.admittedHospital()

        if hasattr(self.emr_patient, 'emrprofile'):
            ctx['EMRProfile'] = self.emr_patient.emrprofile

        Syslog.viewEMR(self.emr_patient, user)

        return render(request, 'emr/filter_emr.html', ctx)


def canCreateEditEmr(mtype, patient, provider):
    auth = True
    auth |= mtype in ['item', 'test', 'vitals', 'profile'] and userauth.userCan_EMR(provider, patient, 'edit')
    auth |= mtype == 'prescription' and userauth.userCan_EMR(provider, patient, 'prescribe')
    auth |= mtype in ['vitals', 'profile'] and userauth.userCan_EMR(provider, patient, 'vitals')
    return auth


class EMRItemCreate(View):
    type = None
    pk_url_kwarg = 'pk'

    def get(self, request, pk=None):
        cuser = viewhelper.get_user(request)
        if cuser is None:
            return HttpResponseRedirect(reverse('login'))

        patient = get_object_or_404(Patient, pk=pk)

        if not canCreateEditEmr(self.type, patient, cuser):
            return HttpResponseRedirect(reverse('emr:vemr', args=(patient.pk,)))

        form = EditEmrItem.getFormFromReqType(self.type, patient, cuser)

        return render(request, 'emr/emritem_edit.html', {'user': cuser, 'form': form})


    def post(self, request, pk=None):
        cuser = viewhelper.get_user(request)
        if cuser is None:
            return HttpResponseRedirect(reverse('login'))

        patient = get_object_or_404(Patient, pk=pk)
        form = EditEmrItem.getFormFromReqType(self.type, patient, cuser, post=request.POST)


        if form.is_valid():
            form.save(commit=True, patient=patient, provider=cuser)
            return HttpResponseRedirect(reverse('emr:vemr', args=(patient.pk,)))
        else:
            return render(request, 'emr/emritem_edit.html', {'user': cuser, 'form': form})


class EditEmrItem(viewhelper.HealthView):

    @staticmethod
    def getFormFromReqType(mtype, patient, provider, post=None, files=None):
        form = None
        if mtype == 'test':
            if post != None:
                form = TestCreateForm(post, files)
            else:
                form = TestCreateForm(initial={'emrpatient': patient.pk})
        elif mtype == 'vitals':
            if post != None:
                form = VitalsCreateForm(post, initial={'emrpatient': patient.pk})
            else:
                form = VitalsCreateForm(initial={'emrpatient': patient.pk})
        elif mtype == 'item':
            if post != None:
                form = EMRItemCreateForm(post, initial={'emrpatient': patient.pk})
            else:
                form = EMRItemCreateForm(initial={'emrpatient': patient.pk})
        elif mtype == 'prescription':
            if post != None:
                form = prescriptionCreateForm(post, initial={'emrpatient': patient.pk, 'proivder': provider.user.pk})
            else:
                form = prescriptionCreateForm(initial={'emrpatient': patient.pk, 'proivder': provider.user.pk})

        return form

    emritem = None

    def setup(self, request, user, **kwargs):
        self.emritem = get_object_or_404(EMRItem, pk=kwargs['pk'])

    def respond(self, request, user):
        if not userauth.userCan_EMRItem(user, self.emritem, 'edit'):
            return self.unauthorized(request)

        form = None

        if self.POST is None:
            form = self.getFormFromReqType(emrItemType(self.emritem), self.emritem.patient, user)
            form.defaults(self.emritem)
        else:
            form = self.getFormFromReqType(emrItemType(self.emritem), self.emritem.patient, user, post=request.POST,
                                      files=request.FILES)
            if form.is_valid():
                form.save(update=self.emritem)
                return HttpResponseRedirect(reverse('emr:vemr', args=(self.emritem.patient.pk,)))

        return render(request, 'emr/emritem_edit.html', {'user': user, 'form': form})


class AdmitDishchargeView(DetailView):
    model = Patient
    type=None

    def kick(self, patient):
        return HttpResponseRedirect(reverse('emr:vemr', args=(patient.pk,)))

    def get(self, request, **kwargs):
        cuser = viewhelper.get_user(request)
        if cuser is None:
            return HttpResponseRedirect(reverse('login'))

        patient = self.get_object()

        if not canCreateEditEmr(self.type, patient, cuser) or not userauth.userCan_EMR(cuser, patient, 'admit'):
            return self.kick(patient)

        form = AdmitDishchargeForm(initial={'emrpatient': patient.pk})

        ctx = {'user': cuser, 'form': form}

        if patient.admittedHospital() is None:
            if not userauth.userCan_EMR(cuser, patient, 'admit'):
                return self.kick(patient)

            ctx['formtitle'] = "Admission Form"
            form.lockField('admit', True)
            form.lockField('title', 'Admission')

            if cuser.getType() in ['nurse', 'hosAdmin']:
                form.lockField('hospital', cuser.hospital)
            elif cuser.getType() == 'doctor':
                form.fields['hospital'].queryset = cuser.hospitals.all()

        else:
            if not userauth.userCan_EMR(cuser, patient, 'discharge'):
                return self.kick(patient)

            ctx['formtitle'] = "Discharge Form"
            form.lockField('admit', False)
            form.lockField('title', 'Discharge')

            form.lockField('hospital', '')


        return render(request, 'emr/emritem_edit.html', ctx)


    def post(self, request, **kwargs):
        cuser = viewhelper.get_user(request)
        if cuser is None:
            return HttpResponseRedirect(reverse('login'))

        patient = self.get_object()

        form = AdmitDishchargeForm(request.POST, initial={'emrpatient': patient.pk})
        ctx = {'user': cuser, 'form': form}

        title=None

        mdict = {}

        if patient.admittedHospital() is None:
            ctx['formtitle'] = "Admission Form"
            form.lockField('admit', True)
            mdict['title'] = "Admission"

            if cuser.getType() in ['nurse', 'hosAdmin']:
                form.lockField('hospital', cuser.hospital)
                mdict['hospital'] = cuser.hospital
            elif cuser.getType() == 'doctor':
                form.fields['hospital'].queryset = cuser.hospitals.all()

        else:
            ctx['formtitle'] = "Discharge Form"
            form.lockField('admit', False)
            form.lockField('hospital', '')
            mdict['title']="Discharge"
            mdict['admit']=False


        if form.is_valid():
            m = form.save(commit=False, patient=patient, provider=cuser)

            viewhelper.add_dict_to_model(mdict, m)
            m.save()

            if not hasattr(patient, 'emrprofile'):
                patient.emrprofile = EMRProfile.objects.create()
                patient.save()

            patient.emrprofile.admit_status = m
            patient.emrprofile.save()

            return HttpResponseRedirect(reverse('emr:vemr', args=(patient.pk,)))
        else:
            return render(request, 'emr/emritem_edit.html', ctx)


def serveTestMedia(request, pk):
    cuser = viewhelper.get_user(request)
    if cuser is None:
        return HttpResponseRedirect(reverse('login'))

    emritem = get_object_or_404(EMRItem, pk=pk)
    patient = emritem.patient

    path = None

    if hasattr(emritem, 'emrtest'):
        if emritem.emrtest.released or userauth.userCan_EMR(cuser, patient, 'view_full'):
            try:
                with open(emritem.emrtest.images.path, "rb") as f:
                    return HttpResponse(f.read(), content_type="image/jpeg")
            except IOError:
                return getBlankImage()
    return getBlankImage()


def getBlankImage():
    red = Image.new('RGBA', (1, 1), (255, 255, 255, 0))
    response = HttpResponse(content_type="image/jpeg")
    red.save(response, "JPEG")
    return response









