from Calendar.models import Event
from django.shortcuts import render, get_list_or_404
from django.views.generic.edit import CreateView, UpdateView
from Calendar.models import Event
from Calendar.forms import EventForm
from django.http import HttpResponseRedirect


def index(request):
    events = Event.objects.all()
    return render(request, 'events/index.html', {'events': events})


def detail(request, event_id):
    event = get_list_or_404(Event, pk=event_id)
    return render(request, 'events/detail.html', {'event': event})


class CreateEvent(CreateView):

    model = Event
    template_name = 'events/event_form.html'

    form_class = EventForm


class EditEvent(UpdateView):

    model = Event
    template_name = 'events/event_form.html'

    form_class = EventForm
