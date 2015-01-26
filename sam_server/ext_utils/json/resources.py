from datetime import datetime
from enum import Enum
import uuid
import tempfile
import base64


from dateutil.parser import parse as parse_date

_NONE_TYPE = type(None)


class Resource(object):
    def __init__(self, required=True):
        self.required = required

    def check_mandatory(self, value):
        if self.required and value is None:
            raise ValueError('No value for mandatory resource')

    def to_json(self, value):
        raise NotImplementedError()

    def to_python(self, resource):
        """
        Convert the resource value to a python value
        """
        raise NotImplementedError()

    @property
    def discovery(self):
        """
        A DiscoveryResource object representing the resource
        """
        raise NotImplementedError()


class _SimpleResource(Resource):

    def to_json(self, value):
        self.check_mandatory(value)
        if value is None:
            return value
        if not isinstance(value, self._TYPE):
            raise ValueError('Not an instance of {0}'.format(self._TYPE))
        return value

    def to_python(self, resource):
        self.check_mandatory(resource)
        if resource is None:
            return
        if not isinstance(resource, self._TYPE):
            raise TypeError('Not an instance of {0}'.format(self._TYPE))
        return resource


class ObjectResource(_SimpleResource):
    """
    An object resource can hold any type of value. No coersion is done
    on get or set
    """
    _TYPE = object
    KIND = 'dynamic'

    def to_json(self, value):
        """
        Check that the value is of a simple python type which can be
        implicitly converted to a json value
        """
        self.check_mandatory(value)
        if value is None:
            return value
        if not isinstance(value, (str, float, int, )):
            raise TypeError('Only None and bool, float, int and str values '
                            'can be encoded to json by an object resource')
        return value


class BoolResource(_SimpleResource):
    _TYPE = bool


class IntegerResource(_SimpleResource):
    _TYPE = int


class FloatResource(_SimpleResource):
    _TYPE = float


class StringResource(_SimpleResource):
    _TYPE = str


class DateTimeResource(Resource):

    def to_python(self, resource):
        self.check_mandatory(resource)
        if resource is None:
            return resource
        return parse_date(resource)

    def to_json(self, value):
        self.check_mandatory(value)
        if value is None:
            return value
        if not isinstance(value, datetime):
            raise TypeError('Not a date or datetime object: {0}'.format(value))
        return value.isoformat()


class EnumResource(Resource):

    def __init__(self, enum_type=None, **kwargs):
        if (enum_type is None
                or not isinstance(enum_type, type)
                or Enum not in enum_type.__mro__):
            raise ValueError('EnumResource requires an enum_type')
        self.enum_type = enum_type
        super().__init__(**kwargs)

    def to_python(self, resource):
        self.check_mandatory(resource)
        if resource is None:
            return None
        return self.enum_type(resource)

    def to_json(self, value):
        self.check_mandatory(value)
        if value is None:
            return None
        if not isinstance(value, self.enum_type):
            raise ValueError('Not a value of {0}'.format(self.enum_type))
        return value.value


class UUIDResource(Resource):
    def to_python(self, resource):
        self.check_mandatory(resource)
        if resource is None:
            return resource
        return uuid.UUID(hex=str(resource))

    def to_json(self, resource):
        self.check_mandatory(resource)
        if resource is None:
            return None
        if not isinstance(resource, uuid.UUID):
            raise TypeError('Not a UUID: {0}'.format(resource))
        return resource.hex


class ListResource(Resource):

    def __init__(self, item_resource=None, **kwargs):
        if item_resource is None:
            item_resource = ObjectResource()
        self.item_resource = item_resource
        super().__init__(**kwargs)

    def to_python(self, resource):
        self.check_mandatory(resource)
        resource = list(resource or [])
        return list(map(self.item_resource.to_python, resource))

    def to_json(self, value):
        self.check_mandatory(value)
        if value is None:
            return []
        value = list(value)
        return list(map(self.item_resource.to_json, value))


class DictResource(Resource):
    """
    Represents an arbitrary key value pair.
    The value is a specific resource type (which defaults to ObjectResource)
    """

    def __init__(self, value_resource=None, **kwargs):
        self.value_resource = value_resource or ObjectResource()
        super().__init__(**kwargs)

    def to_python(self, resource):
        """
        Transform the resource, using the provided value resource.
        A copy of the resource is returned, rather than mutating
        the resource
        """
        self.check_mandatory(resource)
        if resource is None:
            return resource
        resource = dict(resource)
        return {
            k: self.value_resource.to_python(v)
            for k, v in resource.items()
        }

    def to_json(self, value):
        self.check_mandatory(value)
        if value is None:
            return dict()
        value = dict(value)
        return {
            k: self.value_resource.to_json(v)
            for k, v in value.items()
        }


