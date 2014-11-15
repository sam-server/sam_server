import importlib
import os

from django.core.exceptions import ImproperlyConfigured

try:
    GOOGLE_AUTHENTICATION = (
        importlib.import_module(os.environ['DJANGO_SETTINGS_MODULE'])
        .GOOGLE_AUTHENTICATION
    )
except (NameError, AttributeError):
    raise ImproperlyConfigured(
        'authentication app requires GOOGLE_AUTH_SETTINGS to be configured'
        'in the main settings module.'
    )
