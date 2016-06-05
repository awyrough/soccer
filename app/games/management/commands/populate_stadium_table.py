import csv

from django.core.management.base import BaseCommand, CommandError
from games.models import Stadium

class Command(BaseCommand):
    help = 'Populate stadium table'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        filename = "raw_data/venues.csv"
        f = open(filename, 'rU')
        reader = csv.reader(f)
        count = 0
        for stadium_data in reader:
            
            if count == 0:
                count = 1
                continue
            
            sw_id = stadium_data[0]
            name = stadium_data[1]
            location = stadium_data[3].split(",")
            city = location[0].strip()
            state = location[1].strip()
            year_opened = stadium_data[4]
            is_primary = True if stadium_data[5] == "Y" else False
            capacity = int(stadium_data[6])
            surface_id = stadium_data[8]
            is_soccer_specific = True if stadium_data[9] == "Y" else False
            
            
            stadium = Stadium.objects.create(
                name=name,
                sw_id=sw_id,
                city=city,
                state=state,
                is_primary=is_primary,
                capacity=int(capacity),
                soccer_specific=is_soccer_specific)
            if surface_id != '': # if it isn't there, don't assign, let default
                stadium.surface = int(surface_id)
            if year_opened:
                stadium.year_opened = year_opened
            stadium.save()
            
