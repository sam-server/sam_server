from django.test import TestCase
from django.conf import settings

from common.currency import MoneyAmount
from authentication.models import User
from asset.models import Asset

class ModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_basic_user(
            username='test_user',
            email='user@example.com',
            password='password'
        )
        self.asset = Asset(
            user=self.user,
            name='test_asset')
        self.asset.save()

    def tearDown(self):
        self.user.delete()
        self.asset.delete()

    def test_price(self):
        self.assertIsNone(self.asset.price)
        self.asset.price = MoneyAmount('USD', 400)
        self.assertEqual(self.asset.price, MoneyAmount('USD', 400))

    def test_absolute_url(self):
        self.assertEqual(
            self.asset.get_absolute_url(),
            '/assets/user/{0}/asset/{1}'.format(self.user.id, self.asset.id.hex)
        )

    def test_qr_code(self):
        print('QR CODE: {0}'.format(self.asset.qr_code))
        self.assertEqual(
            self.asset.qr_code,
            settings.HOST_URI + self.asset.get_absolute_url()
        )

