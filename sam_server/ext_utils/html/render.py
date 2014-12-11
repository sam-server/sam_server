# Render a html file at a given location, using pystache

import pystache
from pystache.parser import parse

from django.conf import settings

_PRECOMPILED_TEMPLATES = dict()

# Use ASP style delimiters so that they don't conflict with the
# native
DELIMITERS = ('<%', '%>')


def _load_template(path_to_template):
    """
    Loads the template from the given location on the file system
    parsed templates are cached for future access

    Does not cache compiled templates if django is in DEBUG mode
    """
    if settings.DEBUG or path_to_template not in _PRECOMPILED_TEMPLATES:
        with open(path_to_template) as f:
            template_str = f.read()
        _PRECOMPILED_TEMPLATES[path_to_template] = parse(template_str, delimiters=DELIMITERS)
    return _PRECOMPILED_TEMPLATES[path_to_template]


def render(path_to_template, context=None, **kwargs):
    template = _load_template(path_to_template)
    return pystache.render(template, context=context, **kwargs)




