from django.conf.urls import url

from . import views

app_name = 'emr'
urlpatterns = [
    url(r'^(?P<pk>[0-9]+)/', views.index, name='index')
    url(r'^create/$', views.CreateEMR.as_view(success_url="/emr/"), name='create'),
    url(r'^edit/$', views.EditEMR.as_view(success_url="/emr/"), name='edit'),
]