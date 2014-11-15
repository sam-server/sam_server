"""
Backends for the authentcation middleware to authenticate
users
"""

from django.contrib.auth import get_user_model
from oauth2client.client import verify_id_token
from oauth2client.crypt import AppIdentityError


class BackendBase(object):
    def get_user(self, user_id):
        UserModel = get_user_model()
        try:
            return UserModel.objects.get(pk=user_id)
        except UserModel.DoesNotExist:
            return None


class BasicUserBackend(BackendBase):
    def authenticate(self, username=None, password=None, **kwargs):
        UserModel = get_user_model()
        try:
            user = UserModel.objects.get_by_natural_key(
                UserModel.BASIC_USER, username)
            if user.check_password(password):
                return user
        except UserModel.DoesNotExist:
            return None


class OAuthUserBackend(BackendBase):
    def authenticate(self, bearer_token=None, **kwargs):
        UserModel = get_user_model()
        if bearer_token is None or not bearer_token.startswith('Bearer '):
            return None
        bearer_token = bearer_token[len('Bearer '):]
        try:
            id_token = verify_id_token(bearer_token)
        except AppIdentityError:
            return None
        try:
            user = UserModel.objects.get_by_natural_key(
                UserModel.GOOGLEPLUS_USER, id_token['sub'])
            return user
        except UserModel.DoesNotExist:
            pass
