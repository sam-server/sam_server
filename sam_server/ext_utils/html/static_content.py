
from django.conf import settings
import django.contrib.staticfiles.views as static_views


def serve_html_file(request, path):
    print('serving html link: {0}'.format(path))
    if not settings.DEBUG:
        raise Http404('\'.html\' links not served when in debug mode')
    response = static_views.serve(request, path)
    response['Content-Type'] = 'text/html'
    response['Content-Cache'] = 'no-store'
    return response


