# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('asset', '0002_auto_20141130_0702'),
    ]

    operations = [
        migrations.AlterField(
            model_name='asset',
            name='date_purchased',
            field=models.DateField(null=True),
            preserve_default=True,
        ),
    ]
