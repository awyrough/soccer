# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-07-14 02:38
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0003_auto_20160713_0353'),
    ]

    operations = [
        migrations.AlterField(
            model_name='statisticevent',
            name='action',
            field=models.CharField(choices=[('BLOCK', 'Block'), ('CLEARANCE', 'Clearance'), ('CORNER_CROSS', 'Corner Cross'), ('CROSS', 'Cross'), ('DEFLECTION', 'Deflection'), ('DIRECT_FREE_KICK_CROSS', 'Direct Free Kick Cross'), ('DIRECT_FREE_KICK_PASS', 'Direct Free Kick Pass'), ('DIRECT_FREE_KICK_SHOT', 'Direct Free Kick Shot'), ('DRIBBLE', 'Dribble'), ('DROP_BALL', 'Drop Ball'), ('FOUL', 'Foul'), ('FOUL_THROW', 'Foul Throw'), ('GOAL', 'Goal'), ('GOAL_KICK', 'Goal Kick'), ('GOALKEEPER_CATCH', 'Goalkeeper Catch'), ('GOALKEEPER_DROP_CATCH', 'Goalkeeper Drop Catch'), ('GOALKEEPER_KICK', 'Goalkeeper Kick'), ('GOALKEEPER_PICK_UP', 'Goalkeeper Pick Up'), ('GOALKEEPER_PUNCH', 'Goalkeeper Punch'), ('GOALKEEPER_SAVE', 'Goalkeeper Save'), ('GOALKEEPER_SAVE_CATCH', 'Goalkeeper Save Catch'), ('GOALKEEPER_THROW', 'Goalkeeper Throw'), ('HANDBALL', 'Handball'), ('HEADER', 'Header'), ('HEADER_SHOT', 'Header Shot'), ('INDIRECT_FREE_KICK_CROSS', 'Indirect Free Kick Cross'), ('INDIRECT_FREE_KICK_PASS', 'Indirect Free Kick Pass'), ('KICK_OFF', 'Kick Off'), ('OFFSIDE', 'Offside'), ('OWN_GOAL', 'Own Goal'), ('PASS', 'Pass'), ('PENALTY_SHOT', 'Penalty Shot'), ('RED_CARD', 'Red Card'), ('SHOT', 'Shot'), ('START_OF_HALF', 'Start Of Half'), ('SUBSTITUTION', 'Substitution'), ('TACKLE', 'Tackle'), ('THROWN_IN', 'Thrown In'), ('TOUCH', 'Touch'), ('YELLOW_CARD', 'Yellow Card')], default='TOUCH', max_length=50),
        ),
    ]
