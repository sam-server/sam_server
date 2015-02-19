"""
Backends for the authentcation middleware to authenticate
users
"""
import base64
import binascii
import httplib2
import json
import logging

from django.core.exceptions import PermissionDenied
from django.contrib.auth import get_user_model

from .settings import GOOGLE_AUTHENTICATION

logger = logging.getLogger(__name__)


class BackendBase(object):
    def get_user(self, user_id):
        UserModel = get_user_model()
        try:
            return UserModel.objects.get(pk=user_id)
        except UserModel.DoesNotExist:
            return None


class BasicUserBackend(BackendBase):
    NAME = 'Basic user'

    def authenticate(self, **kwargs):
        logger.info('Attempting basic user authorisation')
        if 'auth_header' in kwargs:
            return self._authenticate_header(kwargs['auth_header'])
        elif 'username' in kwargs:
            return self._authenticate_userpass(username=kwargs['username'],
                                               password=kwargs.get('password'),
                                               force=kwargs.get('force'))
        else:
            return None

    def _authenticate_header(self, auth_header=None):
        """
        Authenticates a user given the http 'Authorization' header
        which was present in a request
        """
        if auth_header is None or not auth_header.startswith('Basic '):
            return None
        raw_token = auth_header[len('Basic '):]
        try:
            token = str(base64.b64decode(raw_token), encoding='utf-8')
            username, password = token.split(':')
        except (ValueError, binascii.Error):
            raise PermissionDenied('Invalid authorization header')
        return self._authenticate_userpass(username=username, password=password)

    def _authenticate_userpass(self, username, password=None, force=False):
        if not force and password is None:
            return None
        UserModel = get_user_model()
        try:
            user = UserModel.objects.get_by_natural_key(
                UserModel.Type.BASIC, username)
            if force or user.check_password(password):
                return user
        except UserModel.DoesNotExist:
            return None


class GoogleUserBackend(BackendBase):
    """
    Authentication backend for users which are authenticated using google
    oauth2 identification.

    Users are authenticated by providing a valid 'Authorization' header,
    populated with a 'Bearer' token containing an access_token to be
    passed to the google tokeninfo endpoint
    """

    TOKENINFO_ENDPOINT = 'https://www.googleapis.com/oauth2/v1/tokeninfo'

    def authenticate(self, **kwargs):
        logger.info('attempting to authorise google user')
        if 'auth_header' in kwargs:
            return self._authenticate_header(kwargs['auth_header'])
        elif 'id_token' in kwargs:
            return self._authenticate_id_token(kwargs['id_token'])
        else:
            return None

    def _authenticate_header(self, auth_header):
        if auth_header is None or not auth_header.startswith('Bearer '):
            return None
        logger.info('Authorization header: {0}'.format(auth_header))
        bearer_token = auth_header[len('Bearer '):]
        h = httplib2.Http()
        headers, response = h.request(
            self.TOKENINFO_ENDPOINT + '?access_token={0}'.format(bearer_token)
        )
        id_token = json.loads(str(response, encoding='utf-8'))
        if 'error' in id_token:
            logger.warn('tokeninfo endpoint responded with an error')
            return None
        return self._authenticate_id_token(id_token)

    def _authenticate_id_token(self, id_token):
        UserModel = get_user_model()
        ## If the id token is fetched from the credentials, the audience is
        ## stored as 'aud'. If fetched from tokeninfo, it is present as
        ## 'audience'
        audience = id_token.get('aud') or id_token.get('audience')

        ## If the subscriber is fetched from the stored credentials, the
        ## subscriber is stored as 'sub', if fetched from tokeninfo endpoint
        ## it is 'user_id'
        subscriber = id_token.get('sub') or id_token.get('user_id')
        if audience != GOOGLE_AUTHENTICATION['CLIENT_ID']:
            return None
        try:
            user = UserModel.objects.get_by_natural_key(
                UserModel.Type.GOOGLEPLUS, subscriber)
            return user
        except UserModel.DoesNotExist:
            return None
