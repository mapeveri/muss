# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-09-27 02:02
from __future__ import unicode_literals

import django.contrib.postgres.fields.jsonb
from django.db import migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('muss', '0006_auto_20170916_0938'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='hitcounttopic',
            name='created',
        ),
        migrations.RemoveField(
            model_name='hitcounttopic',
            name='ip',
        ),
        migrations.RemoveField(
            model_name='hitcounttopic',
            name='session',
        ),
        migrations.AddField(
            model_name='hitcounttopic',
            name='data',
            field=django.contrib.postgres.fields.jsonb.JSONField(default=None),
            preserve_default=False,
        ),
    ]
