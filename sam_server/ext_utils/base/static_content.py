import os
import re
from urllib.parse import unquote

from django.conf import settings
from django.http import Http404
import django.contrib.staticfiles.views as static_views

PACKAGE_PATH = re.compile(r'^.*(packages/.*)')


def rewrite_package_path(path):
    """
    Rewrites a package path so that it is resolvable in the
    content directories.

    In production this rewriting is performed by nginx
    """
    path = os.path.normpath(unquote(path))
    match = PACKAGE_PATH.match(path)
    if match:
        # not a package path, return path unchanged
        return match.group(1)
    return path


def serve_static_content(request, path):
    if not settings.DEBUG:
        raise Http404('static content files not served when not in DEBUG mode')
    path = rewrite_package_path(path)
    response = static_views.serve(request, path)
    response['Content-Cache'] = 'no-store'
    return response


