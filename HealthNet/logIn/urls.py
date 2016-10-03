from django.conf.urls import url
from django.core.urlresolvers import reverse




from . import views

app_name = 'logIn'
urlpatterns = [
    url(r'^$', views.index, name='index'), # connects to index
    url(r'^authenticate/', views.authenticate, name='authenticate'),
    url(r'^Register/', views.Register.as_view(success_url='/index/'), name='patientIndex'), # TODO: make sure this goes to the user index
    url(r'^test/', views.testView, name="test")
]
