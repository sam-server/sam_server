import json
import re

from django.test import TestCase
from django.test.client import RequestFactory

from .exceptions import JsonRpcError
from .request import JsonRpcRequest, JsonRpcResponse
from .middleware import JsonRpcMiddleware


class ExceptionsTestCase(TestCase):
    def test_error_to_json(self):
        err = JsonRpcError(0, "message", data=None)
        json = err.to_json()
        self.assertEquals(json, {"code": 0, "message": "message"})


class RequestTestCase(TestCase):

    def setUp(self):
        self.rf = RequestFactory()

    def get_post_request(self, json_body):
        return self.rf.post(
            '/json', json.dumps(json_body),
            content_type='application/json; charset=utf-8'
        )

    def test_request_parse(self):
        body = {
            "jsonrpc": "2.0",
            'method': 'Test.method',
            'params': ['param1', 'param2'],
            'id': 234
        }
        http_request = self.get_post_request(body)
        rpc_request = JsonRpcRequest.from_http_request(http_request)

        self.assertEqual(rpc_request.method, 'Test.method')
        self.assertEqual(rpc_request.params, ['param1', 'param2'])
        self.assertEqual(rpc_request.id, 234)

        with self.assertRaises(JsonRpcError):
            body = {"method": 'Test.method', "params": ['param1'], "id": 234}
            http_request = self.get_post_request(body)
            JsonRpcRequest.from_http_request(http_request)

    def test_response_json(self):
        rpc_request = JsonRpcRequest({
            'jsonrpc': "2.0",
            'method': 'Test.method',
            'params': ['param1', 'param2'],
            'id': 234
        })
        result_response = JsonRpcResponse(request=rpc_request, result=4)
        json = result_response.to_json()
        self.assertEqual(json, {'id': 234, 'result': 4})

        err = JsonRpcError(0, 'message')
        err_response = JsonRpcResponse(request=rpc_request, error=err)
        self.assertEqual(
            err_response.to_json(),
            {"id": 234, 'error': err.to_json()}
        )

class TestMiddleware(TestCase):

    class MockMethod:
        def __init__(self):
            self.method_name = 'mock_method'

        def __call__(self, http_request, params):
            return params[0] + params[1]

    class MockService:
        def __init__(self):
            self.service_name = 'Test'

        def get_method(self, method_name):
            return TestMiddleware.MockMethod()

    def setUp(self):
        self.middleware = JsonRpcMiddleware(
            urlpattern=re.compile(r'^json/?$'),
            services={'Test': TestMiddleware.MockService()}
        )
        self.rf = RequestFactory()

    def set_up_post_request(self, request_body):
        return self.rf.post()

    def test_ignore_request(self):
        ## Should ignore requests that don't hit the JSON endpoint
        self.assertIsNone(
            self.middleware.process_request(self.rf.post('/not_json')))
        # Should ignore requests that aren't POST
        self.assertIsNone(
            self.middleware.process_request(self.rf.get('/json')))

    def test_handle_request(self):
        body = {
            'jsonrpc': '2.0',
            'id': 234,
            'method': 'Test.method',
            'params': [4, 5]
        }
        http_request = self.rf.post(
            '/json', json.dumps(body),
            content_type='application/json; charset=utf-8;')
        response = self.middleware.process_request(http_request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response['CONTENT-TYPE'],
            'application/json; charset=utf-8')
        content = json.loads(str(response.content, 'utf-8'))
        self.assertEqual(content, {'id': 234, 'result': 9})
