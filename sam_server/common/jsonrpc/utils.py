import re
from importlib import import_module
from django.conf import LazySettings
from django.core.exceptions import ImproperlyConfigured

settings = LazySettings()


def root_services_module():
    """
    Load the root services module configuration from the ROOT_SERVICESCONF
    entry in the django settings.
    """
    try:
        return import_module(settings.ROOT_SERVICESCONF)
    except AttributeError:
        raise ImproperlyConfigured("ROOT_SERVICESCONF not found in settings")


def declared_services():
    """
    Get the services from the root services module
    """
    services_module = root_services_module()
    if not hasattr(services_module, 'services'):
        raise ImproperlyConfigured(
            "Expected 'services' attribute in {0}"
            .format(services_module.__name__))
    return list(services_module.services)


def declared_methods(module):
    """
    Get the 'methods' declaration from the given module
    """
    if not hasattr(module, 'methods'):
        raise ImproperlyConfigured(
            "Epxpected 'methods' attribute in {0}"
            .format(module.__name__))
    return list(module.methods)


def root_url_module():
    """
    Returns the module configured in settings via the django standard
    variable ROOT_URLCONF
    """
    try:
        return import_module(settings.ROOT_URLCONF)
    except AttributeError:
        raise ImproperlyConfigured("ROOT_URLCONF not found in settings")


def services_urlpattern():
    url_module = root_url_module()
    if not hasattr(url_module, 'services_urlpattern'):
        raise ImproperlyConfigured(
            "Expected 'services_urlpattern' attribute in {0}"
            .format(url_module.__name__))
    return re.compile(url_module.services_urlpattern)
