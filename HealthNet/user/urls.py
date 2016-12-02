from django.conf.urls import url

from . import views

app_name = 'user'
urlpatterns = [
    url(r'^registry/$', views.Registry.as_view(), name='registry'),
    url(r'^(?P<pk>[0-9]+)/viewProfile/$', views.viewProfile.as_view(), name='vProfile'),
    url(r'^viewProfile/$', views.viewProfileSelf, name='vProfilec'),
    url(r'^(?P<pk>[0-9]+)/EditEvent/$', views.EditEvent.as_view(), name='eEvent'),
    url(r'^(?P<pk>[0-9]+)/EditEvent/d$', views.EditEvent.post_dependant_fields, name='eEventd'),
    url(r'^(?P<pk>[0-9]+)/ViewEvent/$', views.viewEvent, name='vEvent'),
    url(r'^editProfile/$', views.EditProfile.as_view(), name = 'eProfile'),
    url(r'^editProfile/d$', views.EditProfile.dependand_post, name = 'eProfiled'),
    url(r'^createEvent/$', views.createEvent, name='cEvent'),
    url(r'^createEvent/d$', views.createEvent, {'depend': True}, name='veEventd'),
    url(r'^dashboard/', views.dashboardView, name='dashboard'),
    url(r'^(?P<pk>[0-9]+)/dismissNote$', views.dismissNote, name='disnote'),
    url(r'^(?P<pk>[0-9]+)/note$', views.viewNote, name='note')
    ]