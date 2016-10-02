from django.conf.urls import url

from . import views

app_name = 'User'
urlpatterns = [
    url(r'^index/$', views.index, name='index'),
    url(r'^patientList/$', views.patientList, name='pList'),
    url(r'^viewProfile/$', views.viewProfile, name='vProfile'),
    url(r'^eventCreate/$', views.eventCreate, name='eCreate'),
]