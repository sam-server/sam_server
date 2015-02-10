from datetime import datetime, timedelta
import logging
from urllib.parse import quote as url_quote
from django.http import (JsonResponse, HttpResponseNotAllowed)
from django.http import (HttpResponseForbidden)
from django.shortcuts import render
from django.core.context_processors import csrf

from django.contrib.auth import authenticate, login

from oauth2client.client import (flow_from_clientsecrets, FlowExchangeError)
from ext_utils.json import partial_json_response

## TODO: Replace all renders by this
from ext_utils.html import render as render2

from . import settings
from .models import User
from .resources import UserResource

logger = logging.getLogger(__name__)

USER_RESOURCE = UserResource()


def login_user(request):
    """
    Log in a user via basic authentication
    """
    if request.method == 'GET':
        context = {}
        context.update(csrf(request))
        return render2('auth/login.html', context)
    elif request.method == 'POST':
        if request.JSON is None:
            return JsonResponse(
                {'error': 'not a json request'},
                400
            )
        resource = USER_RESOURCE.to_python(request.JSON)
        username = resource.get('username')
        if username is not None:
            password = resource.get('password')
            if password is None:
                return HttpResponseForbidden('password required for user resource')

            user = authenticate(username=username, password=password)
            if user is None:
                return HttpResponseForbidden('invalid username or password')
            login(request, user)

            remembered = resource.get('remembered', False)

            result_resource = USER_RESOURCE.to_json(user)
            del result_resource['password']
            response = partial_json_response(request, result_resource)

            auth_token = user.get_auth_token(resource['password'])

            auth_token_expires = None
            if remembered:
                auth_token_expires = datetime.now() + timedelta(weeks=1)

            response.set_cookie(
                'authToken',
                url_quote(auth_token),
                expires=auth_token_expires,
                ## TODO: Authentication token should be httponly
                #httponly=True
            )

            return response
        else:
            ## TODO: Handle other types of login
            raise NotImplementedError()
    else:
        return HttpResponseNotAllowed(['GET', 'POST'])

"""
def register_user(request):
    if request.method == 'GET':
        context = {}
        context.update(csrf(request))
        return render2('auth/register.html', context)
    elif request.method == 'POST':
        if request.JSON is None:
            return JsonResponse({'error': 'Expected a JSON request'})
"""


def register(request):
    if request.method == 'GET':
        context = {}
        context.update(csrf(request))
        return render2('auth/register.html', context)
    elif request.method == 'POST':
        if request.JSON is None:
            return JsonResponse({'error': 'Expected a json object'}, status=400)
        return dispatch_on_auth_type(request)
    else:
        ## TODO: Should allow POST requests
        return HttpResponseNotAllowed(['GET'])


def dispatch_on_auth_type(request):
    try:
        auth_type = User.Type(request.JSON['auth_type'])
    except KeyError:
        return JsonResponse(
            {'error': "No 'auth_type' in request body"},
            status=400)
    if auth_type is User.Type.GOOGLEPLUS:
        return signin_as_google_user(request)
    elif auth_type is User.Type.BASIC:
        return register_basic_user(request)
    elif auth_type == User.Type.FACEBOOK:
        raise NotImplementedError('Facebook user')
    else:
        return JsonResponse(
            {'error': "Invalid 'auth_type' in request ({0})".format(auth_type)},
            status=400
        )


def signin_as_google_user(request):
    """
    Step 2 of the hybrid flow which authenticates a google user
    """
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])
    try:
        auth_code = request.JSON['auth_code']
    except KeyError:
        return JsonResponse({'error': "No 'auth_code' in json"}, status=400)

    try:
        ## TODO: redirect_uri should be a valid uri
        oauth_flow = flow_from_clientsecrets(
            settings.GOOGLE_AUTHENTICATION['PATH_TO_JSON_SECRETS'],
            scope=['openid', 'profile', 'email'],
            redirect_uri='postmessage')
        credentials = oauth_flow.step2_exchange(auth_code)
    except FlowExchangeError as e:
        logger.warn(str(e))
        response = JsonResponse({
            'error': 'Could not exchange for valid credentials',
            'data': str(e)
        })
        response.status_code = 400
        return response

    if credentials.client_id != settings.GOOGLE_AUTHENTICATION['CLIENT_ID']:
        response = JsonResponse({
            'error': 'Unexpected audience {0}'.format(credentials.client_id)
        })
    sub = credentials.id_token['sub']
    ## Check if the user already exists
    try:
        user = User.objects.get_by_natural_key(User.Type.GOOGLE, sub)
    except User.DoesNotExist:
        user = User.objects.create_googleplus_user(credentials)

    user = authenticate(id_token=credentials.id_token)
    login(request, user)
    return partial_json_response(request, USER_RESOURCE.to_json(user))


def register_basic_user(request):
    """
    Register a user with username and password
    """
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])
    if request.JSON is None:
        return JsonResponse(
            {'error': 'Expected a json request'}, status=400)
    for key in ('email', 'username', 'password'):
        if key not in request.JSON:
            return JsonResponse(
                {'error': 'Required key {0} not found in body'.format(key)},
                status=400)
    username = request.JSON['username']
    try:
        user = User.objects.get_by_natural_key(User.Type.BASIC, username)
        return JsonResponse({'error': 'User already exists'},
                            status=400)
    except User.DoesNotExist:
        user = User.objects.create_basic_user(username=username,
                                              email=request.JSON['email'],
                                              password=request.JSON['password'])

    response = partial_json_response(request, USER_RESOURCE.to_json(user))
    auth_token = user.get_auth_token(request.JSON['password'])

    response.set_cookie(
        'authToken',
        url_quote(auth_token),
        ## TODO: auth token should be http only.
        # httponly=True
    )
    return response
