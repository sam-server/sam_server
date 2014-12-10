
from django.db import models

from common.models import ModelBase
from django.core.urlresolvers import reverse
#from profile.models import ArtistProfile

DEFAULT_AVATAR = 'artist/defaults/default_artist_avatar.jpg'


def upload_avatar(instance, filename):
    folder = instance.get_folder()
    return folder + 'avatars/{1}'.format(filename)


class Artist(ModelBase):
    ## The name of the artist
    name = models.CharField(max_length=128, unique=True, blank=True)
    ## A handle is a StringField, but can be None
    handle = models.CharField(max_length=128, unique=True)

    avatar = models.ImageField(upload_to=upload_avatar,
                               blank=False, null=False,
                               default=DEFAULT_AVATAR)

    country = models.CharField(max_length=128, blank=False)
    website = models.URLField(blank=False)

    is_verified = models.BooleanField(default=False, blank=False)

    members = models.ManyToManyField('ProtoArtist', through='ArtistMembership')

    def get_absolute_url(self):
        """
        Returns the profile url of the artist
        """
        return reverse('artist.views.profile_by_handle', args=[self.handle])

    def get_resource(self):
        resource = {
            'id': self.id.hex,
            'name': self.name,
            'country': self.country,
            'href': self.get_absolute_url(),
        }
        resource['members'] = [m.get_resource() for m in self.members.all()]
        return resource

    def get_folder(self):
        return 'artist/{0}/'.format(self.id.hex)

    def __str__(self):
        return self.name


class ProtoArtist(ModelBase):
    """
    A ProtoArtist is an artist which might not yet exist on the platform,
    or which exists on the platform but is displayed under a different name.

    For example, a guitarist in a band might be displayed under the name
    "George Smith" when playing in the band that they are a member of,
    but might also release works as another artist
    """
    name = models.CharField(max_length=128)

    image = models.ImageField(upload_to=upload_avatar,
                              blank=False, null=False,
                              default=DEFAULT_AVATAR)

    # The role that the ProtoArtist plays in the band (eg. guitarist)
    role = models.CharField(max_length=128)

    # The date the member joined the band (if there is one)
    date_joined = models.DateField(null=True)

    # The date the member left the band (if there is one)
    date_left = models.DateField(null=True)

    ## The link to the artist that represents the [ProtoArtist], if
    ## the [ProtoArtist] releases work independently
    link = models.ForeignKey(Artist, null=True)

    def get_folder(self):
        artist = self.artist
        artist_folder = artist.get_folder()
        return artist_folder + 'members/{0}/'.format(self.id.hex)

    def get_resource(self):
        resource = {
            "id": self.id.hex,
            "name": self.name,
            "role": self.role,
            "image": get_image_resource(self.image, "{0}".format(self.name))
        }
        if self.date_joined is not None:
            resource['date_joined'] = self.date_joined.isoformat()
        if self.date_left is not None:
            resource['date_left'] = self.date_left.isoformat()
        if self.link is not None:
            resource['link'] = self.link.get_absolute_url()
        return resource

    def __str__(self):
        return 'artist: {0} name: {1}'.format(self.artist, self.name)


class ArtistMembership(ModelBase):
    artist = models.ForeignKey(Artist)
    member = models.ForeignKey(ProtoArtist)

