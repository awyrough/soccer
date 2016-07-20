# xx_team_aggregateStats.py

# INPUT: 1) a team's sw_id
#		 2) the type of statistic events by which you want to define a moment
#			2.5) as well as which team each should apply to (Self, Opponent, or Both)
#		 3) the metrics of interest
#
# OUTPUT: aggregated stats for the games

import math

from django.core.management.base import BaseCommand, CommandError
from games.models import *
from events.models import *

def aggregate_statistic(game, primary_team, metric, gs_definer):
		#use the below while all we have is passes in the per 1 min stat file
		if metric != "passes":
			raise Exception("Can only analyze passes right now")

		agg_list = agg_stat_passing(game, primary_team, metric, gs_definer)

		return agg_list

def agg_stat_passing(game, primary_team, metric, gs_definer):
		
		db_time_events = TimeEvent.objects.filter(game = game, team = primary_team)

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
		meta_info = "Game > Start"
		for moment in gs_definer:
			tw = [start, moment[0]]
			agg_value = 0
			for key in time_events:
				if key > start and key <= moment[0]:
					agg_value += time_events[key].passes

			if start < 45 and moment[0] > 45:
				agg_value += time_events[-2].passes
				used_first_stoppage = True

			if start < 90 and moment[0] > 90:
				agg_value += time_events[-1].passes
				used_second_stoppage = True

			agg_list.append([tw, meta_info, agg_value])

			#reset the start of the next time window
			start = moment[0]
			meta_info = moment[1]

		if not used_second_stoppage:
			agg_value = 0
			for key in time_events:
				if key > start:
					agg_value += time_events[key].passes

			agg_value += time_events[-1].passes
			used_second_stoppage = True

			if not used_first_stoppage:
				if start > 45:
					raise Exception("AJ's logic is wrong for aggregating")
				agg_value += time_events[-2].passes
				used_first_stoppage = True
				
			tw = [start,"90.0+"]
			agg_list.append([tw, meta_info, agg_value])

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
			"--moment_definer",
			dest="moment_definer",
			default="",
			help="EventAction,TeamIdentifier pairings to determine what moments to pull; TeamIdentifier = Self,Oppo,Both",
			)
		parser.add_argument(
			"--metrics",
			dest="metrics",
			default="",
			help="List of metrics to pull",
			)
	
	def handle(self,*args,**options):
		# Check to make sure the appropriate arguments are input
		if not options["sw_id"]:
			raise Exception("A sw_id is required for analysis")

		if not options["moment_definer"]:
			raise Exception("Please explain how to define moments; format of 'EventAction,TeamIdentifier;' please; TeamIdentifier = Self,Oppo,Both")

		if not options["metrics"]:
			raise Exception("We need metrics to aggregate; comma separated format please")

		# save the inputs as variables
		arg_sw_id = options["sw_id"]
		
		arg_moment_definer = {}
		x = options["moment_definer"].split(";")
		for item in x:
			i = item.split(",")
			if len(i) != 2:
				raise Exception("The moment definer has a weird combination of inputs")
			if i[1] not in ["Self", "Oppo", "Both"]:
				raise Exception("Unknown team identifier: " + str(i[1]) + "\nShould be either Self, Oppo, Both")
			arg_moment_definer[i[0]] = i[1]

		arg_metrics = options["metrics"].split(";")

		# pull the team name
		db_team = Team.objects.get(sw_id=arg_sw_id)
		print("\nTEAM: " + str(db_team))

		# find all home/away games for the team, and order ASC by date
		db_team_games = Game.objects.filter(home_team = db_team) | Game.objects.filter(away_team = db_team)
		db_team_games = db_team_games.order_by('date')

		# find if there are games with populated stats
		no_games = True

		# game state definer = dictionary with key = dates (of games), value = moment list [(min,action team + action),...]
		game_state_definer = {}

		# create a dictionary of dates and game objects (for later use)
		games_and_dates = {}

		# pull all relevant moments to populate the game state definer
		for game in db_team_games:
			g = StatisticEvent.objects.filter(game = game)

			if g:
				no_games = False
				game_state_definer[game.date] = [] #add a key to the dict for the date of the game
				games_and_dates[game.date] = game

				for item in g: #for every StatisticEvent in a game
					if item.action in arg_moment_definer: #if the StatisticEvent's action is desired
						#if the need for this action is JUST the primary team
						if arg_moment_definer[item.action] == "Self": 
							if item.action_team != db_team: #if the StatEvent's action team isn't the desired team
								continue #skip this item and continue through the game
						
						#if the need for this action is JUST the opponent team
						if arg_moment_definer[item.action] == "Oppo":
							if item.action_team == db_team:
								continue

						#otherwise the need is for Both
						minute = math.ceil(item.get_minute_exact())
						meta_data = str(item.action_team) + ' > ' + str(item.action)
						moment_tuple = (minute, meta_data)
						game_state_definer[game.date].append(moment_tuple)
		if no_games:
			raise Exception(str(db_team) + " has no statistics populated in the DB")

		# FOR EACH METRIC, by game (for which we have moments), aggregate the stats
		for metric in arg_metrics:
			print("\nMETRIC = " + str(metric))
			for date in game_state_definer:
				game = games_and_dates[date]
				
				print("GAME = " + str(game))

				agg_s = aggregate_statistic(game,db_team,metric,game_state_definer[date])

				for item in agg_s:
					print("\t" + str(item[0]) \
						+ "\t" + str(item[1]) + "\t" + str(item[2]))
					
