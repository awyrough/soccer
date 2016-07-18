# xx_team_aggregateStats.py

# INPUT: a team's sw_id and the type of statistic event by which you want to define a moment

# OUTPUT: aggregated stats for the games

import math

from django.core.management.base import BaseCommand, CommandError
from games.models import *
from events.models import *

def aggregate_statistic(game, team, statistic, moment_list):
		#use the below while all we have is passes in the per 1 min stat file
		if statistic != "passes":
			raise Exception("Can only analyze passes right now")

		db_time_events = TimeEvent.objects.filter(game = game, team = team)

		time_events = {}

		for item in db_time_events:
			if item.minute in time_events:
				continue
			else:
				time_events[item.minute] = item

		agg_list = []
		used_first_stoppage = False
		used_second_stoppage = False
		#remove stoppage times:
		start = 0.0
		for moment in moment_list:
			tw = [start, moment]
			agg_value = 0
			for key in time_events:
				if key > start and key <= moment:
					agg_value += time_events[key].passes

			if start < 45 and moment > 45:
				agg_value += time_events[-2].passes
				used_first_stoppage = True

			if start < 90 and moment > 90:
				agg_value += time_events[-1].passes
				used_second_stoppage = True

			agg_list.append([tw, agg_value])

			#reset the start of the next time window
			start = moment

		if not used_second_stoppage:
			agg_value = 0
			for key in time_events:
				if key > start:
					agg_value += time_events[key].passes

			agg_value += time_events[-1].passes
			used_second_stoppage = True

			tw = [start,"90.0+"]
			agg_list.append([tw,agg_value])

		if not used_first_stoppage:
			raise Exception("Lost the first half stoppage")
		if not used_second_stoppage:
			raise Exception("Lost the second half stoppage")

		return agg_list



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


		# produce a set of moments (for aggregation of other stats)
		moments = {}

		for game in db_team_games:
			g = StatisticEvent.objects.filter(game = game)

			if g:
				moments[game.date] = [] #add a key to the dict for the date of the game

				for item in g:
					if item.action in arg_stat_events:
						tw = math.ceil(item.get_minute_exact())
						moments[game.date].append(tw)



		for date in moments:
			for game in db_team_games:
				if game.date != date:
					continue
				print(game)
				print(str(date) + ": " + str(moments[date]))

				a = aggregate_statistic(game,db_team,"passes",moments[date])

				print(a)

				print("")
					
