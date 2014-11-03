from django.db import models
from common.models import ModelBase
from artist.models import Artist
from mod_venue.models import Venue


class Show(ModelBase):
    """
    A Show represents a performed act, avaiable for download
    on the site
    """

    # The artist who performed the show
    artist = models.ForeignKey(Artist)

    # The venue where the show was performed
    venue = models.OneToOneField(Venue)

