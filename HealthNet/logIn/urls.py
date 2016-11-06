from django.conf.urls import url
from django.core.urlresolvers import reverse




from . import views

app_name = 'logIn'
urlpatterns = [
    #url(r'^$', views.index, name='index'), # connects to index
    #url(r'^authenticate/', views.authenticate, name='authenticate'),
    #url(r'^Register/', views.Register.as_view(success_url='/index/'), name='patientIndex'), # TODO: make sure this goes to the user index
    #url(r'^test/', views.testView, name="test")
    url(r'^register/', views.Register, name='register'),
    url(r'^userSelect/', views.UserSelect.as_view(), name='userSelect'),
    url(r'^doctorRegister/', views.DoctorRegister.as_view(), name='doctorRegister'),
    url(r'^nurseRegister/', views.NurseRegister.as_view(), name='nurseRegister'),
    #url(r'^complete/', views.RegistrationCompletion, name='registrationCompletion'),
]
