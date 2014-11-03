# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import artist.models
import common.fields
import uuid


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Artist',
            fields=[
                ('id', common.fields.UUIDField(default=uuid.uuid4, serialize=False, max_length=32, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(unique=True, blank=True, max_length=128)),
                ('handle', models.CharField(default=None, max_length=128, unique=True, null=True)),
                ('avatar', models.ImageField(default='artist/defaults/default_artist_avatar.jpg', upload_to=artist.models.upload_avatar)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
    ]
