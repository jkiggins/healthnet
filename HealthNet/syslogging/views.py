from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views.generic import View

from HealthNet.viewhelper import get_user
from .forms import DateSearchForm
from .models import Syslog


# Create your views here.

class view_log(View):

    def get(self, request):
        form = DateSearchForm()
        message = "Log Entries: " + str(Syslog.objects.all().count())
        context = {'system_log': Syslog.objects.all(),
                   'user': get_user(request),
                   'search_form': form,
                   'message': message}
        return render(request, 'syslogging/System_Log.html', context)

    def post(self, request):
        """ searches the database for those items that occur between specific times"""

        form = DateSearchForm(request.POST)
        if not form.is_valid():
            return HttpResponseRedirect(reverse('syslogging:viewlog'))
        form.full_clean()
        start_time = form.cleaned_data['startTime']
        end_time = form.cleaned_data['endTime']
        if start_time < end_time:
            relevant_logs = []
            c=0
            for item in Syslog.objects.all(): #if between the times
                if (item.date_created > start_time) and (item.date_created < end_time):
                    c += 1
                    relevant_logs.append(item)

            message = str(c) + " Results between: " + str(start_time)[:19] + " and " + str(end_time)[:19]

            context = {'system_log': relevant_logs,
                       'cuser': get_user(request),
                       'search_form': form,
                       'message': message}
        else:
            message = "End time must occur after start time!"
            context = {'system_log': Syslog.objects.all(),
                       'cuser': get_user(request),
                       'search_form': form,
                       'message': message}
        return render(request, 'syslogging/System_Log.html', context)