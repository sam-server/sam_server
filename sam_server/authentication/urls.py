from django.conf.urls import patterns, url

from . import views

urlpatterns = patterns('',
    url(r'^google/signin', views.googplus_signin),
    url(r'^register/?$', views.register),
    url(r'^signin/?$', views.signin)
)
