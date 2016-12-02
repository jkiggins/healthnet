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


###################EMR AJAX##########################
def emrItemAjax(request, pk):
    user = viewhelper.get_user(request)
    patient = get_object_or_404(Patient, pk=pk)
    pkdict = json.loads(request.body.decode("utf-8"))
    item = get_object_or_404(EMRItem, pk=pkdict['emrpk'])
    return render(request, 'emr/view_emr_item.html', {'item': item, 'permissions': getPermissionsContext(user, patient)})


def emrActionAjax(request, pk):
    pkdict = json.loads(request.body.decode("utf-8"))
    if 'emrpk' in pkdict and 'action' in pkdict:
        item = get_object_or_404(EMRItem, pk=pkdict['emrpk'])

        if isTest(item):
            if pkdict['action'] == 'releasehide':
                bool = item.emrtest.released
                item.emrtest.released = not bool
                item.emrtest.save()
        elif isPrescription(item):
            if pkdict['action'] == 'stop':
                item.endDate = timezone.now()
        else:
            return HttpResponse("PASS")

        item.save()
        return emrItemAjax(request, pk)
    return HttpResponse("PASS")


###################EMR AJAX##########################

def getFormFromReqType(mtype, patient, provider, post=None, files=None):
    form = None
    if mtype == 'test':
        if post != None:
            form = TestCreateForm(post, files)
        else:
            form = TestCreateForm(initial={'patient': patient.pk})
    elif mtype == 'vitals':
        if post != None:
            form = VitalsCreateForm(post, initial={'patient': patient.pk})
        else:
            form = VitalsCreateForm(initial={'patient': patient.pk})
    elif mtype == 'note':
        if post != None:
            form = EMRItemCreateForm(post, initial={'patient': patient.pk})
        else:
            form = EMRItemCreateForm(initial={'patient': patient.pk})
    elif mtype == 'prescription':
        if post != None:
            form = prescriptionCreateForm(post, initial={'patient': patient.pk, 'proivder': provider.user.pk})
        else:
            form = prescriptionCreateForm(initial={'patient': patient.pk, 'proivder': provider.user.pk})
    elif mtype == "admitdischarge":
        if post != None:
            form = AdmitDishchargeForm(post)
        else:
            form = AdmitDishchargeForm()

    return form


#####################################VIEW EMR#####################################
def getPermissionsContext(cuser, patient):
    return {'canEdit': userauth.userCan_EMR(cuser, patient, 'edit'),
            'canVitals': userauth.userCan_EMR(cuser, patient, 'vitals'),
            'canAdmit': userauth.userCan_EMR(cuser, patient, 'admit'),
            'canPrescribe': userauth.userCan_EMR(cuser, patient, 'prescribe')}

def viewEMR(request, pk):
    user = viewhelper.get_user(request)
    if user is None:
        return viewhelper.unauth(request)

    patient = get_object_or_404(Patient, pk=pk)

    if not userauth.userCan_EMR(user, patient, 'view'):
        # TODO: add syslogging to unauth, Syslog.unauth_acess(request)
        return viewhelper.unauth(request)

    emr = patient.emritem_set.all().order_by('-date_created')

    form=None

    if request.method == "POST":
        form = FilterSortForm(request.POST)
        if form.is_valid():
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
                    pass  # TODO: impliment admisson and dishcharge in models
                if 'discharge' in form.cleaned_data['filters']:
                    pass
                emr = build

            if ('keywords' in form.cleaned_data):
                build = emr.none()
                words = form.cleaned_data['keywords'].split(' ')
                for word in words:
                    build |= emr.filter(content__contains=word)
                    build |= emr.filter(emrvitals__bloodPressure__contains=word)

                    if viewhelper.try_parse(word):
                        num = int(word)
                        build |= emr.filter(priority=num)
                        build |= emr.filter(emrprescription__dosage=num)
                        build |= emr.filter(emrprescription__amountPerDay=num)
                        build |= emr.filter(emrvitals__height=num)
                        build |= emr.filter(emrvitals__weight=num)

                emr = build

            if 'sort' in form.cleaned_data:
                if 'date' in form.cleaned_data['sort']:
                    emr = emr.order_by('-date_created')
                elif 'priority' in form.cleaned_data['sort']:
                    emr = emr.order_by('-priority')
                elif 'aplph' in form.cleaned_data['sort']:
                    emr = emr.order_by('content')

    else:
        form = FilterSortForm()

    ctx = {'EMRItems': emr, 'form': form, 'user': user, 'tuser': patient,
           'permissions': getPermissionsContext(user, patient),
           'admit': viewhelper.isAdmitted(patient)}

    if ctx['admit']:
        ctx['hospital'] = patient.admittedHospital()

    if hasattr(patient, 'emrprofile'):
        ctx['EMRProfile'] = patient.emrprofile

    Syslog.viewEMR(patient, user)

    return render(request, 'emr/filter_emr.html', ctx)
