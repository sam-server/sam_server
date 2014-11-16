"""
Django settings for sam_server project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'tzxnf8yo$xxky_zuvcx82%hj2&0-fto#ak0is*nb9s3lav%#*x'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'authentication',
    'artist',
    'mod_venue',
    'mod_show',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    ## Adds a JSON attribute to request, which is filled with the
    ## json content of the request, if the content type is application/json
    ## and the request has a body
    'json_utils.middleware.JsonRequestMiddleware',
    # Better to handle the json requests using the rest framework
    #'common.jsonrpc.middleware.JsonRpcMiddleware',
)

ROOT_URLCONF = 'sam_server.urls'
# TODO: remove this completely
#ROOT_SERVICESCONF = 'sam_server.services'

WSGI_APPLICATION = 'sam_server.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'samserverdb',
        'USER': 'sam_server',
        'PASSWORD': 'connect'
    }
}


## Set up caches for the server
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211'
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

STATIC_URL = '/static/'

STATICFILES_DIRS = (
    # build directory of dart project
    "/Users/ovangle/Programming/sam_server2_workspace/cs_client/",
)

TEMPLATE_DIRS = (
    # build directory of dart project
    "/Users/ovangle/Programming/sam_server2_workspace/cs_client/",
)


MEDIA_URL = '/media/'

# The root directory for uploaded files on the filesystem
# FIXME: This should be replaced by a custom storage
MEDIA_ROOT = 'media/'

## Configuration for controlling cors request handling
# See https://github.com/ottoyiu/django-cors-headers
CORS_ORIGIN_ALLOW_ALL = True

# Set up the session
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'

LOGGING = {
    'version': 1,
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['console'],
            'propagate': True,
            'level': 'DEBUG'
        }
    }
}

# Authentication
# Important ##
# AUTH_USER_MODEL specifies the custom user model (which supports oauth authentication)
# Must be set before attempting to make or apply any migrations
AUTH_USER_MODEL = 'authentication.User'

AUTHENTICATION_BACKENDS = (
    'authentication.backends.BasicUserBackend',
    'authentication.backends.GoogleUserBackend',
)


# Settings for authenticating with google services
GOOGLE_AUTHENTICATION = {
    'CLIENT_ID': '291208690985-jpbik0s2qsrucjv1llaa4j34iktrnofk.apps.googleusercontent.com',
    'EMAIL': '291208690985-jpbik0s2qsrucjv1llaa4j34iktrnofk@developer.gserviceaccount.com',
    'CLIENT_SECRET': 'eL2za8MDCpvwdoUC_k5O4mPa',
    'PATH_TO_JSON_SECRETS': '/Users/ovangle/Programming/auth/cultivated_era_759/client_secrets.json',
    'REQUIRED_SCOPES': [
        'https://www.googleapis.com/auth/userinfo.email',
    ],
    'TEST_CREDENTIALS_PATH': '/Users/ovangle/Programming/auth/cultivated_era_759/test_credentials.json',
}
