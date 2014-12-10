from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.contrib import admin
import django.contrib.staticfiles.views as staticfiles

from . import settings
import artist.urls
import authentication.urls
import asset.urls


def serve_dart_file(request, path):
    ## Always serve the compiled js file
    response = staticfiles.serve(request, path)
    response['Content-Type'] = 'application/dart'
    return response


def serve_package(request, path):
    response = staticfiles.serve(request, path)
    if path.endswith('.dart'):
        response['Content-Type'] = 'application/dart'
    return response


def serve_css(request, path):
    print('Serving css file: {0} '.format(path))
    return staticfiles.serve(request, path)

## Hacks to get dart working in the development environment
## TODO: Should be handled better than this.
if settings.DEBUG:
    urlpatterns = patterns('',
        url(r'^.*(?P<path>packages/.*)$', serve_package),
        url(r'^(?P<path>.*?\.dart)$', serve_dart_file),
        url(r'^(?P<path>css/.*\.css)$', serve_css),
    )
else:
    urlpatterns = patterns('')

urlpatterns += patterns('',
    # Examples:
    # url(r'^$', 'sam_server.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^artist/', include(artist.urls)),
    url(r'^auth/', include(authentication.urls)),
    url(r'^assets/', include(asset.urls))
)

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

