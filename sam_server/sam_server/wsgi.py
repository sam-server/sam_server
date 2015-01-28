"""
WSGI config for sam_server project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/howto/deployment/wsgi/
"""

import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sam_server.settings")

from django.core.wsgi import get_wsgi_application
from django.conf import settings
from django.utils import autoreload

application = get_wsgi_application()


HAS_WSGI = False
try:
    import uwsgi
    from uwsgidecorators import timer

    @timer(3)
    def change_code_graceful_reload(sig):
        if settings.DEBUG and autoreload.code_changed():
            uwsgi.reload()
except ImportError:
    ## uwsgi module only available when running
    ## as the uwsgi server
    pass
