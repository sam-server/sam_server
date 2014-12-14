
from ext_utils.json.resources import Resource
from .currency import MoneyAmount


class MoneyAmountResource(Resource):
    def to_json(self, value):
        self.check_mandatory(value)
        if value is None:
            return None
        if not isinstance(value, MoneyAmount):
            raise TypeError('Not a MoneyAmount: {0}'.format(value))
        return {
            'code': value.code,
            'symbol': value.currency.symbol,
            'num_decimal_digits': value.currency.num_digits_in_minor_units,
            'value': value.decimal_string_value
        }

    def to_python(self, resource):
        self.check_mandatory(resource)
        if resource is None:
            return None
        if isinstance(resource, str):
            return MoneyAmount.parse(resource)
        elif isinstance(resource, dict):
            try:
                code = resource['code']
                value_decimal_string = resource['value']
            except KeyError:
                raise ValueError('Invalid money amount: {0}'.format(resource))
            return MoneyAmount(code, value_decimal_string)


