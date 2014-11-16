import base64

from django.test import TestCase

from ..backends import BasicUserBackend, GoogleUserBackend
from ..models import User
from ..testing import load_test_credentials


class TestBasicUserBackend(TestCase):
    def setUp(self):
        self.user = User.objects.create_basic_user(
            'test_user',
            'test@example.com',
            'test_password'
        )

    def tearDown(self):
        self.user.delete()

    def test_get_user(self):
        backend = BasicUserBackend()
        self.assertEqual(
            self.user.id,
            backend.get_user(self.user.id).id
        )

    def test_basic_user_backend_authentication(self):
        backend = BasicUserBackend()
        auth_user = backend.authenticate(username='test_user',
                                         password='test_password')
        self.assertEqual(auth_user, self.user)

        mismatch_pwd = backend.authenticate(username='test_user',
                                            password='hello')
        self.assertIsNone(mismatch_pwd)

        not_exist = backend.authenticate(username='non_existent_user',
                                         password='test_password')
        self.assertIsNone(not_exist)

    def test_header_authorization(self):
        backend = BasicUserBackend()
        userpass = 'test_user:test_password'.encode('ascii')
        encoded = str(base64.b64encode(userpass), encoding='ascii')
        header = 'Basic {0}'.format(encoded)
        auth_user = backend.authenticate(auth_header=header)
        self.assertEqual(auth_user, self.user)


class TestGoogleBackend(TestCase):
    def setUp(self):
        self.credentials = load_test_credentials()
        self.user = User.objects.create_googleplus_user(self.credentials)

    def test_get_user(self):
        backend = GoogleUserBackend()
        self.assertEqual(
            self.user.id,
            backend.get_user(self.user.id).id
        )

    def test_id_token_authentication(self):
        backend = GoogleUserBackend()
        id_token = {
            'aud': self.credentials.id_token['aud'],
            'sub': self.credentials.id_token['sub']
        }
        auth_user = backend.authenticate(id_token=id_token)
        self.assertEqual(auth_user, self.user)

        invalid_audience_token = {
            'aud': 'invalid_audience',
            'sub': self.credentials.id_token['sub']
        }
        auth_user = backend.authenticate(id_token=invalid_audience_token)
        self.assertIsNone(auth_user)

        non_existent_subscriber_token = {
            'aud': self.credentials.id_token['aud'],
            'sub': 12345
        }
        auth_user = backend.authenticate(id_token=non_existent_subscriber_token)
        self.assertIsNone(auth_user)

    def test_bearer_authentication(self):
        backend = GoogleUserBackend()
        auth_header = 'Bearer {0}'.format(self.credentials.access_token)
        auth_user = backend.authenticate(auth_header=auth_header)
        self.assertEqual(auth_user, self.user)





