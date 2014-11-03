from django.db import models
from common.models import ModelBase


class Venue(ModelBase):
    ## The user visible name of the venue
    name = models.CharField(max_length=128, unique=True)
