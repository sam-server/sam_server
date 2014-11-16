from django.test import TestCase

from django.db import transaction
from django.db.utils import IntegrityError
from django.core.exceptions import ValidationError

from ..models import User, UserTypeError
from ..testing import load_test_credentials


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
        self.assertTrue(
            User.objects.natural_key_exists(User.Type.BASIC, 'test_user')
        )
        self.assertFalse(
            User.objects.natural_key_exists(User.Type.BASIC, 'non-existent')
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


class GoogleUserTest(TestCase):

    def setUp(self):
        self.credentials = load_test_credentials()
        self.user = User.objects.create_googleplus_user(self.credentials)

    def tearDown(self):
        self.user.delete()

    def test_create_user(self):
        ident = str(self.credentials.id_token['sub'])
        self.assertEqual(self.user.user_id, 'googplus:{0}'.format(ident))
        self.assertEqual(self.user.email, self.credentials.id_token['email'])
        self.assertEqual(self.user.email_verified, True)

        self.assertTrue(
            User.objects.natural_key_exists(User.Type.GOOGLEPLUS, ident)
        )
        self.assertFalse(
            User.objects.natural_key_exists(User.Type.GOOGLEPLUS, '1')
        )

    def test_cannot_set_password(self):
        with self.assertRaises(UserTypeError):
            self.user.set_password('test_password')
