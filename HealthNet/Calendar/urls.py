from django.conf.urls import url

from . import views

app_name = 'Calendar'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^(?P<event_id>[0-9]+)/$', views.detail, name='detail'),
    url(r'^create/$', views.CreateEvent.as_view(success_url="/events/"), name='create'),
    url(r'^edit/(?P<pk>[0-9]+)/$', views.EditEvent.as_view(success_url="/events/"), name='edit')
]
