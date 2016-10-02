from django.conf.urls import url

from . import views

app_name = 'User'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^$', views.patientList, name='pList'),
    url(r'^$', views.viewProfile, name='vProfile'),
    url(r'^$', views.eventCreate, name='eCreate'),
]