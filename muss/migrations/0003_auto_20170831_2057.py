# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-08-31 23:57
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('muss', '0002_auto_20170831_2055'),
    ]

    operations = [
        migrations.AlterField(
            model_name='forum',
            name='slug',
            field=models.SlugField(editable=False, max_length=100),
        ),
    ]
