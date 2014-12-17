from functools import total_ordering
from numbers import Rational
from fractions import Fraction
from decimal import Decimal
import os
from xml.etree import ElementTree

from dateutil.parser import parser as date_parser

from django.conf import settings
from parsers import parser, lexer
from parsers.exceptions import ParseError

UTIL_FILES = os.path.join(settings.BASE_DIR, 'common', 'utility_files')

ISO_4217_PATH = os.path.join(UTIL_FILES, 'iso_4217.xml')
CURRENCY_SYMBOLS_PATH = os.path.join(UTIL_FILES, 'currency_symbols.xml')

## TODO: GET RID OF INTEGER VALUE, just use decimal everywhere

@total_ordering
class MoneyAmount(object):
    def __init__(self, currency_code, value=None):
        """
        Creates a new money amount using the given value.
        If the amount is a Rational or Decimal value it will be converted
        to an integer using bankers rounding

        If value is None, then the value is parsed as a formatted string

        """
        if value is None:
            money = self.parse(currency_code)
            self.code = money.code
            self.currency = money.currency
            self.value = money.value
            return
        self.code = currency_code
        self.currency = Currency.from_code(currency_code)

        if isinstance(value, str):
            decimal_value = Decimal(value)
            int_value = self.currency.to_integer_value(
                *map(int, str(decimal_value).split('.'))
            )
        elif isinstance(value, int):
            int_value = value
        else:
            raise TypeError('Unsupported value type {0}'.format(type(value)))

        self.value = int_value

    @classmethod
    def parse(cls, money_amount):
        parser = MoneyAmountParser()
        return parser.run(money_amount)

    @property
    def decimal_string_value(self):
        """
        Return the value as a decimal string
        """
        major_units, minor_units = self.currency.from_integer_value(self.value)
        string = str(major_units)
        if minor_units is not None:
            string += '.'
            str_value = str(minor_units)
            num_leading_zeroes = self.currency.num_digits_in_minor_units - len(str_value)
            leading_zeroes = '0' * num_leading_zeroes
            string += (leading_zeroes + str_value)
        return string

    def convert_to(self, curr_code):
        if self.code == curr_code:
            return self
        raise NotImplementedError('Currency conversions')

    def __eq__(self, other):
        if self is other:
            return True
        if other is None:
            return False
        return self.code == other.code and self.value == other.value

    def __lt__(self, other):
        """
        Returns `True` if self < other. If the amounts are in different
        currencies, convert them both to `self.curr_code` before comparison

        Note that currency conversion is a *very* expensive operation
        """
        other = other.convert_to(self.code)
        return self.value < other.value

    def __add__(self, other):
        """
        Add the two amounts. If the amounts are in different currencies,
        convert them both to `self.curr_code` before addition
        """
        if not isinstance(other, MoneyAmount):
            raise TypeError('Expected a MoneyAmount: {0}'.format(other))
        other = other.convert_to(self.code)
        return MoneyAmount(self.code, self.value + other.value)

    def __pos__(self):
        return MoneyAmount(self.code, +self.value)

    def __neg__(self):
        return MoneyAmount(self.code, -self.value)

    def __sub__(self, other):
        return self.__add__(other.__neg__())

    def __mul__(self, frac):
        """
        Multiply the amount by the given fraction, using bankers rounding
        to round to the nearest value
        """
        if isinstance(frac, Decimal):
            frac = Fraction.from_decimal(frac)
        elif not isinstance(frac, Rational):
            raise TypeError('Expected a Decimal or a numbers.Rational value')
        return MoneyAmount(self.code, frac * self.value)

    def __repr__(self):
        return str(self)

    def __str__(self):
        string = '{0} {1}'.format(self.code, self.decimal_string_value)
        return string


