# xx_team_StatisticEvents.py

# This script takes an input of a team's sw_id 
# and outputs all of the team's statistic events for the type you ask for
from django.core.management.base import BaseCommand, CommandError
from games.models import *
from events.models import *

class Command(BaseCommand):
	help = 'SJE querying file'

	def add_arguments(self,parser):
		#add team sw_id argument
		parser.add_argument(
			"--sw_id",
			dest="sw_id",
			default="",
			help="sw_id to identify team on which to analyze",
			)
		parser.add_argument(
			"--stat_events",
			dest="stat_events",
			default="",
			help="statistic events to determine what to pull",
			)

	def handle(self,*args,**options):
		if not options["sw_id"]:
			raise Exception("A sw_id is required for analysis")

		if not options["stat_events"]:
			raise Exception("StatisticEvents required for analysis")

		# save the inputs as variables
		arg_sw_id = options["sw_id"]
		arg_stat_events = options["stat_events"].split(",")

		# pull the team name
		db_team = Team.objects.get(sw_id=arg_sw_id)
		print("TEAM: " + str(db_team))
		print("")

		# find all home/away games for this team
		db_team_games = Game.objects.filter(home_team = db_team) | Game.objects.filter(away_team = db_team)

		# order list by date
		db_team_games = db_team_games.order_by('date')

		# for each game in the DB for this team, find the games that have populated Stats
		no_games = True
		for game in db_team_games:
			if StatisticEvent.objects.filter(game = game):
				no_games = False
				g = StatisticEvent.objects.filter(game = game)

				for item in g:
					if item.action in arg_stat_events:
						print(item)

		if no_games:
			raise Exception(str(db_team) + " has no statistics populated in the DB")
