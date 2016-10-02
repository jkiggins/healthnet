from django.shortcuts import render
from django.http import HttpResponse
from emr.models import EMRVitals, EMRNote, EMRTrackedMetric
from emr.forms import EMRVitalsForm
from django.views.generic.edit import CreateView, UpdateView

def index(request, pk):
    return HttpResponse("This is the emr index for user with id = " + pk)


class CreateEMR(CreateView):

    model = EMRVitals
    template_name = 'emr/emrForm.html'

    form_class = EMRVitalsForm


class EditEMR(UpdateView):

    model = EMRVitals
    template_name = 'emr/emrForm.html'

    form_class = EMRVitalsForm


