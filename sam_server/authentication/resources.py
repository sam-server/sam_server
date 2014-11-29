from json_utils.resources import *

from . import models

class UserResource(ModelResource):

    KIND = 'authentication#user'

    id = IntegerResource()
    type = EnumResource(enum_type=models.User.Type)
    date_joined = DateTimeResource()
    last_login = DateTimeResource(required=False)

    ## At least one of the following must be non-null
    goog_id = StringResource(required=False)
    username = StringResource(required=False)
    facebook_id = StringResource(required=False)

    def get_type(self, model):
        return model.auth_type

    def get_goog_id(self, model):
        if model.auth_type == models.User.Type.GOOGLEPLUS:
            return model.auth_identifier
        return None

    def get_username(self, model):
        if model.auth_type == models.User.Type.BASIC:
            return model.auth_identifier
        return None

    def get_facebook_id(self, model):
        if model.auth_type == models.User.Type.FACEBOOK:
            return model.auth_identifier
        return None






