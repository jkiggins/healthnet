from django.conf.urls import url

from . import views

app_name = 'User'
urlpatterns = [
    url(r'^index/$', views.index, name='index'),
    url(r'^patientList/$', views.patientList, name='pList'),
    url(r'^(?P<pk>[0-9]+)/viewProfile/$', views.viewProfile, name='vProfile'),
    url(r'^(?P<ut>p|d)/(?P<pk>[0-9]+)/viewCalendar/$', views.viewCalendar, name='vCalendar'),
    url(r'^(?P<pk>[0-9]+)/viewEditEvent/$', views.ViewEditEvent.as_view(), name='veEvent'),
    url(r'^editProfile/$', views.EditProfile.as_view(), name = 'eProfile'),
    url(r'^createEvent/$', views.CreateEvent.as_view(), name='cEvent'),
    url(r'^dashboard/', views.dashboardView, name='dashboard')
]