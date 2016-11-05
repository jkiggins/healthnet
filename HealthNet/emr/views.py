from django.shortcuts import render , get_object_or_404
from django.http import HttpResponse , HttpResponseRedirect
from emr.models import EMRVitals, EMRNote, EMRTrackedMetric
from emr.forms import EMRVitalsForm
from django.views.generic.edit import CreateView, UpdateView , View
from django.contrib.auth.models import Permission
from django.core.urlresolvers import reverse
from user.models import Patient
from user import userauth
from user.viewhelper import get_user


def viewSelfEMR(request):
    pass

def viewEMR(request, pk):
    cuser = get_user(request)
    if cuser is None:
        return HttpResponseRedirect(reverse('login'))




    if currUser.getType() == "doctor" or currUser.getType() == "nurse":
        user = get_object_or_404(Patient, pk=pk)
    else:
        user=currUser

    return render(request, 'emr/index.html', {'user': currUser, 'emruser': user})

def viewEMRItem(request, pk):
    pass

