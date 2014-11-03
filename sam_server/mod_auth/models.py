from datetime import datetime, timedelta

from django.db import models


class User(models.Model):
    #id = database.idField
    #created = database.created_field
    #updated = database.updated_field

    name = models.CharField(max_length=128, unique=True)
    email = models.CharField(max_length=128, unique=True)

    ## A token which allows the refreshing of user credentials
    refresh_token = models.CharField(max_length=36)


class Session(models.Model):

    DURATION = timedelta(seconds=3600)

    #id = database.idField
    #created = database.created_field
    #updated = database.updated_field

    user = models.ForeignKey(User)
    token = models.CharField(max_length=36)

    @property
    def is_expired(self):
        return datetime.now() - self.updated > Session.DURATION

