from django.conf.urls import url
from . import views

app_name = 'emr'
urlpatterns = [
    url(r'^$', views.viewSelfEmr, name='vsemr'),
    url(r'^(?P<pk>[0-9]+)/$', views.viewEMR.as_view(), name='vemr'),
    url(r'^(?P<pk>[0-9]+)/v$', views.emrItemAjax, name='vemr_item_ajax'),
    url(r'^(?P<pk>[0-9]+)/editItem$', views.EditEmrItem.as_view(), name='eemrItem'),
    url(r'^(?P<pk>[0-9]+)/editProfile$', views.editEmrProfile, name='eprofile'),
    url(r'^(?P<pk>[0-9]+)/createItem$', views.EMRItemCreate.as_view(type='item'), name='citem'),
    url(r'^(?P<pk>[0-9]+)/createTest$', views.EMRItemCreate.as_view(type='test'), name='ctest'),
    url(r'^(?P<pk>[0-9]+)/createVitals$', views.EMRItemCreate.as_view(type='vitals'), name='cvitals'),
    url(r'^(?P<pk>[0-9]+)/createPrescript$', views.EMRItemCreate.as_view(type='prescription'), name='cpre'),
    url(r'^(?P<pk>[0-9]+)/admitDischarge$', views.AdmitDishchargeView.as_view(), name='admitdischarge'),
    url(r'^(?P<pk>[0-9]+)/testMedia$', views.serveTestMedia, name='testmedia')
]

