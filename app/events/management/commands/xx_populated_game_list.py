# xx_populated_game_list.py

# This script takes an input of a team's sw_id and outputs the list of games in the DB for which we have populated StatisticEvents

from django.core.management.base import BaseCommand, CommandError
from games.models import *
from events.models import *

class Command(BaseCommand):
	help = 'populated game querying file'

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

		# save the input as a variable
		arg_sw_id = options["sw_id"]
		
		# pull the team name
		db_team = Team.objects.get(sw_id=arg_sw_id)
		print("TEAM:")
		print(db_team)
		print("")

		# find all home/away games for this team
		db_team_games = Game.objects.filter(home_team = db_team) | Game.objects.filter(away_team = db_team)

		# order list by date
		db_team_games = db_team_games.order_by('date')

		# for each game in the DB for this team, find the games that have populated Stats
		print("GAMES WITH POPULATED STATS:")
		no_games = True

		for game in db_team_games:
			if StatisticEvent.objects.filter(game = game):
				no_games = False
				print(game)
		if no_games:
			print("0 games populated in DB")
		print("")