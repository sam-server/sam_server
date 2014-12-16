from fractions import Fraction
from decimal import Decimal

from django.test import TestCase

from ..currency import MoneyAmount, Currency, MoneyAmountParser


class MoneyAmountTest(TestCase):

    def test_rounding(self):
        amt1 = MoneyAmount('USD', Decimal('2.5'))
        self.assertEqual(amt1.value, 2)
        amt2 = MoneyAmount('USD', Decimal('3.5'))
        self.assertEqual(amt2.value, 4)

    def test_addition(self):
        amt1 = MoneyAmount('USD', 400)
        amt2 = MoneyAmount('USD', 500)
        self.assertEqual(amt1 + amt2, MoneyAmount('USD', 900))

    def test_ordering(self):
        amt1 = MoneyAmount('USD', 400)
        amt2 = MoneyAmount('USD', 500)
        self.assertTrue(amt1 < amt2)

    def test_multiplication(self):
        amt1 = MoneyAmount('USD', 400)
        self.assertEqual(amt1 * 4, MoneyAmount('USD', 1600))

        self.assertEqual(amt1 * Fraction(4, 5), MoneyAmount('USD', 320))
        self.assertEqual(amt1 * Decimal(0.8), MoneyAmount('USD', 320))

    def test_to_string(self):
        amt1 = MoneyAmount('AUD', 412)
        self.assertEqual(str(amt1), 'AUD 4.12')

        amt2 = MoneyAmount('AUD', 4000)
        self.assertEqual(str(amt2), 'AUD 40.00')


class CurrencyTest(TestCase):
    def test_currency_from_code(self):
        currency = Currency.from_code('NZD')
        self.assertEqual(currency.name, 'New Zealand Dollar')
        countries = set([
            'COOK ISLANDS',
            'NEW ZEALAND',
            'NIUE',
            'PITCAIRN',
            'TOKELAU'
        ])
        self.assertEqual(currency.countries, countries)
        self.assertEqual(currency.minor_units, 100)

    def test_to_integer_value(self):
        currency = Currency.from_code('AUD')
        self.assertEqual(
            currency.to_integer_value(major_units=4, minor_units=12),
            412
        )

    def test_from_integer_value(self):
        currency = Currency.from_code('AUD')
        self.assertEqual(
            currency.from_integer_value(400),
            (4, 0)
        )

    def test_currency_symbol(self):
        currency = Currency.from_code('AUD')
        self.assertEqual(currency.symbol, '$')
        currency = Currency.from_code('EUR')
        self.assertEqual(currency.symbol, '€')


class ParsingTest(TestCase):
    def test_parse_monetary_value(self):
        parser = MoneyAmountParser()
        result = parser.run('AUD 4.12')
        self.assertEqual(result, MoneyAmount('AUD', 412))

        result = parser.run('USD 4.02')
        self.assertEqual(result, MoneyAmount('USD', 402))
