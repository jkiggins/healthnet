from django.conf.urls import url

from . import views

app_name = 'emr'
urlpatterns = [
    url(r'^', views.viewEMR.as_view(), name='vsemr'),
    url(r'^(?P<pk>[0-9]+)/', views.viewEMR.as_view(), name='vemr'),
    url(r'^(?P<pk>[0-9]+)/viewItem', views.viewEMRItem, name='vemrItem'),
    url(r'^(?P<pk>[0-9]+)/createItem', views.viewEMRItem, name='citem'),
    url(r'^(?P<pk>[0-9]+)/createTest', views.viewEMRItem, name='ctest'),
url(r'^(?P<pk>[0-9]+)/createVitals', views.viewEMRItem, name='cvitals'),
    url(r'^(?P<pk>[0-9]+)/admit', views.viewEMRItem, name='admit'),
    url(r'^(?P<pk>[0-9]+)/discharge', views.viewEMRItem, name='discharge')
]

