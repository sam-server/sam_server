
from ext_utils.json.resources import Resource
from .currency import MoneyAmount


class MoneyAmountResource(Resource):
    def to_json(self, value):
        self.check_mandatory(value)
        if value is None:
            return None
        if not isinstance(value, MoneyAmount):
            raise TypeError('Not a MoneyAmount: {0}'.format(value))
        return str(value)

    def to_python(self, resource):
        self.check_mandatory(resource)
        if resource is None:
            return None
        return MoneyAmount.parse(resource)
