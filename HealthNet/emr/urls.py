from django.conf.urls import url

from . import views

app_name = 'emr'
urlpatterns = [
    url(r'^/', views.viewSelfEMR, name='vsemr'),
    url(r'^(?P<pk>[0-9]+)/', views.viewEMR, name='vemr'),
    url(r'^(?P<pk>[0-9]+)/viewItem', views.viewEMRItem, name='vemrItem'),
]