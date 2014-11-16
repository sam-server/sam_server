# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import oauth2client.django_orm


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=75, verbose_name='email address')),
                ('email_verified', models.BooleanField(default=False)),
                ('user_id', models.CharField(max_length=128, unique=True)),
                ('password', models.CharField(max_length=128, blank=True, verbose_name='password')),
                ('_credential', oauth2client.django_orm.CredentialsField(blank=True, null=True, verbose_name='credentials')),
                ('date_joined', models.DateTimeField(auto_now_add=True, verbose_name='date joined')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
