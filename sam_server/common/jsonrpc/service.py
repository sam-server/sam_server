import re
from .exceptions import JsonRpcError

SERVICE_NAME = re.compile(r'[a-z]+', re.IGNORECASE)


class Service(object):
    def __init__(self, name, methods):
        if SERVICE_NAME.match(name) is None:
            raise ValueError(
                'Service name must match {0}'
                .format(SERVICE_NAME.pattern))
        self.name = name
        self.methods = dict()
        for method in methods:
            if not isinstance(method, Method):
                raise TypeError('Not a Method: {0}'.format(method))
            method.service_name = name
            self.methods[method.name] = method

    def get_method(self, method_name):
        try:
            return self.methods[method_name]
        except KeyError:
            raise JsonRpcError.method_not_found(self.name, method_name)

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, o):
        return isinstance(o, Service) and o.name == self.name


class Method(object):
    def __init__(self, name, func):
        self.name = name
        self.func = func
        self.service_name = None

    def __call__(self, http_request, params):
        try:
            if params is list:
                return self.function(http_request, *params)
            elif params is map:
                return self.function(http_request, **params)
            else:
                raise JsonRpcError.invalid_params('Expected a list or dict')
        except ValueError as e:
            raise JsonRpcError.invalid_params(str(e))

    def __str__(self):
        return '{0.service_name}.{0.name}'.format(self)
