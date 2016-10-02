from django.shortcuts import render
from django.http import HttpResponse

def index(request, pk):
    return HttpResponse("This is the emr index for user with id = " + pk)
