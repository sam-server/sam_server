# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('asset', '0003_auto_20141130_0702'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='asset',
            name='qr_code',
        ),
    ]
