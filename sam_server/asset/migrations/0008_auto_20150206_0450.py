# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import asset.models


class Migration(migrations.Migration):

    dependencies = [
        ('asset', '0007_auto_20150205_0817'),
    ]

    operations = [
        migrations.AlterField(
            model_name='asset',
            name='image',
            field=models.FileField(max_length=1024, blank=True, null=True, upload_to=asset.models._asset_image_upload_location),
            preserve_default=True,
        ),
    ]
