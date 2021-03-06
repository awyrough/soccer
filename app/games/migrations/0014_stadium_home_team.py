# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-07-03 16:59
from __future__ import unicode_literals
import csv

from django.db import migrations, models
import django.db.models.deletion

def add_team(apps, schema_editor):
    Stadium = apps.get_model("games", "Stadium")
    Team = apps.get_model("games", "Team") 
    filename = "raw_data/venues.csv"
    f = open(filename, 'rU')
    reader = csv.reader(f)
    count = 0
    for stadium_data in reader:
        if count == 0:
            count = 1
            continue
        stadium = Stadium.objects.get(sw_id=stadium_data[0])
        team = Team.objects.get(name=stadium_data[2])
        stadium.home_team = team
        stadium.save()

def reverse_func(apps, schema_editor):
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('games', '0013_auto_20160703_1654'),
    ]

    operations = [
        migrations.AddField(
            model_name='stadium',
            name='home_team',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='games.Team'),
            preserve_default=False,
        ),
    ]
