from django.conf.urls import url

from . import views

app_name = 'user'
urlpatterns = [
    url(r'^registry/$', views.Registry.as_view(), name='registry'),
    url(r'^(?P<pk>[0-9]+)/viewProfile/$', views.viewProfile, name='vProfile'),
    url(r'^viewProfile/$', views.viewProfileSelf, name='vProfilec'),
    url(r'^(?P<pk>[0-9]+)/EditEvent/$', views.editEvent, name='eEvent'),
    url(r'^(?P<pk>[0-9]+)/EditEvent/d$', views.editEvent, {'depend': True}, name='eEventd'),
    url(r'^(?P<pk>[0-9]+)/ViewEvent/$', views.viewEvent, name='vEvent'),
    url(r'^(?P<pk>[0-9]+)/editProfile/$', views.editProfile, name = 'eProfile'),
    url(r'^(?P<pk>[0-9]+)/editProfile/d$', views.editProfile, {'depend': True}, name = 'eProfile'),
    url(r'^createEvent/$', views.createEvent, name='cEvent'),
    url(r'^(?P<pk>[0-9]+)/cancleEvent/$', views.cancleEvent, name='delEvent'),
    url(r'^message/', views.sendMessage.as_view(), name='sendMessage'),
    url(r'^(?P<pk>[0-9]+)/message/$', views.viewMessage, name='viewMessage'),
    url(r'^createEvent/d$', views.createEvent, {'depend': True}, name='veEventd'),
    url(r'^dashboard/', views.dashboardView, name='dashboard'),
    url(r'^(?P<pk>[0-9]+)/adminDash/', views.hosAdDashView, name='hosDash'),
    url(r'nurseDash/', views.nurseDashView, name='nurseDash'),
    url(r'^(?P<pk>[0-9]+)/dismissNote$', views.dismissNote, name='disnote'),
    url(r'^stats$', views.viewStats, name='stats'),
    url(r'^(?P<pk>[0-9]+)/approval$', views.approval, name='approval'),
    url(r'^CSV/', views.viewCSV, name="vCSV"),
    url(r'^(?P<file>(doctor|nurse|patient)).csv', views.downloadCsv, name="dcsv")
]