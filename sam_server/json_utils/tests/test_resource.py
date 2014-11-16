from django.test import TestCase

## User UserResource to perform testing
from authentication.models import User
from authentication.resources import UserResource


class ResourceTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_basic_user(
            email="test@example.com",
            username="test_user",
            password="test_password"
        )

    def tearDown(self):
        self.user.delete()

    def test_to_resource(self):
        r = UserResource()
        json = r.to_json_value(self.user)
        self.assertEqual(json['resource'], "authentication#user")
        self.assertEqual(json['id'], self.user.id)
        self.assertEqual(json['type'], 'userpass')
        self.assertEqual(json['date_joined'], self.user.date_joined.isoformat())
        self.assertEqual(json['last_login'], None)


