import csv

from django.core.management.base import BaseCommand, CommandError
from games.models import Team

class Command(BaseCommand):
    help = 'Populate Team table'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        filename = "raw_data/teams.csv"
        f = open(filename, 'rU')
        reader = csv.reader(f)
        count = 0
        for team_data in reader:
            
            if count == 0:
                count = 1
                continue
            
            sw_id = int(team_data[0])
            team_name = team_data[1]
            conference = team_data[2]
            city = team_data[3]
            state = team_data[4]
            year_joined = int(team_data[5])

            
            team = Team.objects.create(
                name=team_name,
                sw_id=sw_id,
                city=city,
                state=state,
                year_joined=year_joined

            if year_joined != '': # if it isn't there, don't assign, let default
                team.year_joined = int(year_joined)
    
            team.save()
            
