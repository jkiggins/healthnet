from django.shortcuts import render, get_object_or_404
from django.views.generic.edit import CreateView
from django.http import HttpResponse
from User.models import *
from .forms import PatientForm
from django.template import loader

from .models import logIn

# Create your views here.

def index(request):

    return render(request, 'logIn/index.html')


def authenticate(request):
    response = 'neutral'
    #queryset
    patientquery = Patient.objects.filter(UserName=request.POST['UN'])

    if patientquery.exists():
        response = 'well the username exists'
        passfromdb = patientquery.values('Password')[0]['Password']
        if passfromdb == request.POST['PW']:
            response = response +' hell yeah you in'
        else:
            response = response+ ' gettt outta here with that password tho'
    else:
        response = 'username does not exist'
    return HttpResponse(response + str(passfromdb))


class Register(CreateView):
    model = Patient
    template_name = 'login/register_form.html'
    form_class = PatientForm


def testView(request):
    return HttpResponse("Hello World")