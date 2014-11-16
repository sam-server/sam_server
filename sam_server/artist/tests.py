import uuid
from django.test import TestCase
from .models import Artist



class ArtistTest(TestCase):
    def setUp(self):
        self.artist = Artist(name="test_artist")
        self.artist.save()
        self.handle_artist = Artist(name="test_artist", handle="test_artist")

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

    def test_artist_handle(self):
        self.assertEqual(
            self.artist.get_absolute_url(),
            "/artist/id/{0}".format(self.artist.id.hex)
        )
        self.assertEqual(
            self.handle_artist.get_absolute_url(),
            "/artist/test_artist"
        )

    def test_artist_resource(self):
        resource = self.artist.get_resource()
        self.assertEqual(
            resource,
            {
                "id": self.artist.id.hex,
                "href": '/artist/{0}'


            }
        )
