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
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('user_id', models.CharField(unique=True, max_length=128)),
                ('email', models.EmailField(max_length=75, verbose_name='email address')),
                ('email_verified', models.BooleanField(default=False)),
                ('auth_type', models.CharField(max_length=8, choices=[('googplus', 'Google+'), ('facebook', 'Facebook'), ('userpass', 'Email + password')])),
                ('password', models.CharField(blank=True, max_length=128, verbose_name='password')),
                ('credential', oauth2client.django_orm.CredentialsField(blank=True, verbose_name='credentials', null=True)),
                ('date_joined', models.DateTimeField(auto_now_add=True, verbose_name='date joined')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
