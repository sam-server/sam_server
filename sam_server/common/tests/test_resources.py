from django.test import TestCase

from ..currency import MoneyAmount
from ..resources import MoneyAmountResource

class ResourcesTest(TestCase):
    def test_money_amount_resource(self):
        r = MoneyAmountResource()

        m = MoneyAmount('USD', 400)
        resource = 'USD 4.00'
        self.assertEqual(r.to_json(m), resource)
        self.assertEqual(r.to_python(resource), m)
