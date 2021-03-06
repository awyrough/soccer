# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-07-04 00:32
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('games', '0014_stadium_home_team'),
    ]

    operations = [
        migrations.RenameField(
            model_name='game',
            old_name='awayTeam',
            new_name='away_team',
        ),
        migrations.RenameField(
            model_name='game',
            old_name='homeTeam',
            new_name='home_team',
        ),
        migrations.AlterUniqueTogether(
            name='game',
            unique_together=set([('home_team', 'away_team', 'date')]),
        ),
    ]
