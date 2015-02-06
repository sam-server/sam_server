# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import asset.models


class Migration(migrations.Migration):

    dependencies = [
        ('asset', '0006_auto_20150126_1831'),
    ]

    operations = [
        migrations.AlterField(
            model_name='asset',
            name='image',
            field=models.FileField(blank=True, upload_to=asset.models._asset_image_upload_location, max_length=1024),
            preserve_default=True,
        ),
    ]
