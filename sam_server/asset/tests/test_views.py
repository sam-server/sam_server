import json
from operator import itemgetter
from django.test import TestCase, RequestFactory

from authentication.models import User

from ..models import Asset


class ViewsTest(TestCase):

    def setUp(self):
        self.rf = RequestFactory()
        self.user1 = User.objects.create_basic_user(
            username='test_user',
            email='user@example.com',
            password='password'
        )
        self.user2 = User.objects.create_basic_user(
            username='test_user2',
            email='user2@example.com',
            password='password'
        )
        self.asset1 = Asset(
            user=self.user1,
            name='asset1',
            description='asset belonging to user 1',
        )
        self.asset1.save()
        self.asset2 = Asset(
            user=self.user2,
            name='asset2',
            description='asset belonging to user 2'
        )
        self.asset2.save()

    def tearDown(self):
        self.user1.delete()
        self.user2.delete()
        self.asset1.delete()
        self.asset2.save()

    def test_asset(self):
        url = (
            '/assets/user/{0}/asset/{1}'
            .format(self.user1.id, self.asset1.id.hex)
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        body = json.loads(str(response.content, encoding='utf-8'))
        self.assertEqual(body['id'], self.asset1.id.hex)

    def test_list_assets(self):
        """
        Lists all assets associated with the given user
        """
        ## TODO: Pagination
        url = (
            '/assets/user/{0}'
            .format(self.user1.id)
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        body = json.loads(str(response.content, encoding='utf-8'))
        ids = list(map(itemgetter('id'), body))
        self.assertEqual(ids, [self.asset1.id.hex])