#####################################VIEW EMR#####################################

def canCreateEditEmr(mtype, patient, provider):
    auth = True
    auth |= mtype in ['item', 'test', 'vitals', 'profile'] and userauth.userCan_EMR(provider, patient, 'edit')
    auth |= mtype == 'prescription' and userauth.userCan_EMR(provider, patient, 'prescribe')
    auth |= mtype in ['vitals', 'profile'] and userauth.userCan_EMR(provider, patient, 'vitals')
    return auth


def EMRItemCreate(request, pk, type):

    cuser = viewhelper.get_user(request)
    if cuser is None:
        return HttpResponseRedirect(reverse('login'))

    patient = get_object_or_404(Patient, pk=pk)

    if not canCreateEditEmr(type, patient, cuser):
        return viewhelper.toEmr(request, patient.pk)


    if request.method == "POST":
        form = getFormFromReqType(type, patient, cuser, post=request.POST, files=request.FILES)

        if form.is_valid():
            m = form.save(commit=False, patient=patient)

            if isPrescription(m):
                m.provider = cuser

            m.save()

            return HttpResponseRedirect(reverse('emr:vemr', args=(patient.pk,)))

    else:
        form = getFormFromReqType(type, patient, cuser)

    return render(request, 'emr/emritem_edit.html', {'user': cuser, 'form': form})


def editAdmitDischarge(request, emritem):
    user = viewhelper.get_user(request)
    if user is None:
        viewhelper.unauth(request)

    if not userauth.userCan_EMRItem(user, emritem, 'edit'):
        viewhelper.unauth(request)

    #TODO: allow hospital admin to edit all admission fields

    form = None
    if request.method == "POST":
        form = AdmitDishchargeForm(request.POST)
        if form.is_valid():
            m = form.save(commit=True, update=emritem)
            return viewhelper.toEmr(request, emritem.patient.pk)
    else:
        form = AdmitDishchargeForm()
        form.defaults(emritem)

    form.lockField('hospital', emritem.emradmitstatus.hospital)
    form.lockField('patient', emritem.patient)

    return render(request, 'emr/emritem_edit.html', {'user': user, 'form': form})


def editEmrItem(request, pk):
    user = viewhelper.get_user(request)
    if user is None:
        return viewhelper.unauth(request)

    emritem = get_object_or_404(EMRItem, pk=pk)

    if not userauth.userCan_EMRItem(user, emritem, 'edit'):
        return viewhelper.unauth(request)

    if hasattr(emritem, 'emradmitstatus'):
        return editAdmitDischarge(request, emritem)

    form = None

    if request.method == "GET":
        print(emrItemType(emritem))
        form = getFormFromReqType(emrItemType(emritem), emritem.patient, user)
        form.defaults(emritem)
    else:
        form = getFormFromReqType(emrItemType(emritem), emritem.patient, user, post=request.POST,
                                       files=request.FILES)
        if form.is_valid():
            form.save(update=emritem, commit=True)
            return HttpResponseRedirect(reverse('emr:vemr', args=(emritem.patient.pk,)))

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

            if cuser.getType() in ['nurse', 'hosAdmin']:
                form.lockField('hospital', cuser.hospital)
            elif cuser.getType() == 'doctor':
                form.fields['hospital'].queryset = cuser.hospitals.all()

        else:
            if not userauth.userCan_EMR(cuser, patient, 'discharge'):
                return self.kick(patient)

            ctx['formtitle'] = "Discharge Form"
            form.lockField('admit', False)

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











