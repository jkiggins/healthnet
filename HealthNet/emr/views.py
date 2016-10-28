from django.shortcuts import render , get_object_or_404
from django.http import HttpResponse , HttpResponseRedirect
from emr.models import EMRVitals, EMRNote, EMRTrackedMetric
from emr.forms import EMRVitalsForm
from django.views.generic.edit import CreateView, UpdateView , View
from django.contrib.auth.models import Permission
from django.core.urlresolvers import reverse
from user.models import Patient
from user.views import get_user_or_404

def index(request, pk):
    currUser = get_user_or_404(request , {"doctor" , "nurse" , "patient"})
    user = None

    if currUser.getType() == "doctor" or currUser.getType() == "nurse":
        user = get_object_or_404(Patient, pk=pk)
    else:
        user=currUser

    return render(request, 'emr/index.html', {'user': currUser, 'emruser': user})


class CreateEMR(CreateView):

    model = EMRVitals
    template_name = 'emr/emrForm.html'

    form_class = EMRVitalsForm


class EditEMR(View):

    def get(self, request, pk):
        user = request.user
        request.session['Patient.emr'] = pk

        if(user.getType() == "doctor" or user.getType() == "nurse"):
            model = EMRVitals
            template_name = 'emr/emrForm.html'

            form_class = EMRVitalsForm

    def post(self , request):
        changedEMR = EMRVitalsForm(request.POST)
        if changedEMR.is_valid():
            changedEMR.save()
        return HttpResponseRedirect(reverse('emr:index' , request.session['Patient.emr']))