class File(object):
    ## TODO, temporary file object for handling file inputs.
    ## Remove in preference of something more useful

    def __init__(self, mime_type, name, body):
        self.mime_type = mime_type
        self.name = name
        ## Base64 encoded body
        self.body = body

    @property
    def body_bytes(self):
        return base64.b64decode(self.body)

    def __str__(self):
        return 'resources.File<{0.name}>'.format(self)


class FileResource(Resource):
    """
    A FileResource represents a list of File type objects.
    Each File has a mime_type, name and base64 encoded body
    """

    def _file_to_python(self, resource_item):
        if resource_item is None:
            raise ValueError('None in file list')
        try:
            mime_type = resource_item['type']
        except KeyError:
            raise ValueError("No 'type' in file resource")
        try:
            name = resource_item['name']
        except KeyError:
            raise ValueError("No 'name' in file resource")
        try:
            body = resource_item['body']
        except KeyError:
            raise ValueError("No 'body' in file resource")
        return File(mime_type, name, body)

    def _file_to_json(self, resource_item):
        if not isinstance(resource_item, File):
            raise ValueError("Expected a 'file'")
        return {
            'type': resource_item.mime_type,
            'name': resource_item.name,
            'body': resource_item.body
        }

    def to_python(self, resource):
        self.check_mandatory(resource)
        if resource is None:
            return resource
        if not hasattr(resource, '__iter__'):
            raise ValueError('Expected an iterable value for file resource')
        resource = list(resource)
        return list(map(self._file_to_python, resource))

    def to_json(self, resource):
        self.check_mandatory(resource)
        if resource is None:
            return []
        resource = list(resource)
        return list(map(self._file_to_json, resource))


class _ModelResourceMeta(type):
    def __new__(cls, name, bases, attrs):
        new_cls = super().__new__(cls, name, bases, attrs)

        if name == 'ModelResource' and bases == (Resource, ):
            new_cls._resource_fields = {}
            return new_cls

        if not 'KIND' in attrs:
            raise TypeError(
                'Model resource must have a class level KIND attribute')

        resource_fields = {}
        resource_bases = tuple(b for b in bases if ModelResource in b.__mro__)

        for k, v in attrs.items():
            if k == 'kind':
                raise ValueError(
                    '\'kind\' is a reserved name on model resources'
                )
            if not isinstance(v, Resource):
                continue
            resource_fields[k] = v
        for base in resource_bases:
            resource_fields.update(base._resource_fields)
        new_cls._resource_fields = resource_fields

        return new_cls


class ModelResource(Resource, metaclass=_ModelResourceMeta):

    def _check_resource_kind(self, resource):
        try:
            kind = resource.pop('kind')
            if kind != self.KIND:
                raise ValueError('Invalid kind for resource ({0})'.format(kind))
        except KeyError:
            raise ValueError('No \'kind\' key resource')

    def to_python(self, resource):
        """
        Returns a dict which contains the field resources transformed
        by each field's corresponding to_python method.

        The resource is considered invalid if:
        - It contains a key which is not present on the classes declared
        resource fields
        """
        self.check_mandatory(resource)
        if resource is None:
            return resource
        resource = dict(resource)
        self._check_resource_kind(resource)
        model_resource = dict()

        for key, value in resource.items():
            try:
                field_resource = self._resource_fields[key]
            except KeyError:
                raise ValueError('Key invalid for resource: {0}'.format(key))
            model_resource[key] = field_resource.to_python(value)
        return model_resource

    def _resolve_field_value(self, field_name, model):
        custom_getter_name = 'get_{0}'.format(field_name)
        if hasattr(self, custom_getter_name):
            return getattr(self, custom_getter_name)(model)
        if hasattr(model, '__getitem__'):
            return model[field_name]
        return getattr(model, field_name)

    def to_json(self, model):
        """
        Converts the given json object into json using the resources
        defined at the class level.

        The value corresponding to a field is resolved by trying, in order:
        - The class declaration is searched for a 'get_(field_name)' method.
          The method will be called with the model instance as the sole argument
        - If the model delcares a '__getitem__' method, an item lookup will be
          made with the field name as argument
        - Otherwise, an attribute lookup will be performed on the model.
        """
        self.check_mandatory(model)
        if model is None:
            return None

        resource = dict()
        for field, field_resource in self._resource_fields.items():
            raw_value = self._resolve_field_value(field, model)
            field_value = field_resource.to_json(raw_value)
            if field_value is not None:
                resource[field] = field_value
        resource['kind'] = self.KIND
        return resource

