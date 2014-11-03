"""
Services defined for the artist module
"""
from common.jsonrpc import method
from .models import Artist
from .views import urlpath_to_uuid, uuid_to_urlpath


def lookup_artist(http_request, artist_id, fields=None):
    uuid = urlpath_to_uuid(artist_id)
    artist = Artist.objects.filter(id=uuid)
    return artist.to_json()

methods = (
    method('get', lookup_artist),
)
