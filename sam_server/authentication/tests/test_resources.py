from django.test import TestCase
from ..models import User
from ..testing import load_test_credentials
from .. import resources


class ResourcesTest(TestCase):
    def setUp(self):
        self.basic_user = User.objects.create_basic_user(
            username='test_user',
            email='test@example.com',
            password='test_password'
        )
        self.goog_user = User.objects.create_googleplus_user(
            load_test_credentials()
        )

    def tearDown(self):
        self.basic_user.delete()
        self.goog_user.delete()

    def test_user_resource(self):
        r = resources.UserResource()

        basic_json = r.to_json(self.basic_user)
        self.assertEqual(
            basic_json,
            {
                'kind': 'authentication#user',
                'id': self.basic_user.id,
                'type': 'userpass',
                'username': 'test_user',
                'date_joined': self.basic_user.date_joined.isoformat(),
            })

        goog_user_json = r.to_json(self.goog_user)
        self.assertEqual(
            goog_user_json,
            {
                'kind': 'authentication#user',
                'type': 'googplus',
                'id': self.goog_user.id,
                'goog_id': self.goog_user.auth_identifier,
                'date_joined': self.goog_user.date_joined.isoformat(),
            })
