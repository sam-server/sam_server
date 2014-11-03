"""
Implements a UUID field for postgres.

Code is taken from dev version of django
https://github.com/django/django/blob/master/django/db/models/fields/__init__.py
and should be removed when django is upgraded
"""

import uuid

import psycopg2.extras

from django.core import exceptions
from django.utils.translation import ugettext_lazy as _
from django.db.models import Field

# psycopg2 requires the registration of the uuid type
psycopg2.extras.register_uuid()


class UUIDField(Field):
    default_error_messages = {
        'invalid': _("'%(value)s is not a valid UUID."),
    }

    description = "A field which corresponds to the postgres UUID type"
    empty_strings_allowed = False

    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 32
        super(UUIDField, self).__init__(*args, **kwargs)

    def get_internal_type(self):
        return "UUIDField"

    def get_prep_value(self, value):
        if isinstance(value, uuid.UUID):
            return value.hex
        if isinstance(value, str):
            return value.replace('-', '')
        return value

    def to_python(self, value):
        if value and not isinstance(value, uuid.UUID):
            try:
                return uuid.UUID(value)
            except ValueError:
                raise exceptions.ValidationError(
                    self.error_messages['invalid'],
                    code='invalid',
                    params={'value': value})
        return value

    def db_type(self, connection):
        if 'postgres' not in connection.vendor:
            raise NotImplementedError(
                'UUID only implemented for postgres database')
        return 'UUID'


