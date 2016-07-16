import csv
import datetime

from django.core.management.base import BaseCommand, CommandError
from games.models import Game, Team
from events.models import StatisticEvent

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
        
        statistic_events = []

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
                
            game = Game.objects.filter(date=event[0]) \
                .filter(home_team=home_team) \
                .get(away_team=away_team)
            games.add(game)
            

            half = 1 if event[2] == "First Half" else 2
            time = float(event[3])
            event_action = "_".join(event[4].upper().split(" "))

            action_team_name = event[6].replace("FC", "").strip()
            action_team = Team.objects.get(name__contains=action_team_name)

            statistic_events.append(
                StatisticEvent(
                    game=game,
                    half=half,
                    seconds=time,
                    action=event_action,
                    action_team=action_team,
                    )
                )

        
        if dry_run:
            return
        if clear:
            deleted = StatisticEvent.objects \
                .filter(game__in=list(games)) \
                .distinct().delete()
        all_created = StatisticEvent.objects.bulk_create(statistic_events)
        print("Created %d statistic events" % len(all_created))
