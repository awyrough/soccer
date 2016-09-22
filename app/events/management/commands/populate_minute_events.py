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
            
            print '%s vs %s on %s' % (home_team_name, away_team_name, date)
                
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
                minute = -2
            elif event[4] == "45 +":
                minute = -1
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
                    passes=passes,
                    passes_succ=int(event[10]) if event[10] != "NULL" else 0,
                    passes_unsucc=int(event[11]) if event[11] != "NULL" else 0,
                    passes_received=int(event[14]) if event[10] != "NULL" else 0,
                    shots=int(event[15]) if event[15] != "NULL" else 0,
                    shots_on_target=int(event[16]) if event[16] != "NULL" else 0,
                    goals=int(event[17]) if event[17] != "NULL" else 0,
                    offsides=int(event[18]) if event[18] != "NULL" else 0,
                    dribbles=int(event[19]) if event[19] != "NULL" else 0,
                    crosses=int(event[20]) if event[20] != "NULL" else 0,
                    corners_taken=int(event[21]) if event[21] != "NULL" else 0,
                    free_kicks_taken=int(event[22]) if event[22] != "NULL" else 0,
                    fouls=int(event[23]) if event[23] != "NULL" else 0,
                    fouled=int(event[24]) if event[24] != "NULL" else 0,
                    yellow_cards=int(event[25]) if event[25] != "NULL" else 0,
                    red_cards=int(event[26]) if event[26] != "NULL" else 0,
                    tackles=int(event[27]) if event[27] != "NULL" else 0,
                    tackled=int(event[28]) if event[28] != "NULL" else 0,
                    blocks=int(event[29]) if event[29] != "NULL" else 0,
                    interceptions=int(event[30]) if event[30] != "NULL" else 0,
                    clearances=int(event[31]) if event[31] != "NULL" else 0,
                    blocked_shots=int(event[32]) if event[32] != "NULL" else 0,
                    shots_on_target_ex_blocked=int(event[33]) if event[33] != "NULL" else 0,
                    shots_off_target_ex_blocked=int(event[34]) if event[34] != "NULL" else 0,
                    shots_inside_box=int(event[35]) if event[35] != "NULL" else 0,
                    shots_on_target_inside_box=int(event[36]) if event[36] != "NULL" else 0,
                    shots_outside_box=int(event[37]) if event[37] != "NULL" else 0,
                    shots_on_target_outside_box=int(event[38]) if event[38] != "NULL" else 0,
                    goals_inside_box=int(event[40]) if event[40] != "NULL" else 0,
                    goals_outside_box=int(event[41]) if event[41] != "NULL" else 0,
                    entries_final_third=int(event[58]) if event[58] != "NULL" else 0,
                    entries_pen_area=int(event[59]) if event[59] != "NULL" else 0,
                    entries_pen_area_succ=int(event[60]) if event[60] != "NULL" else 0,
                    entries_pen_area_unsucc=int(event[61]) if event[61] != "NULL" else 0,
                    first_time_passes=int(event[78]) if event[78] != "NULL" else 0,
                    first_time_passes_complete=int(event[79]) if event[79] != "NULL" else 0,
                    first_time_passes_incomplete=int(event[80]) if event[80] != "NULL" else 0,
                    passes_attempted_ownhalf=int(event[83]) if event[83] != "NULL" else 0,
                    passes_successful_ownhalf=int(event[84]) if event[84] != "NULL" else 0,
                    passes_attempted_opphalf=int(event[85]) if event[85] != "NULL" else 0,
                    passes_successful_opphalf=int(event[86]) if event[86] != "NULL" else 0,
                    )
                )

        
        if dry_run:
            return
        if clear:
            deleted = TimeEvent.objects \
                .filter(game__in=list(games)) \
                .distinct().delete()
        all_created = TimeEvent.objects.bulk_create(minute_events)
        print("Created and saved %d minute events" % len(all_created))
