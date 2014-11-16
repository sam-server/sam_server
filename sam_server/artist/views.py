import json
import logging
from slugify import slugify

from django import http
from django.shortcuts import get_object_or_404, render


from json_utils.resource import partial_response
from .models import Artist

logger = logging.getLogger(__name__)

## A list of separators that can be used to encode an artist handle
## We iterate through this trying to find a unique handle for the artist.
## The slugified name may not be unique after eliminating unicode
HANDLE_SEPARATORS = ('-', '+', '_', '~')


def profile_by_handle(request, handle):
    if request.method != 'GET':
        raise http.HttpResponseNotAllowed(['GET'])
    try:
        artist = Artist.objects.filter(handle=handle).get()
    except Artist.DoesNotExist:
        raise http.Http404()

    resource = artist.get_resource()
    format = request.GET.get('format', None).lower()
    if format == 'json':
        return partial_response(request, resource)
    return render(request, 'web/profile/profile.html', resource)


def create_artist_resource(request):
    """
    Create the artist's basic info from a json resource
    The keys in the resource are as follows
    """
    ct = request.META['CONTENT_TYPE']
    if not ct.startswith('application/json'):
        raise http.HttpResponseBadRequest('Expected json')
    resource = json.loads(''.join(request.readlines()))
    try:
        name = resource['name']
    except KeyError:
        raise http.HttpResponseBadRequest('No \'name\' in json resource')
    ## Test whether the name is unique
    if Artist.objects.filter(name=name).exists():
        raise http.HttpResponseConflict('name already exists')
    handle = None
    for separator in HANDLE_SEPARATORS:
        handle = slugify(name, separator=separator)
        if not Artist.objects.filter(handle=handle).exists():
            break
    if not handle:
        raise http.HttpResponseConflict(
            'Could not generate unique handle from name')
    artist = Artist(name=name, handle=handle)
    artist.save()
    return partial_response(artist.get_resource(),
                            fields=request.GET.get('fields', None))

def dashboard(request, artist_id):
    """
    Gets the artist dashboard corresponding to the artist id
    """
    pass


def profile(request):
    if request.method == 'GET':
        return get_profile(request)
    elif request.method == 'POST':
        return create_artist_resource(request)


def get_profile(request):
    query_set = request.GET
    format = query_set.get('format', None)
    try:
        id = query_set['id']
        artist = Artist.objects.filter(id=id).get()
    except (KeyError, Artist.DoesNotExist) as e:
        raise http.Http404(e)
    resource = artist.get_resource()
    if format == 'JSON':
        return partial_response(resource, query_set.get('fields', None))










