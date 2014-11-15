# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='user',
            old_name='credential',
            new_name='_credential',
        ),
        migrations.RemoveField(
            model_name='user',
            name='auth_type',
        ),
    ]
