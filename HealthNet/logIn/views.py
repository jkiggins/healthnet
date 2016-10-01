from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.template import loader

from .models import logIn

# Create your views here.

def index(request):

    return render(request, 'logIn/index.html')