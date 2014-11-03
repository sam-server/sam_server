# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import common.fields
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('artist', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ArtistMembership',
            fields=[
                ('id', common.fields.UUIDField(default=uuid.uuid4, serialize=False, max_length=32, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('role', models.CharField(max_length=128)),
                ('date_joined', models.DateField()),
                ('date_left', models.DateField(null=True)),
                ('artist', models.ForeignKey(to='artist.Artist')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ProtoArtist',
            fields=[
                ('id', common.fields.UUIDField(default=uuid.uuid4, serialize=False, max_length=32, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=128)),
                ('link', models.ForeignKey(null=True, to='artist.Artist')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='artistmembership',
            name='member',
            field=models.ForeignKey(to='artist.ProtoArtist'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='artist',
            name='members',
            field=models.ManyToManyField(to='artist.ProtoArtist', through='artist.ArtistMembership'),
            preserve_default=True,
        ),
    ]
