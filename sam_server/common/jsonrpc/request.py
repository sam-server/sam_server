import json
import logging

from .exceptions import JsonRpcError
from django.http import HttpResponse

JSONRPC_VERSION = "2.0"
CHARSET_PARAM_KEY = 'charset='
CHARSET_PARAM_KEY_LENGTH = len(CHARSET_PARAM_KEY)

## TODO: Remove this
logging.basicConfig(level=logging.DEBUG)


def charset_from_content_type(content_type):
    """
    Returns the charset specified in the CONTENT-TYPE header,
    otherwise assumes 'utf-8'
    """
    charset = 'utf-8'
    params = list(content_type.split(';'))[1:]
    for param in params:
        param = param.strip()
        if param.startswith(CHARSET_PARAM_KEY):
            return param[CHARSET_PARAM_KEY_LENGTH:]
    return charset


class JsonRpcRequest(object):
    def __init__(self, data):
        rpc_version = data.get('jsonrpc', '1.0')
        if rpc_version != JSONRPC_VERSION:
            raise JsonRpcError.invalid_request(
                'Unsupported json rpc version {0}'.format(rpc_version))
        if "method" not in data:
            raise JsonRpcError.invalid_request("No 'method' in request")
        self.data = data

    @classmethod
    def from_http_request(cls, request):
        charset = 'utf-8'
        ct = request.META.get('CONTENT_TYPE', None)
        if ct is None or not ct.startswith('application/json'):
            raise JsonRpcError.invalid_request(
                'Invalid content type {0} on request'
                .format(ct))
        charset = charset_from_content_type(ct)
        try:
            request_body = str(request.body, encoding=charset)
            return cls(json.loads(request_body))
        except (UnicodeDecodeError, ValueError) as e:
            raise JsonRpcError.parse_error(e)

    @property
    def method(self):
        return self.data['method']

    @property
    def params(self):
        return self.data.get('params', [])

    @property
    def id(self):
        return self.data['id']


class JsonRpcResponse(object):
    def __init__(self, request=None, result=None, error=None):
        self.request = request
        if result is not None and error is not None:
            raise ValueError('Both error and result provided on rpc response')
        self.result = result
        if error is not None and not isinstance(error, JsonRpcError):
            raise ValueError('Expected a JsonRpcError, got {0}'.format(error))
        self.error = error

    def to_json(self):
        json = dict()
        if self.request is not None:
            json['id'] = self.request.id
        if self.result is not None:
            json['result'] = self.result
        if self.error is not None:
            json['error'] = self.error.to_json()
        return json

    def to_http_response(self, http_request):
        ## FIXME: Should respect the Accept-Charset request header
        return HttpResponse(
            json.dumps(self.to_json()),
            content_type='application/json; charset=utf-8')
