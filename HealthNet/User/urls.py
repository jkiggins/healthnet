from django.conf.urls import url

from . import views

app_name = 'User'
urlpatterns = [
    url(r'^index/$', views.index, name='index'),
    url(r'^patientList/$', views.patientList, name='pList'),
    url(r'^(?P<pk>[0-9]+)/viewProfile/$', views.viewProfile, name='vProfile'),
    url(r'^(?P<pk>[0-9]+)/eventCreate/$', views.eventCreate, name='eCreate'),
    url(r'^(?P<pk>[0-9]+)/dashboard', views.dashboardView, name='dashboard')
]