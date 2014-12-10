from django.conf.urls import include, patterns, url

from . import views


urlpatterns = patterns('assets',
    url(r'^user/(?P<user_id>\d+)/', include(patterns('assets.user',
        url(r'^$', views.list_user_assets),
        url(r'^asset/(?P<asset_id>[\da-fA-F]+)$', views.asset)
    )))
)
