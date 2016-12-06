from django.conf.urls import url
from . import views

app_name = 'emr'
urlpatterns = [
    url(r'^$', views.viewSelfEmr, name='vsemr'),
    url(r'^(?P<pk>[0-9]+)/$', views.viewEMR, name='vemr'),
    url(r'^(?P<pk>[0-9]+)/export$', views.exportEMR, name='eemr'),
    url(r'^(?P<pk>[0-9]+)/item$', views.viewEmrItem, name='vemri'),
    url(r'^(?P<pk>[0-9]+)/a$', views.emrActionAjax, name='action_item_ajax'),
    url(r'^(?P<pk>[0-9]+)/editItem$', views.editEmrItem, name='eemrItem'),
    url(r'^(?P<pk>[0-9]+)/editProfile$', views.editEmrProfile, name='eprofile'),
    url(r'^(?P<pk>[0-9]+)/createNote$', views.EMRItemCreate, {'type': 'note'}, name='citem'),
    url(r'^(?P<pk>[0-9]+)/createTest$', views.EMRItemCreate, {'type': 'test'}, name='ctest'),
    url(r'^(?P<pk>[0-9]+)/createVitals$', views.EMRItemCreate, {'type': 'vitals'}, name='cvitals'),
    url(r'^(?P<pk>[0-9]+)/createPrescript$', views.EMRItemCreate, {'type': 'prescription'}, name='cpre'),
    url(r'^(?P<pk>[0-9]+)/admitDischarge$', views.AdmitDishchargeView.as_view(), name='admitdischarge'),
    url(r'^(?P<pk>[0-9]+)/testMedia$', views.serveTestMedia, name='testmedia')
]

