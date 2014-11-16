import json

from django.test import TestCase, RequestFactory
from ..middleware import JsonRequestMiddleware


class JsonRequestMiddlewareTest(TestCase):
    def setUp(self):
        self.rf = RequestFactory()
        self.middleware = JsonRequestMiddleware()

    def test_should_handle_json_request(self):
        body = {"param1": "value1"}
        request = self.rf.post('/', json.dumps(body),
                               content_type="application/json; charset=utf-8")
        self.middleware.process_request(request)
        self.assertEqual(request.JSON, body)

    def test_should_handle_non_json_request(self):
        request = self.rf.get('/')
        self.middleware.process_request(request)
        self.assertIsNone(request.JSON)
