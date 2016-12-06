from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views.generic import View

from HealthNet.viewhelper import get_user
import HealthNet.viewhelper as viewhelper
from .forms import DateSearchForm
from .models import Syslog


def view_log(request):
    user = get_user(request)
    if (user is None):
        return viewhelper.unauth(request, "You much be logged in to view this page")

    if not viewhelper.isHosadmin(user):
        return viewhelper.unauth(request, "You much be a hospital admin to view the page")

    form = None

    logs = Syslog.objects.all()

    if request.method == "POST":
        form = DateSearchForm(request.POST)

        if form.is_valid():
            logs = logs.filter(date_created__gte=form.cleaned_data['start']).filter(date_created__lte=form.cleaned_data['end'])
            build = Syslog.objects.none()
            for w in form.cleaned_data['keywords'].split(' '):
                build |= logs.filter(message__icontains=w)
            logs = build
    else:
        form = DateSearchForm()

    return render(request, 'syslogging/System_Log.html', viewhelper.getBaseContext(request, user, form=form, logs=logs, title="System Logs"))
