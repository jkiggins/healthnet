from django.shortcuts import render
from django.views.generic import View
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from .models import Syslog
from user.viewhelper import get_user

# Create your views here.

class view_log(View):

    def get(self, request):
        context = {'system_log': Syslog.objects.all(),
                   'cuser': get_user(request)}
        return render(request, 'syslogging/System_Log.html', context)

    def post(self, request):
        return HttpResponseRedirect(reverse('user:dashboard'))