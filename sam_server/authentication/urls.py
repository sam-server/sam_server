from django.conf.urls import patterns, url

from . import views


urlpatterns = patterns('',
    url(r'^register/?$', views.register),
    url(r'^deactivate/(?P<user_id>\d+)?$', views.deactivate)
)

