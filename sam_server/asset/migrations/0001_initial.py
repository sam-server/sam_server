# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import common.fields
from django.conf import settings
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Asset',
            fields=[
                ('id', common.fields.UUIDField(default=uuid.uuid4, primary_key=True, max_length=32, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('qr_code', models.CharField(unique=True, max_length=256)),
                ('name', models.CharField(max_length=128)),
                ('description', models.CharField(max_length=1024)),
                ('use', models.CharField(max_length=256)),
                ('model_number', models.CharField(max_length=128)),
                ('vendor', models.CharField(max_length=128)),
                ('price_value', models.IntegerField()),
                ('price_currency_code', models.CharField(max_length=3)),
                ('date_purchased', models.DateField()),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
    ]
