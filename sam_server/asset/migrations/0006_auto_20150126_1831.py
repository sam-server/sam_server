# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import asset.models


class Migration(migrations.Migration):

    dependencies = [
        ('asset', '0005_auto_20150126_1829'),
    ]

    operations = [
        migrations.AlterField(
            model_name='asset',
            name='image',
            field=models.FileField(upload_to=asset.models._asset_image_upload_location, blank=True, default=''),
            preserve_default=False,
        ),
    ]
