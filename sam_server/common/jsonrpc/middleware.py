"""
Middleware that processes json rpc requests and handles them
independently of the django urls

"""
from .exceptions import JsonRpcError
from .request import JsonRpcRequest, JsonRpcResponse
from .utils import root_services_module, services_urlpattern


class JsonRpcMiddleware(object):
    """
    The JsonRpcMiddleware intercepts any request to '/json'
    and processes them as a json RPC 2.0 call
    """

    @property
    def services(self):
        if not hasattr(self, '_services'):
            services_module = root_services_module()

        return self._services

    @property
    def urlpattern(self):
        if not hasattr(self, '_urlpattern'):
            self._urlpattern = services_urlpattern()
        return self._urlpattern

    def call_method(self, foo, rpc_request):
        """
        Call the python function foo with parameters from the rpc request
        """
        raise NotImplementedError('Middleware.call_method')

    def resolve_method(self, method):
        """
        Resolve the function which declares the given method
        """
        ## FIXME: Implement
        raise NotImplementedError('Middleware.resolve_method')

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
            rpc_request = JsonRpcRequest.from_request(
                http_request.body, http_request.META['CONTENT_TYPE'])
            method = resolve_method(rpc_request.method)
            result = self.call_method(method, rpc_method)
            response = JsonRpcResponse(request=rpc_request, result=result)
        except JsonRpcError as e:
            response = JsonRpcResponse(request=rpc_request, error=e)
        return response.to_http_response(request)


