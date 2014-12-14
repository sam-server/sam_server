from ext_utils.json.resources import *

from . import models

class UserResource(ModelResource):

    KIND = 'authentication#user'

    id = IntegerResource()
    type = EnumResource(enum_type=models.User.Type)
    date_joined = DateTimeResource(required=False)
    last_login = DateTimeResource(required=False)

    ## At least one of the following must be non-null
    goog_id = StringResource(required=False)
    username = StringResource(required=False)
    facebook_id = StringResource(required=False)

    password = StringResource(required=False)
    remembered = BoolResource(required=False)

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

    def get_remembered(self, model):
        ## TODO: Store whether we remember the user on the model
        return True






