# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-12-04 00:25
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0004_player_owner'),
    ]

    operations = [
        migrations.AlterField(
            model_name='player',
            name='game_id',
            field=models.IntegerField(null=True),
        ),
    ]
