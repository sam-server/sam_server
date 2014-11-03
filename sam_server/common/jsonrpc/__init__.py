from types import ModuleType

from .service import Service, Method
from .utils import declared_methods


def service(service_name, service_module):
    """
    Defines a service with the given name, and methods
    from the specified module
    """
    if not isinstance(service_module, ModuleType):
        raise ValueError('Not a module: {0}'.format(service_module))
    service_methods = declared_methods(service_module)
    return Service(service_name, service_methods)


def method(method_name, callable):
    if not hasattr(callable, '__call__'):
        raise ValueError(
            'Not a callable object: {0}'
            .format(callable))
    return Method(method_name, callable)
