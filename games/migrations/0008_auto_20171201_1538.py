# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-12-01 15:38
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('games', '0007_auto_20171201_1500'),
    ]

    operations = [
        migrations.AlterField(
            model_name='game',
            name='guest',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='guest', to='user.Player'),
        ),
    ]
