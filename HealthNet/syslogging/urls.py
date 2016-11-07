from django.conf.urls import url

from . import views

app_name = 'syslogging'
urlpatterns = [
    url(r'^$', views.view_log.as_view(), name='viewlog')
]
