

class JsonRpcError(Exception):
    """
    Represents an error handling a json rpc
    """
    PARSE_ERROR = -32700
    INVALID_REQUEST = -32600
    METHOD_NOT_FOUND = -32601
    INVALID_PARAMS = -32602

    SERVER_ERROR = -32000

    def __init__(self, errcode, message, data=None):
        self.errcode = errcode
        self.message = message
        self.data = data

    @classmethod
    def from_exception(cls, e):
        if isinstance(e, JsonRpcError):
            return cls(e.errcode, e.message, e.data)
        return cls(JsonRpcError.SERVER_ERROR, str(e))

    @classmethod
    def parse_error(cls, e):
        return cls(JsonRpcError.PARSE_ERROR,
                   'Parse error: {0}'.format(e))

    @classmethod
    def invalid_request(cls, reason):
        return cls(JsonRpcError.INVALID_REQUEST,
                   'Invalid request: {0}'.format(reason))

    @classmethod
    def invalid_params(cls, reason):
        return cls(JsonRpcError.INVALID_PARAMS,
                   'Invalid params: {0}'.format(reason))

    @classmethod
    def method_not_found(cls, service_name, method_name):
        return cls(JsonRpcError.METHOD_NOT_FOUND,
                   'No such method: {0}.{1}'
                   .format(service_name, method_name))

    def to_json(self):
        json = {
            'code': self.errcode,
            'message': self.message
        }
        if self.data is not None:
            json['data'] = self.data
        return json
