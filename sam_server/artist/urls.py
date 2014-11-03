
from sam_server.settings import DEBUG
from django.conf.urls import patterns, url


from . import views


urlpatterns = patterns('',
    url(r'^(?P<artist_id>[a-zA-Z0-9_-]+)$', views.profile),
    url(r'^(?P<artist_id>[a-zA-Z0-9_-]+)/dashboard/$', views.dashboard),
)
