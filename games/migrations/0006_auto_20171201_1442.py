# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-12-01 14:42
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('games', '0005_auto_20171201_1440'),
    ]

    operations = [
        migrations.AlterField(
            model_name='game',
            name='guest',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='guest', to='user.Player'),
        ),
    ]
