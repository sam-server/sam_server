import re

from ext_utils.json.resources import Resource
from .currency import MoneyAmount


class MoneyAmountResource(Resource):
    CURRENCY_PATTERN = re.compile(
        r'([-+]?\d+\.\d+) ([A-Z]{3})'
    )

    def to_json(self, value):
        self.check_mandatory(value)
        if value is None:
            return None
        if not isinstance(value, MoneyAmount):
            raise TypeError('Not a MoneyAmount: {0}'.format(value))
        return '{0} {1}'.format(value.decimal_string_value, value.code)

    def to_python(self, resource):
        self.check_mandatory(resource)
        if resource is None:
            return None
        if isinstance(resource, str):
            match = MoneyAmountResource.CURRENCY_PATTERN.match(resource)
            if match is None:
                raise ValueError('Invalid format for money value: {0}'.format(resource))
            value = '{0} {1}'.format(match.group(2), match.group(1))
            return MoneyAmount.parse(value)
        raise ValueError('Expected a string: {0}'.format(resource))


