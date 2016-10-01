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


class Register(CreateView):
    model = Patient
    template_name = 'login/register_form.html'
    form_class = PatientForm