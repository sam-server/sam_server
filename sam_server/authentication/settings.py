from django.core.exceptions import ImproperlyConfigured
from django.conf import settings

try:
    GOOGLE_AUTHENTICATION = settings.GOOGLE_AUTHENTICATION
except (NameError, AttributeError):
    raise ImproperlyConfigured(
        'authentication app requires GOOGLE_AUTH_SETTINGS to be configured'
        'in the main settings module.'
    )
