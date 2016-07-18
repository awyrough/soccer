import csv
import datetime

from django.core.management.base import BaseCommand, CommandError
from games.models import Game, Team
from events.models import TimeEvent

class Command(BaseCommand):
    help = 'Populate statistic events table'

    def add_arguments(self, parser):
        # add file path argument
        parser.add_argument(
            "--file",
            dest="file_path",
            default="",
            help="path to file from which to import data",
            )
        # add optional clearing flag
        parser.add_argument(
            "--clear",
            action="store_true",
            dest="clear",
            default=False,
            help="clear all existing statistics events before import",
            )
        # add dry-run flag
        parser.add_argument(
            "--dry-run",
            action="store_true",
            dest="dry_run",
            default=False,
            help="just run import and data mgmt, don't save",
            )

    def handle(self, *args, **options):
        if not options["file_path"]:
            raise Exception("File path required")
        file_path = options["file_path"]

        dry_run = options["dry_run"]
        clear = options["clear"]

        # open the file
        f = open(file_path, 'rU')
        reader = csv.reader(f)

        # to prevent constantly looking things up
        name_to_team = {}
        games = set()
        
        minute_events = []

        # iterate over the rows
        first = True
        for event in reader:
            if first:
                first = False
                continue
            
            # this is really fragile, can we guarentee the team names
            # in the file are a certain format?
            team_str = event[1]
            split_str = " v "
            home_team_name = team_str.split(split_str)[0].strip() \
                .replace("FC", "").strip()
            away_team_name = team_str.split(split_str)[1].strip() \
                .replace("FC", "").strip()

            if home_team_name == "Los Angeles Galaxy":
                home_team_name = "Galaxy"
            if away_team_name == "Los Angeles Galaxy":
                away_team_name = "Galaxy"

            print home_team_name
            print away_team_name

            if (home_team_name in name_to_team):
                home_team = name_to_team[home_team_name]
            else:
                home_team = Team.objects.get(name__contains=home_team_name)
                name_to_team[home_team_name] = home_team

            if (away_team_name in name_to_team):
                away_team = name_to_team[away_team_name]
            else:
                away_team = Team.objects.get(name__contains=away_team_name)
                name_to_team[away_team_name] = away_team

            date = datetime.datetime.strptime(event[2], "%d/%m/%Y")
                
            game = Game.objects.filter(date=date) \
                .filter(home_team=home_team) \
                .get(away_team=away_team)
            games.add(game)

            action_team_name = event[0].replace("FC", "").strip()
            
            if action_team_name == "Los Angeles Galaxy":
                action_team_name = "Galaxy"

            if action_team_name in name_to_team:
                action_team = name_to_team[action_team_name]
            else:
                action_team = Team.objects.get(name__contains=action_team_name)
                name_to_team[action_team_name] = action_team

            time_on_pitch = float(event[3])
            if event[4] == "90 +":
                minute = -1
            elif event[4] == "45 +":
                minute = -2
            else:
                minute = int(event[4])
            
            home_score = int(event[7])
            away_score = int(event[8])

            #stats
            passes = int(event[9])

            minute_events.append(
                TimeEvent(
                    game=game,
                    team=action_team,
                    time_on_pitch=time_on_pitch,
                    minute=minute,
                    home_score=home_score,
                    away_score=away_score,
                    passes=passes
                    )
                )

        
        if dry_run:
            return
        if clear:
            deleted = TimeEvent.objects \
                .filter(game__in=list(games)) \
                .distinct().delete()
        all_created = TimeEvent.objects.bulk_create(minute_events)
        print("Created %d minute events" % len(all_created))
