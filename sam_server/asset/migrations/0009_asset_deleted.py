# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('asset', '0008_auto_20150206_0450'),
    ]

    operations = [
        migrations.AddField(
            model_name='asset',
            name='deleted',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
