from functools import wraps

from urllib.parse import quote_plus

from django.contrib.auth import authenticate, login
from django.http import JsonResponse, HttpResponseRedirect
from django.utils.decorators import available_attrs


def authorization_required(view_func):
    """
    Decorator that checks the 'Authorization' header for
    credentials required to log the user in.

    If no 'Authorization' header is found on the request,
    an HttpResponseForbidden response will be raised.
    """
    @wraps(view_func, assigned=available_attrs(view_func))
    def decorator(request, *args, **kwargs):
        if not request.user.is_authenticated():
            try:
                auth_header = request.META['HTTP_AUTHORIZATION']
            except KeyError:
                return HttpResponseRedirect(
                    '/auth/login?cb={0}'.format(quote_plus(request.path))
                )
                # return JsonResponse({
                #    'error': 'No Authorization header on request'
                #}, status=403)
            user = authenticate(auth_header=auth_header)
            if user is None:
                return JsonResponse({
                    'error': 'Could not authenticate user'
                }, status=403)
            login(request, user)
        return view_func(request, *args, **kwargs)
    return decorator

