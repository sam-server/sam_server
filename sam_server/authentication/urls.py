from django.conf.urls import patterns, url

from . import views


urlpatterns = patterns('',
    url(r'^login$', views.login_user),
    #url(r'^register$', views.register_user)
    url(r'^register$', views.register),
)

