from dateutil.parser import parse as date_parser


class Resource(object):
    def __init__(self, attr=None):
        self.attr = attr

    def _get_model_field(self, model):
        model_attr_value = getattr(model, self.attr)
        return self.to_json_value(model_attr_value)

    def to_json_value(self, value):
        return value

    def from_json_value(self, value):
        return value


class Integer(Resource):
    pass


class String(Resource):
    pass


class DateTime(Resource):
    def to_json_value(self, value):
        if value is None:
            return None
        return value.isoformat()

    def from_json_value(self, value):
        if value is None:
            return None
        return date_parser(value)


class Enum(Resource):
    def __init__(self, attr=None, enum_type=None):
        super().__init__(attr)
        self.enum_type = enum_type

    def to_json_value(self, value):
        return value.value

    def from_json_value(self, value):
        return self.enum_type(value)


class ModelResourceMeta(type):
    def __init__(cls, name, bases, ns):
        if name == 'Model':
            return
        err_msg = None
        if 'NAME' not in ns:
            err_msg = ('Resource {0} does not declare a class level NAME '
                       'attribute').format(self.__class__.__name__)
        if 'MODEL_TYPE' not in ns:
            err_msg = ('Resource {0} does not declare a class level '
                       'MODEL_TYPE attribute').format(self.__class__.__name__)
        if err_msg:
            raise TypeError(err_msg)
        cls._fields = {k: v for k, v in ns.items() if isinstance(v, Resource)}


class Model(Resource, metaclass=ModelResourceMeta):

    def to_json_value(self, value):
        json = {'resource': self.NAME}
        for field, resource in self._fields.items():
            json[field] = resource._get_model_field(value)
        return json

    def from_json_value(self, value):
        """
        From json value is only implemented on Model resources if
        the implementating resource defines it
        """
        raise NotImplementedError('from_json_value')


class ValidationError(Exception):
    pass
