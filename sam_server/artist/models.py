
from django.db import models

from common.models import ModelBase
from common.utils import uuid_to_urlpath, urlpath_to_uuid
from django.core.urlresolvers import reverse
#from profile.models import ArtistProfile


def upload_avatar(instance, filename):
    print(instance)
    print(filename)
    uid = str(instance.id)
    return 'artist/{0}/avatars/{1}'.format(uid, filename)


class Artist(ModelBase):
    DEFAULT_AVATAR = 'artist/defaults/default_artist_avatar.jpg'

    ## The name of the artist
    name = models.CharField(max_length=128, unique=True, blank=True)
    ## A handle is a StringField, but can be None
    handle = models.CharField(max_length=128,
                              unique=True,
                              null=True,
                              default=None)

    avatar = models.ImageField(upload_to=upload_avatar,
                               blank=False, null=False,
                               default=DEFAULT_AVATAR)

    members = models.ManyToManyField('ProtoArtist', through='ArtistMembership')

    @classmethod
    def from_urlpath(self, urlpath):
        id = urlpath_to_uuid(urlpath)


    @property
    def urlpath(self):
        return uuid_to_urlpath(self.id)

    def get_absolute_url(self):
        """
        Returns the profile url of the artist
        """
        return reverse('artist.views.profile', args=[self.urlpath])

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

    ## The link to the artist that represents the [ProtoArtist], if
    ## the [ProtoArtist] releases work independently
    link = models.ForeignKey(Artist, null=True)


class ArtistMembership(ModelBase):
    """
    Represents a period in which a [ProtoArtist] is a member of a
    particular band
    """
    artist = models.ForeignKey(Artist)
    member = models.ForeignKey(ProtoArtist)

    # The role the artist had in the band
    role = models.CharField(max_length=128)

    # The date the [ProtoArtist] joined the band
    date_joined = models.DateField(null=False)
    date_left = models.DateField(null=True)
