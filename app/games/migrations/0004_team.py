# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-06-05 19:02
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('games', '0003_stadium_capacity'),
    ]

    operations = [
        migrations.CreateModel(
            name='Team',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, verbose_name='Name')),
                ('conference', models.CharField(max_length=20, null=True, verbose_name='Conference')),
                ('city', models.CharField(blank=True, max_length=50, null=True, verbose_name='City')),
                ('state', models.CharField(blank=True, max_length=20, null=True, verbose_name='State')),
                ('yearJoined', models.IntegerField(default=-9999, null=True, verbose_name='yearJoined')),
            ],
        ),
    ]
