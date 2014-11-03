"""
Defines models common to all of the sam server models
"""

import uuid

from django.db import models

from .fields import UUIDField


class ModelBase(models.Model):
    """
    Define our own model base, which implements fields common
    to all models
    """
    #TODO: Change to UUIDField when upgrading to next version of
    # django
    id = UUIDField(primary_key=True, default=uuid.uuid4)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    @property
    def uuid(self):
        return uuid.UUID(self.id)
