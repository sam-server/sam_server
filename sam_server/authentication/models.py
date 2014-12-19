import logging
import re
from enum import Enum
import base64

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import BaseUserManager
from django.contrib.auth.hashers import (
    check_password, make_password, is_password_usable)

from oauth2client.django_orm import CredentialsField, Storage

logger = logging.getLogger(__name__)

_VALID_GOOGLEID_PATTERN = re.compile(r'^\d+$')
_VALID_USERNAME_PATTERN = re.compile(r'^[\w+_-]+$')


class UserManager(BaseUserManager):

    def create_basic_user(self, username, email, password):
        user_id = _make_user_id(User.Type.BASIC, username)
        email = self.normalize_email(email)
        user = self.model(email=email, user_id=user_id)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_googleplus_user(self, credentials):
        id_token = credentials.id_token
        email = self.normalize_email(id_token['email'])
        user_id = _make_user_id(User.Type.GOOGLEPLUS, id_token['sub'])
        user = self.model(email=email, user_id=user_id,
                          email_verified=id_token['email_verified'])
        user.set_credential(credentials)
        user.save(using=self._db)
        return user

    def natural_key_exists(self, auth_type, identifier):
        user_id = _make_user_id(auth_type, identifier)
        return self.filter(user_id=user_id).exists()

    def get_by_natural_key(self, auth_type, identifier):
        user_id = _make_user_id(auth_type, identifier)
        return self.get(user_id=user_id)


def _check_valid_identifier_for_auth_type(auth_type, identifier):
    """
    Checks that the given identifier is valid for the authentication type

    @returns None on success

    @raises
    ValidationError: If the identifier is invalid
    """
    if identifier is None:
        raise ValidationError('Identifier cannot be None')
    identifier = str(identifier)

    if auth_type == User.Type.BASIC:
        if _VALID_USERNAME_PATTERN.match(identifier) is None:
            raise ValidationError(
                'Username must consist of a sequence of letters'
                'and digits or the characters -, +, _ ({0})'
                .format(identifier)
            )
    elif auth_type == User.Type.GOOGLEPLUS:
        if _VALID_GOOGLEID_PATTERN.match(identifier) is None:
            raise ValidationError(
                'Google ID must be a sequence of digits ({0})'
                .format(identifier)
            )
    elif auth_type == User.Type.FACEBOOK:
        raise NotImplementedError('Facebook user')
    else:
        raise ValidationError(
            'Invalid auth_type ({0})'.format(auth_type)
        )


def _make_user_id(auth_type, identifier):
    """
    Create a new user id given the auth_type and identifier

    @returns The user id

    @raises
    ValidationError if the identifier is invalid for the auth_type
    """
    _check_valid_identifier_for_auth_type(auth_type, identifier)
    return '{0}:{1}'.format(auth_type.value, identifier)


def _parse_user_id(user_id):
    """
    parses a user into auth_type and identifier components

    @returns
    A tuple 'auth_type, identifier'

    @raises
    ValidationError if the identifier is invalid for the authentication
    type
    """
    try:
        auth_type, identifier = user_id.split(':')
        auth_type = User.Type(auth_type)
    except ValueError:
        raise ValidationError(
            "Not a string of the form 'auth_type:identifier'")
    _check_valid_identifier_for_auth_type(auth_type, identifier)
    return auth_type, identifier


class User(models.Model):
    """
    The custom user model.

    This unfortunately duplicates a lot of the functionality
    of the AbstractBaseUser, but needs to because the password
    field is optional on the custom user models.
    """
    class Type(Enum):
        GOOGLEPLUS = 'googplus'
        FACEBOOK = 'facebook'
        BASIC = 'userpass'

        def __str__(self):
            return 'User.Type.{0}'.format(super().__str__())

    USERNAME_FIELD = 'user_id'
    REQUIRED_FIELDS = []
    objects = UserManager()

    email = models.EmailField(_('email address'))

    email_verified = models.BooleanField(default=False)

    # A user_id is a
    user_id = models.CharField(max_length=128, unique=True)

    ## Only provided if the user is authenticated via email + password
    password = models.CharField(_('password'), max_length=128, blank=True)

    ## Only provided if the user is authenticated via oauth credentials
    _credential = CredentialsField(_('credentials'), blank=True, null=True)

    date_joined = models.DateTimeField(_('date joined'), auto_now_add=True)

    # The date and time the user was last logged in
    last_login = models.DateTimeField(_('last login'), blank=True, null=True)

    @property
    def auth_type(self):
        return _parse_user_id(self.user_id)[0]

    @property
    def auth_identifier(self):
        return _parse_user_id(self.user_id)[1]

    def get_username(self):
        return self.user_id

    def get_auth_token(self, raw_password=None):
        """
        Return a bytestring containing a valid authorization token.
        If the user is a BASIC user, then a raw password must be provided.
        """
        if self.auth_type == self.Type.BASIC:
            if raw_password is None:
                raise ValueError('raw_password must be provided')
            userpass = '{0}:{1}'.format(self.auth_identifier, raw_password)
            userpass_bytes = userpass.encode('utf-8')
            b64_encoded = base64.urlsafe_b64encode(userpass_bytes)
            auth_token_bytes = b'Basic ' + b64_encoded
            return str(auth_token_bytes, encoding='utf-8')
        else:
            raise NotImplementedError('User.get_auth_token')

    def check_auth_token(self, token):
        components = token.split(' ')
        if len(components) != 2:
            return False
        auth_type = components[0]
        if auth_type == 'Basic':
            b64_encoded = components[1].encode('utf-8')
            userpass_bytes = base64.urlsafe_b64decode(b64_encoded)
            userpass = str(userpass_bytes, 'utf-8').split(':')
            try:
                user = User.objects.get_by_natural_key(User.Type.BASIC, userpass[0])
            except User.DoesNotExist:
                return False
            return user.check_password(userpass[1])
        else:
            raise NotImplementedError()

    def is_anonymous(self):
        """
        Always returns False. A way of comparing User objects to anonymous
        users
        """
        return False

    def is_authenticated(self):
        """
        Always returns True. A way to tell if the user has been authenticated
        in templates
        """
        return True

    def get_credential(self):
        if self._credential is None:
            return None
        storage = Storage(User, 'id', self.id, '_credential')
        return storage.get()

    def set_credential(self, credential):
        if self.auth_type == User.Type.BASIC:
            raise UserTypeError('Can not set credential on BASIC_USER')
        storage = Storage(User, 'id', self.id, '_credential')
        return storage.put(credential)

    credential = property(get_credential, set_credential)

    def set_password(self, raw_password):
        if self.auth_type != User.Type.BASIC:
            raise UserTypeError('Can only set password on BASIC_USER')
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        if self.auth_type != User.Type.BASIC:
            return False

        def setter(raw_password):
            self.set_password(raw_password)
            self.save(updated_fields=['password'])

        return check_password(raw_password, self.password, setter)

    def set_unusable_password(self):
        self.password = make_password(None)

    def has_usable_password(self):
        if self.auth_type != User.BASIC_USER:
            return False
        return is_password_usable(self.password)

    def get_short_name(self):
        return _parse_user_id(self.user_id)[1]

    def get_long_name(self):
        return _parse_user_id(self.user_id)[1]

    def __str__(self):
        return self.get_username()

    def to_json(self):
        return {
            "resource": "authentication#user",
            "auth_type": self.auth_type,
            "id": self.id,
            "date_joined": self.date_joined.isoformat(),
            "last_login": self.last_login.isoformat()
        }


class UserTypeError(Exception):
    pass
