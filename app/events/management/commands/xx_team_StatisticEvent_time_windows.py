# xx_team_StatisticEvent_time_windows.py

# This script takes an input of a team's sw_id 
# and outputs all of the time windows of a team's statistic events 
# for the type you ask for

import math

from django.core.management.base import BaseCommand, CommandError
from games.models import *
from events.models import *

class Command(BaseCommand):
	help = 'querying file to pull team StatisticEvents'

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

		# find if there are games with populated stats
		no_games = True
		for game in db_team_games:
			g = StatisticEvent.objects.filter(game = game)
			if g:
				no_games = False

		if no_games:
			raise Exception(str(db_team) + " has no statistics populated in the DB")


		# produce a set of time_windows (for aggregation of other stats)
		time_windows = {}

		for game in db_team_games:
			g = StatisticEvent.objects.filter(game = game)

			if g:
				time_windows[game.date] = [] #add a key to the dict for the date of the game

				for item in g:
					if item.action in arg_stat_events:
						tw = math.ceil(item.get_minute_exact())
						time_windows[game.date].append(tw)



		for date in time_windows:
			print(date)
			print(time_windows[date])
			print("")
					
