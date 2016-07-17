# xx_team_name.py

# This script takes an input of a team's sw_id and outputs the team's name

from django.core.management.base import BaseCommand, CommandError
from games.models import Game, Team
from events.models import StatisticEvent

class Command(BaseCommand):
	help = 'team querying file'

	def add_arguments(self,parser):
		#add team sw_id argument
		parser.add_argument(
			"--sw_id",
			dest="sw_id",
			default="",
			help="sw_id to identify team on which to analyze",
			)

	def handle(self,*args,**options):
		if not options["sw_id"]:
			raise Exception("Team's sw_id required for analysis")

		arg_sw_id = options["sw_id"]
		
		print(Team.objects.get(sw_id=arg_sw_id))
