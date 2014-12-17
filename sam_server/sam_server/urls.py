import os
from django.conf import settings

from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.contrib import admin

from django.http import HttpResponse, HttpResponseRedirect
from django.core.context_processors import csrf

from ext_utils.html import render, serve_html_file
from ext_utils.dart import serve_dart_file
from ext_utils.js import serve_js_file
from ext_utils.css import serve_css_file

import artist.urls
import authentication.urls
import asset.urls

TEMPLATES_DIR = os.path.join(settings.BASE_DIR, 'sam_server', 'templates')


def serve_index(request):
    """
    Serves the `index.html` from the root of the template
    """
    if request.user.is_anonymous():
        return HttpResponseRedirect('/auth/login')
    context = {
        'init_url':  '/assets/user/{0}'.format(request.user.id),
    }
    context.update(csrf(request))
    rendered_template = render('index.html', context)
    return HttpResponse(rendered_template)


## Hacks to get dart working in the development environment
## TODO: Should be handled better than this.
if settings.DEBUG:
    urlpatterns = patterns('',
        url(r'^(?P<path>.*?\.dart)$', serve_dart_file),
        url(r'^(?P<path>.*?\.html)$', serve_html_file),
        url(r'^(?P<path>.*?\.js)$', serve_js_file),
        url(r'^(?P<path>.*?\.css)$', serve_css_file),
    )
else:
    urlpatterns = patterns('')

urlpatterns += patterns('',
    # Examples:
    # url(r'^$', 'sam_server.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^$', serve_index),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^artist/', include(artist.urls)),
    url(r'^auth/', include(authentication.urls)),
    url(r'^assets/', include(asset.urls))
)

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
