
## For testing with credential authentication
## we currently use the credentials for my google account.

## TODO: Create a new google account just for testing

import json

from oauth2client import client
from httplib2 import Http

from .settings import GOOGLE_AUTHENTICATION


def create_test_credentials():
    with open(GOOGLE_AUTH_SETTINGS['TEST_CREDENTIALS_PATH']) as f:
        json = json.loads(f.readlines())
    creds = client.OAuth2Credentials.from_json(json)
    creds.refresh(Http())
    return creds




