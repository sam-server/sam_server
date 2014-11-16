
from sam_server.settings import DEBUG
from django.conf.urls import patterns, url


from . import views


urlpatterns = patterns('',
    url(r'^(?P<handle>[\w-]+)$', views.profile_by_handle),
    url(r'^$', views.profile),
)
