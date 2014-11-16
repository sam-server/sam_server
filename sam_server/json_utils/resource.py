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
        if 'NAME' not in ns:
            raise TypeError('Resource {0} does not declare a class level NAME attribute')
        if 'MODEL_TYPE' not in ns:
            raise TypeError('Resource {0} does not declare a class level MODEL_TYPE attribute')
        cls._fields = {k: v for k, v in ns.items() if isinstance(v, Resource)}


class Model(Resource, metaclass=ModelResourceMeta):

    def to_json_value(self, value):
        json = {'resource': self.NAME}
        for field, resource in self._fields.items():
            json[field] = resource._get_model_field(value)
        return json

    def from_json_value(self, value):
        model_manager = self.MODEL_TYPE.objects
        if not hasattr(model_manager, 'from_resource'):
            raise TypeError(('{0} resource cannot be deserialized as model manager '
                             'does not declare a \'from_resource\' method'
                             ).format(self.NAME))
        data = {}
        for field, resource in self._fields.items():
            data[field] = resource.from_json_value(value[field])
        return model_manager.from_resource(data)

