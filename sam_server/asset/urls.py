from django.conf.urls import patterns, url

from . import views

urlpatterns = patterns('assets',
    url(r'^$', views.list),
    url(r'^/create$', views.create),

    url(r'^/(?P<asset_id>[\da-fA-F]+)$', views.update_or_view)
)
