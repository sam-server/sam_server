import importlib

from django.test import TestCase, RequestFactory
from django.http import HttpResponse
from django.contrib.auth.models import AnonymousUser

from ..decorators import authorization_required
from ..models import User

from ..testing import make_basic_authorization_header, load_test_credentials

from django.conf import settings

session_engine = importlib.import_module(settings.SESSION_ENGINE)
SESSION_COOKIE_NAME = settings.SESSION_COOKIE_NAME


@authorization_required
def test_view(request):
    return HttpResponse('OK', 200)


class TestAuthorization(TestCase):
    def setUp(self):
        self.credentials = load_test_credentials()
        self.basic_user = User.objects.create_basic_user(
            email='test@example.com',
            username='test_user',
            password='test_password'
        )
        self.google_user = User.objects.create_googleplus_user(self.credentials)

    def tearDown(self):
        self.basic_user.delete()

    def create_test_request(self, auth_header):
        rf = RequestFactory()
        request = rf.get('/test')
        request.META['HTTP_AUTHORIZATION'] = auth_header
        request.user = AnonymousUser()

        ## Set up the request's session
        s = session_engine.SessionStore()
        s.save()
        request.session = s
        request.COOKIES[SESSION_COOKIE_NAME] = s.session_key

        return request

    def test_basic_authorization(self):
        request = self.create_test_request(
            make_basic_authorization_header('test_user', 'test_password')
        )
        response = test_view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(request.user, self.basic_user)

        request = self.create_test_request(
            make_basic_authorization_header('invalid_user', 'invalid_password')
        )
        response = test_view(request)
        self.assertEqual(response.status_code, 403)

    def test_google_authorization(self):
        request = self.create_test_request(
            'Bearer {0}'.format(self.credentials.access_token)
        )
        response = test_view(request)
        self.assertEqual(response.status_code, 200)
