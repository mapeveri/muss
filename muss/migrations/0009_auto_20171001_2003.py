# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-10-01 23:03
from __future__ import unicode_literals

import django.contrib.postgres.fields.jsonb
from django.db import migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('muss', '0008_forum_public_forum'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='likecomment',
            name='user',
        ),
        migrations.AddField(
            model_name='likecomment',
            name='data',
            field=django.contrib.postgres.fields.jsonb.JSONField(default=dict),
            preserve_default=False,
        ),
    ]