from django.shortcuts import render
from django.http import HttpResponse , HttpResponseRedirect
from emr.models import EMRVitals, EMRNote, EMRTrackedMetric
from emr.forms import EMRVitalsForm
from django.views.generic.edit import CreateView, UpdateView , View
from django.contrib.auth.models import Permission
from django.core.urlresolvers import reverse

def index(request, pk):
    return HttpResponse("This is the emr index for user with id = " + pk)


class CreateEMR(CreateView):

    model = EMRVitals
    template_name = 'emr/emrForm.html'

    form_class = EMRVitalsForm


class EditEMR(View):

    def get(self , request , pk):
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