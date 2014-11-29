from datetime import datetime
import uuid

from django.db import models
from django.test import TestCase

from .. import resources


class MyModelResource(resources.ModelResource):
    KIND = 'test#my_model'

    id = resources.UUIDResource(required=True)
    required_field = resources.IntegerResource(required=True)
    custom_getter_field = resources.StringResource(required=True)

    def get_model_custom_getter_field(self, model):
        return '**custom_getter**'


class SubclassModelResource(MyModelResource):
    KIND = 'test#my_submodel'
    subclass_field = resources.IntegerResource(required=True)


class ResourcesTest(TestCase):
    def test_simple_resource(self):
        """
        Use the integer resource to test simple resources.
        Other simple resources should behave similarly
        """
        r = resources.IntegerResource()
        self.assertEqual(r.to_json(4), 4)

        self.assertEqual(r.to_python(4), 4)
        r2 = resources.IntegerResource(required=True)
        with self.assertRaises(ValueError):
            r2.to_json(None)

    def test_datetime_resource(self):
        r = resources.DateTimeResource()
        dt = datetime.fromtimestamp(0)
        self.assertEquals(r.to_json(dt), '1970-01-01T00:00:00')
        self.assertEquals(r.to_python('1970-1-1T00:00:00'), dt)

    def test_uuid_resource(self):
        r = resources.UUIDResource()
        u = uuid.UUID(int=0)
        self.assertEqual(r.to_json(u), '0' * 32)
        self.assertEqual(r.to_python('0' * 32), u)

    def test_list_resource(self):
        r_object = resources.ListResource()
        resource = ['hello', 4]
        self.assertEqual(r_object.to_python(resource), resource)
        self.assertEqual(r_object.to_json(resource), resource)

        r_uuid = resources.ListResource(resources.UUIDResource())
        value = [uuid.UUID(int=0), uuid.UUID(int=1), None]
        resource = ['0' * 32, ('0' * 31) + '1', None]
        self.assertEqual(r_uuid.to_json(value), resource)
        self.assertEqual(r_uuid.to_python(resource), value)

    def test_dict_resource(self):
        r_object = resources.DictResource()
        value = {
            'arg1': 'value1',
            'arg2': 2
        }
        self.assertEqual(r_object.to_python(value), value)
        self.assertEqual(r_object.to_json(value), value)

        r_uuid = resources.DictResource(resources.UUIDResource())
        value = {
            'arg1': uuid.UUID(int=0),
            'arg2': uuid.UUID(int=1)
        }
        resource = {
            'arg1': '0' * 32,
            'arg2': ('0' * 31) + '1'
        }
        self.assertEqual(r_uuid.to_python(resource), value)
        self.assertEqual(r_uuid.to_json(value), resource)

    def test_model_resource_meta(self):
        id_field = MyModelResource._resource_fields['id']
        self.assertIsInstance(id_field, resources.UUIDResource)

        required_field = MyModelResource._resource_fields['required_field']
        self.assertIsInstance(required_field, resources.IntegerResource)
        self.assertTrue(required_field.required)

        custom_getter_field = MyModelResource._resource_fields['custom_getter_field']
        self.assertIsInstance(custom_getter_field, resources.StringResource)

    def test_model_subclassing(self):
        id_field = SubclassModelResource._resource_fields['id']
        self.assertIsInstance(id_field, resources.UUIDResource)

        subclass_field = SubclassModelResource._resource_fields['subclass_field']
        self.assertIsInstance(subclass_field, resources.IntegerResource)

        with self.assertRaises(KeyError):
            subclass_field = MyModelResource._resource_fields['subclass_field']

    def test_model_resource(self):
        r = MyModelResource()

        class TestModel(models.Model):
            def __init__(self):
                self.id = uuid.uuid4()
                self.required_field = 4
                self.custom_getter_field = '**invalid_value**'

        model = TestModel()
        resource = {
            'kind': 'test#my_model',
            'id': model.id.hex,
            'required_field': 4,
            'custom_getter_field': '**custom_getter**'
        }
        self.assertEqual(r.to_json(model), resource)

        self.assertEqual(r.to_python(resource),
            {
                'id': model.id,
                'required_field': 4,
                'custom_getter_field': '**custom_getter**'
            })











