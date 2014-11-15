from django.test import TestCase

from ..backends import BasicUserBackend
from ..models import User

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

class TestGoogleBackend(TestCase):
    def setUp(self):
        self.user = User.objects.create_googleplus_user(
        )

