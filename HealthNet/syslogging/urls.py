from django.conf.urls import url

from . import views

app_name = 'syslogging'
urlpatterns = [
    url(r'^$', views.viewSelfEmr, name='viewlog')

]