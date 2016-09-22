import csv
import datetime

from django.core.management.base import BaseCommand, CommandError
from games.models import Game, Team

class Command(BaseCommand):
    help = 'Populate Game table'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        filename = "raw_data/gameMaster2016_incomplete.csv"
        f = open(filename, 'rU')
        reader = csv.reader(f)
        count = 0
        for game_data in reader:
            
            if count == 0:
                count = 1
                continue
            
            date = datetime.datetime.strptime(game_data[0], "%m/%d/%y").date()
            home_team_id = game_data[1]
            home_team = Team.objects.get(sw_id=home_team_id)
            away_team = Team.objects.get(sw_id=game_data[5])
            new_game = Game.objects.create(date=date,
                                           home_team=home_team,
                                           away_team=away_team)
