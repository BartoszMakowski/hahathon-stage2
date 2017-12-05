# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-12-04 21:16
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('games', '0014_auto_20171204_2057'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='game',
            name='player_p1',
        ),
        migrations.RemoveField(
            model_name='game',
            name='player_p2',
        ),
        migrations.AddField(
            model_name='player',
            name='game',
            field=models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, related_name='players', to='games.Game'),
            preserve_default=False,
        ),
    ]
