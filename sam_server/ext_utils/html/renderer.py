# Render a html file at a given location, using pystache
import re
import os

from pystache.parser import parse
from pystache.renderer import Renderer

from django.conf import settings
from django.http import HttpResponse

# Use ASP style delimiters so that they don't conflict with the
# native
DELIMITERS = ('{%', '%}')

_settings_key = re.compile('^[A-Z][A-Z_]*$')
APP_CONTEXT = (
    lambda settings: {
        k: getattr(settings, k)
        for k in dir(settings)
        if _settings_key.match(k) is not None
    })(settings)

_PRECOMPILED_TEMPLATES = dict()

_renderer = Renderer()


def _load_template(path_to_template):
    """
    Loads the template from the given location on the file system
    parsed templates are cached for future access

    Does not cache compiled templates if django is in DEBUG mode
    """
    webapp_root = settings.WEBAPP_ROOT
    """
    if not settings.DEBUG:
        webapp_root = os.path.join(webapp_root, 'build/')
    else:
        webapp_root = os.path.join(webapp_root, 'web/')
    """
    normpath = os.path.normpath(path_to_template)
    abspath = os.path.join(webapp_root, normpath)

    if settings.DEBUG or path_to_template not in _PRECOMPILED_TEMPLATES:
        with open(abspath) as f:
            template_str = f.read()
        _PRECOMPILED_TEMPLATES[path_to_template] = parse(template_str, delimiters=DELIMITERS)
    return _PRECOMPILED_TEMPLATES[path_to_template]


def render(path_to_template, context=None, **kwargs):
    template = _load_template(path_to_template)
    rendered_file = _renderer.render(template, APP_CONTEXT, context, **kwargs)
    response = HttpResponse(rendered_file)
    if settings.DEBUG:
        response['Cache-Control'] = 'no-store'
    return response