class Currency(object):
    """
    A dict mapping currency codes to currency, loaded from the
    ISO 4217 standards document
    """
    _currencies = None

    """
    The date that the currency list was published
    """
    _date_published = None

    """
    A map of currency codes to symbols
    """
    _symbols = None

    @classmethod
    def _load_currencies_from_iso(cls):
        tree = ElementTree.parse(ISO_4217_PATH)
        root = tree.getroot()
        cls._date_published = date_parser(root.attrib['Pblshd'])
        currencies = dict()
        for element in root.findall('./CcyTbl/CcyNtry'):
            currency_code_elem = element.find('Ccy')
            if currency_code_elem is None:
                # The entry does not represent a currency
                continue
            currency_code = currency_code_elem.text
            try:
                currency = currencies[currency_code]
                # The currency already exists, just add the country to it
                country_name_elem = element.find('CtryNm')
                currency.countries.add(country_name_elem.text)

            except KeyError:
                currencies[currency_code] = Currency._from_element(currency_code, element)
        cls._currencies = currencies

    @classmethod
    def _load_symbols(cls):
        def to_symbol(hex_codepoints):
            if hex_codepoints == '':
                return ''
            return ''.join(chr(int(d, base=16)) for d in hex_codepoints.split(','))
        tree = ElementTree.parse(CURRENCY_SYMBOLS_PATH)
        root = tree.getroot()
        symbols = dict()
        for element in root.findall('entry'):
            code = element.attrib['code']
            symbol = to_symbol(element.attrib['unicode-hex'])
            symbols[code] = symbol
        cls._symbols = symbols

    def __init__(self, code, name, countries, number,
                 num_digits_in_minor_units=None):
        self.code = code
        self.name = name
        self.countries = countries
        self.number = number
        self.num_digits_in_minor_units = num_digits_in_minor_units

    @classmethod
    def _from_element(cls, currency_code, element):
        country_name_elem = element.find('CtryNm')
        if country_name_elem is None:
            return None
        num_digits = element.find('CcyMnrUnts').text
        if num_digits == 'N.A.':
            num_digits = None
        else:
            num_digits = int(num_digits)
        return cls(
            code=currency_code,
            name=element.find('CcyNm').text,
            number=int(element.find('CcyNbr').text),
            countries=set([country_name_elem.text, ]),
            num_digits_in_minor_units=num_digits
        )

    @classmethod
    def from_code(cls, code):
        """
        Load the currency from the ISO document stored at
        settings.ISO_4217_PATH
        """
        if cls._currencies is None:
            cls._load_currencies_from_iso()
        try:
            currency = cls._currencies[code]
        except KeyError:
            raise CurrencyException(
                'Unrecognised ISO currency code: {0}'.format(code))
        return currency

    @classmethod
    def from_country(cls, country):
        if cls._currencies is None:
            cls._load_currencies_from_iso()
        for currency in cls._currencies.values():
            if country in currency.countries:
                return currency
        raise CurrencyException(
            'No ISO currency for country {0}'.format(country))

    @classmethod
    def _get_symbol(cls, code):
        if cls._symbols is None:
            cls._load_symbols()
        return cls._symbols[code]

    @property
    def minor_units(self):
        return pow(10, self.num_digits_in_minor_units)

    @property
    def symbol(self):
        """
        The string representation of the currency's symbol
        """
        return self._get_symbol(self.code)

    def to_integer_value(self, major_units=0, minor_units=0):
        """
        Returns the integer value of the currency (the value of the currency)
        in amounts of the minor unit
        """
        if major_units < 0:
            raise CurrencyException('Major units cannot be negative')
        if minor_units < 0:
            raise CurrencyException('minor units cannot be negative')
        if minor_units >= self.minor_units:
            raise CurrencyException(
                'Minor units of {0} limited to {1}'
                .format(self.code, self.minor_units))
        value = major_units * self.minor_units
        value += minor_units
        return value

    def from_integer_value(self, currency_value):
        """
        Returns a tuple (major_units, minor_units) representing the decimal
        value of the currency
        If the currency has no minor units, None is returned as the minor
        unit value
        """
        if self.minor_units == 0:
            return (currency_value, None)
        return (currency_value // self.minor_units,
                currency_value % self.minor_units)


class MoneyAmountParser(parser.Parser):
    LEXER_TOKENS = [
        ('PERIOD', lexer.LiteralToken('.')),
        ('SIGN', lexer.LiteralToken('+', '-')),
        ('INT', lexer.RegexToken(r'[0-9]+')),
        ('CURR_CODE', lexer.RegexToken(r'[a-zA-Z]{3}')),
    ]

    def __init__(self):
        lex = lexer.Lexer(self.LEXER_TOKENS)
        super(MoneyAmountParser, self).__init__(lex)

    def begin(self):
        code = self.parse_currency_code()
        try:
            currency = Currency.from_code(code)
        except CurrencyException as e:
            raise ParseError(self.position, str(e))
        value = self.parse_currency_value(currency)
        return MoneyAmount(code, value)

    def parse_currency_code(self):
        token = self.move_next()
        if not token or token.name != 'CURR_CODE':
            raise ParseError(self.position, 'No currency code')
        currency_code = token.string
        return currency_code

    def parse_currency_value(self, currency):
        token = self.move_next(lookahead=True)
        is_negative_value = False
        if not token:
            raise ParseError(self.position, 'Expected decimal value')
        elif token.name == 'SIGN':
            is_negative_value = (token.string == '-')
            token = self.move_next()
        major_units = self.parse_major_units()
        minor_units = self.parse_minor_units(currency)
        value = currency.to_integer_value(major_units, minor_units)
        if is_negative_value:
            value = -value
        return value

    def parse_major_units(self):
        token = self.move_next()
        if not token or token.name != 'INT':
            raise ParseError(self.position, 'Expected major units')
        return int(token.string)

    def parse_minor_units(self, currency):
        token = self.move_next()
        if (currency.minor_units is None or currency.minor_units == 0):
            if token is not None:
                raise ParseError(self.position,
                                 'Currency {0} has no minor units'
                                 .format(currency.currency_name))
            return 0
        if token is None:
            raise ParseError(self.position,
                             'Currency {0} has minor units'
                             .format(currency.name))
        token = self.move_next()
        if token is None or token.name != 'INT':
            raise ParseError(self.position,
                             'Currency {0} has minor units'
                             .format(currency.name))
        return int(token.string)


class CurrencyException(Exception):
    pass






