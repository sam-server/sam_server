
from django.conf import settings
from django.contrib.staticfiles import views


def serve_dart_file(request, path):
    print(path)
    if not settings.DEBUG:
        raise Http404('\'.dart\' files not served when not in DEBUG mode')
    response = views.serve(request, path)
    response['Content-Type'] = 'application/dart'
    response['Content-Cache'] = 'no-store'
    return response
