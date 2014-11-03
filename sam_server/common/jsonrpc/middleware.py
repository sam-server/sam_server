"""
Middleware that processes json rpc requests and handles them
independently of the django urls

"""
import traceback

from .exceptions import JsonRpcError
from .request import JsonRpcRequest, JsonRpcResponse
from .service import Service
from .utils import declared_services, services_urlpattern


class JsonRpcMiddleware(object):
    """
    The JsonRpcMiddleware intercepts any request to '/json'
    and processes them as a json RPC 2.0 call
    """
    def __init__(self, services=None, urlpattern=None):
        self._services = services
        self._urlpattern = urlpattern

    @property
    def services(self):
        if self._services is None:
            self._services = dict()
            for service in declared_services():
                if not isinstance(service, Service):
                    raise TypeError('Not a service: {0}'.format(service))
                self._services[service.name] = service
        return self._services

    @property
    def urlpattern(self):
        if self._urlpattern is None:
            self._urlpattern = services_urlpattern()
        return self._urlpattern

    def resolve_method(self, method):
        """
        Resolve the function which declares the given method
        """
        method_comps = method.split('.')
        if len(method_comps) < 2:
            raise JsonRpcError.invalid_request(
                "method must match [a-z]+\.(.*)")
        service_name = method_comps[0]
        method_name = '.'.join(method_comps[1:])
        try:
            service = self.services[service_name]
        except KeyError:
            raise JsonRpcError.method_not_found(service_name, method_name)
        return service.get_method(method_name)

    def process_request(self, http_request):
        path = http_request.path
        if path.startswith('/'):
            path = path[1:]
        if not self.urlpattern.match(path):
            return None
        ## TODO: Handle OPTIONS request
        if http_request.method != 'POST':
            return None
        rpc_request = None
        try:
            rpc_request = JsonRpcRequest.from_http_request(http_request)
            method = self.resolve_method(rpc_request.method)
            result = method(http_request, rpc_request.params)
            response = JsonRpcResponse(request=rpc_request, result=result)
        except JsonRpcError as e:
            response = JsonRpcResponse(request=rpc_request, error=e)
        http_response = response.to_http_response(http_request)
        return http_response
