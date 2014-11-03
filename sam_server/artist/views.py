import json
import traceback

from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, render

from common.utils import uuid_to_urlpath, urlpath_to_uuid
from .models import Artist


def profile(request, artist_id):
    """
    Gets the full artist for the given artist id
    """
    if request.method == 'GET':
        try:
            return profile_GET(request, artist_id)
        except Exception as e:
            traceback.print_exc()
            raise e
    if request.method == 'POST':
        return profile_POST(request, artist_id)


def profile_GET(request, artist_id):
    try:
        artist_id = urlpath_to_uuid(artist_id)
    except ValueError:
        raise Http404()
    host = request.get_host()
    artist = get_object_or_404(Artist, id=artist_id)
    artist_json = {
        'id': uuid_to_urlpath(artist.id),
        'name': artist.name,
        'avatar_src': host + artist.avatar.url,
        'href': host + artist.get_absolute_url()
    }

    format = request.GET.get('format', None)
    if format == 'json':
        return HttpResponse(
            json.dumps(artist_json),
            content_type='application/json; charset=utf-8'
        )
    return render(request, 'web/profile/profile.html', artist_json)


def profile_POST(request, artist_id):
    try:
        artist_id = urlpath_to_uuid(artist_id)
    except ValueError:
        raise Http404()


def dashboard(request, artist_id):
    """
    Gets the artist dashboard corresponding to the artist id
    """
    pass
