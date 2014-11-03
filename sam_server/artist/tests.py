import uuid
from django.test import TestCase
from .models import Artist

from .services import lookup_artist


class ArtistTest(TestCase):
    def setUp(self):
        self.artist = Artist(name="test_artist")
        self.artist.save()

    def tearDown(self):
        self.artist.delete()

    def test_absolute_url(self):
        artist_url = self.artist.get_absolute_url()
        self.assertEqual(
            artist_url,
            '/artist/{0}'.format(self.artist.id.int)
        )

    def test_get_artist(self):
        int_id = self.artist.id.int
        artist = Artist.objects.get(id=uuid.UUID(int=int_id))
        self.assertEqual(artist.name, self.artist.name)

