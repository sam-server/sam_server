from datetime import datetime
from enum import Enum
import uuid

from django.db import models
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

    def to_json(self, model):
        """
        A model can be set from a django ORM model. If a 'get_(field_name)'
        method is defined on the resource definition, it will be passed the model
        as argument to get the associated value.

        Otherwise, the model can
        """
        self.check_mandatory(model)
        if model is None:
            return None

        resource = dict()
        for field, field_resource in self._resource_fields.items():
            custom_getter_name = 'get_{0}'.format(field)
            if hasattr(self, custom_getter_name):
                raw_value = getattr(self, custom_getter_name)(model)
            else:
                raw_value = getattr(model, field)
            field_value = field_resource.to_json(raw_value)
            if field_value is not None:
                resource[field] = field_value
        resource['kind'] = self.KIND
        return resource

