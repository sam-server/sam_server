import logging
from django.http import (JsonResponse, HttpResponseNotAllowed)
from django.shortcuts import render

from django.contrib.auth import authenticate, login

from oauth2client.client import (flow_from_clientsecrets, FlowExchangeError)
from json_utils import partial_json_response

from . import settings
from .models import User
from .resources import UserResource

logger = logging.getLogger(__name__)

user_resource = UserResource()


def register(request):
    if request.method == 'GET':
        return render(request, 'example/signup.html', {})
    elif request.method == 'POST':
        if request.JSON is None:
            return JsonResponse({'error': 'Expected a json object'}, status=400)
        return dispatch_on_auth_type(request)
    else:
        ## TODO: Should allow POST requests
        return HttpResponseNotAllowed(['GET'])


def dispatch_on_auth_type(request):
    try:
        auth_type = request.JSON['auth_type']
    except KeyError:
        return JsonResponse(
            {'error': "No 'auth_type' in request body"},
            status=400)
    if auth_type is User.Type.GOOGLEPLUS:
        return signin_as_google_user(request)
    elif auth_type is User.TYPE.BASIC:
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
        print('CREATING G+ user')
        user = User.objects.create_googleplus_user(credentials)

    user = authenticate(id_token=credentials.id_token)
    login(request, user)
    return partial_json_response(request, user_resource.to_json_value(user))


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
    except User.DoesNotExist:
        user = User.objects.create_basic_user(username=username,
                                              email=request.JSON['email'],
                                              password=request.JSON['password'])
    user = authenticate(username=user.username, password=user.password)
    login(request, user)
    return partial_json_response(request, user_resource.to_json_value(user))
