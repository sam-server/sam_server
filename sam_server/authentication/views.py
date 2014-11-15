import importlib
import logging
import os
from django.http import (JsonResponse, HttpResponseNotAllowed)
from django.shortcuts import render

from oauth2client.client import (
    verify_id_token, flow_from_clientsecrets, FlowExchangeError)

from .models import User

logger = logging.getLogger(__name__)

GOOGLE_AUTH_SETTINGS = (
    importlib.import_module(os.environ['DJANGO_SETTINGS_MODULE'])
    .GOOGLE_AUTH_SETTINGS)


def register(request):
    if request.method == 'GET':
        return render('example/signup.html', {})
    else:
        ## TODO: Should allow POST requests
        return HttpResponseNotAllowed(['GET'])


def signup_google_user(request):
    """
    Step 2 of the hybrid flow which authenticates a google user
    """

    if request.method != 'POST':
        return HttpREsponseNotAllowed(['POST'])
    if request.JSON is None:
        response = JsonResponse({'error': 'Expected a json object'})
        response.status_code = 400
        return response
    try:
        auth_code = request.JSON['auth_code']
    except KeyError:
        response = JsonResponse({'error': "No 'auth_code' in json"})
        response.status_code = 400
        return response

    try:
        oauth_flow = flow_from_clientsecrets(
            GOOGLE_AUTH_SETTINGS['PATH_TO_JSON_SECRETS'],
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

    if credentials.client_id != GOOGLE_AUTH_SETTINGS['CLIENT_ID']:
        response = JsonResponse({
            'error': 'Unexpected audience {0}'.format(credentials.client_id)
        })
    id_token = credentials.id_token

def signin_google_user(request):
    bearer_token = request.META['HTTP_AUTHORIZATION']
    if bearer_token is None or not bearer_token.startswith('Bearer '):
        bearer_token = bearer_token[len('Bearer '):]
    id_token = verify_id_token(
        bearer_token,
        audience=GOOGLE_AUTH_SETTINGS['CLIENT_ID'])










