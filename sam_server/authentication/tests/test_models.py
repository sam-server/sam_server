from django.test import TestCase

from django.db import transaction
from django.db.utils import IntegrityError
from django.core.exceptions import ValidationError

from ..models import User, UserTypeError


class MockCredentials(object):
    def __init__(self, access_token=None):
        self.access_token = access_token
        self.access_token_exipired = False


class BasicUserTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_basic_user(
            username='test_user',
            email='test@example.com',
            password='test_password'
        )

    def tearDown(self):
        self.user.delete()

    def test_create_user(self):
        self.assertEqual(self.user.user_id, 'userpass:test_user')
        with self.assertRaises(ValidationError):
            User.objects.create_basic_user(
                username='an&invalid!username',
                email='an@example.com',
                password='hello world'
            )

    def test_set_password(self):
        self.user.set_password('password')
        self.assertTrue(self.user.check_password('password'))

    def test_cannot_set_credentials(self):
        with self.assertRaises(UserTypeError):
            self.user.set_credential(MockCredentials())

    def test_username_must_be_unique(self):
        with transaction.atomic():
            with self.assertRaises(IntegrityError):
                User.objects.create_basic_user(
                    username='test_user',
                    email='email@email.com',
                    password='password'
                )


class GoogleUserTest(object):

    def setUp(self):
        self.user = User.objects.create_googleplus_user(
            email='test@example.com',
        )

    def tearDown(self):
        self.user.delete()





