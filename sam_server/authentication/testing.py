
## For testing with credential authentication
## we currently use the credentials for my google account.

## TODO: Create a new google account just for testing

import base64

from oauth2client import client
from httplib2 import Http

from .settings import GOOGLE_AUTHENTICATION

_test_credentials = None

def load_test_credentials():
    """
    Load a set of test credentials from the value configured
    in GOOGLE_AUTHENTCATION.TEST_CREDENTIALS_PATH
    """
    global _test_credentials
    if _test_credentials is None:
        with open(GOOGLE_AUTHENTICATION['TEST_CREDENTIALS_PATH']) as f:
            content = f.read()
        _test_credentials = client.OAuth2Credentials.from_json(content)
        _test_credentials.refresh(Http())
    return _test_credentials


def make_basic_authorization_header(username, password):
    userpass = '{0}:{1}'.format(username, password).encode('utf-8')
    encoded = base64.b64encode(userpass)
    return 'Basic {0}'.format(str(encoded, encoding='utf-8'))
