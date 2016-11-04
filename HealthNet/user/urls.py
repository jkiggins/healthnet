from django.conf.urls import url

from . import views

app_name = 'user'
urlpatterns = [
    url(r'^patientList/$', views.patientList, name='pList'),
    url(r'^(?P<ut>doctor|patient)/(?P<pk>[0-9]+)/viewProfile/$', views.viewProfile, name='vProfile'),
    url(r'^(?P<pk>[0-9]+)/viewEditEvent/$', views.ViewEditEvent.as_view(), name='veEvent'),
    url(r'^(?P<pk>[0-9]+)/viewEditEvent/d$', views.ViewEditEvent.post_dependant_fields, name='veEventd'),
    url(r'^editProfile/$', views.EditProfile.as_view(), name = 'eProfile'),
    url(r'^createEvent/$', views.CreateEvent.as_view(), name='cEvent'),
    url(r'^createEvent/d$', views.CreateEvent.post_dependant_fields, name='veEventd'),
    url(r'^dashboard/', views.dashboardView, name='dashboard'),
    url(r'^logout/', views.logout, name='logout'),
]