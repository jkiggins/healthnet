from django.shortcuts import render
from django.views.generic import View
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

# Create your views here.

class view_log(View):

    def get(self, request, **kwargs):
        return HttpResponseRedirect(reverse('user:dashboard'))

    def post(self, request, **kwargs):
        return HttpResponseRedirect(reverse('user:dashboard'))