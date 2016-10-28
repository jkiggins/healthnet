"""HealthNet URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import include, url
from django.contrib import admin
from logIn.views import *

urlpatterns = [

    #login url
    url(r'^$', LoginView.as_view() , name='loginIndex'),
    url(r'^admin/', admin.site.urls),

    # register user url
    url(r'^register/$', Register.as_view(), name='register'),
    # succesful registration url
    url(r'^register/success/$', register_success),
    # where you are sent after login
    url(r'^accounts/profile/$', home),
    # call to logout
    url(r'^logout/$', logout_page, name='logout'),
    url(r'^login/', LoginView.as_view(), name='login'),
    url(r'^user/', include('user.urls')), # User URL
    url(r'emr/', include('emr.urls')),

]
