from django.conf.urls import url

from . import views

app_name = 'emr'
urlpatterns = [
    url(r'^(?P<pk>[0-9]+)/', views.index, name='index')
]