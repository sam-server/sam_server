from json_utils import resource

from .models import User


class UserResource(resource.Model):

    NAME = 'authentication#user'
    MODEL_TYPE = User

    id = resource.Integer(attr='id')
    type = resource.Enum(attr='auth_type', enum_type=User.Type)
    date_joined = resource.DateTime(attr='date_joined')
    last_login = resource.DateTime(attr='last_login')


