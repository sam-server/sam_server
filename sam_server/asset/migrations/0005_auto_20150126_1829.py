# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import uuid
import asset.models
import common.fields


class Migration(migrations.Migration):

    dependencies = [
        ('asset', '0004_remove_asset_qr_code'),
    ]

    operations = [
        migrations.CreateModel(
            name='AssetAttachement',
            fields=[
                ('id', common.fields.UUIDField(default=uuid.uuid4, primary_key=True, max_length=32, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=128)),
                ('type', models.CharField(max_length=64)),
                ('location', models.FilePathField()),
                ('upload_date', models.DateField(auto_now=True)),
                ('asset', models.ForeignKey(to='asset.Asset')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='asset',
            name='image',
            field=models.FileField(null=True, upload_to=asset.models._asset_image_upload_location),
            preserve_default=True,
        ),
    ]
