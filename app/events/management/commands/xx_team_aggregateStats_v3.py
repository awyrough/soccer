# xx_team_aggregateStats_v3.py

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

		#for the future, break up calculations based on type of metric
		#if metric in ["passes"]:
		agg_list = agg_stat_discrete_sum(game, primary_team, metric, gs_definer)

		return agg_list

def agg_stat_discrete_sum(game, primary_team, metric, gs_definer):
		
		db_time_events = TimeEvent.objects.filter(game = game, team = primary_team)

		time_events = {}

		first_stoppage = None
		second_stoppage =  None

		for item in db_time_events:
			if item.minute in time_events:
				continue
			elif item.minute == -1:
				second_stoppage = item
			elif item.minute == -2:
				first_stoppage = item
			else:
				time_events[item.minute] = item

		agg_list = []
		"""NEED TO FIX THESE"""
		used_first_stoppage = False
		used_second_stoppage = False

		#remove stoppage times:
		start = 0.0
		meta_info = "Game > Start"

		# create game state windows based off moments
		game_states = []
		for moment in gs_definer:
			game_states.append((start,moment[0],meta_info))

			start = moment[0]
			meta_info = moment[1]

		if not game_states:
			raise Exception("Check why there aren't any game states")

		# add in one last game state window if it doesn't reach the end of the game
		last_item = game_states[-1] #last item in the game_states list
		if last_item[1] != -1: #-1 in this case represents the 90+'
			game_states.append((last_item[1],-1,meta_info))

		# iterate through all the game state windows and find the appropriate time_events to aggregate
		for tupl in game_states:
			tw = [tupl[0], tupl[1]]
			agg_value = 0
			if_count = 0

			#No time window should start in the 2nd half stoppage time?
			if tupl[0] == -1:
				continue	#I think this is fine? B/c anything starting in the 90+ minute will be aggregated in the tw ending in the 90+
				#if_count += 1
				#raise Exception("Check why the time window starts in the 90+ minute")

			#When 1st half stoppage time is start of tw 
			if tupl[0] == -2:
				if_count += 1
				#(so we don't want to incl stoppage)
				for key in sorted(time_events.iterkeys()):
					if key >= 46 and key <= tupl[1]:
						agg_value += time_events[key].passes

			#When 2nd half stoppage time is end of tw
			elif tupl[1] == -1:
				if_count += 1
				for key in sorted(time_events.iterkeys()):
					if key > tupl[0]:
						agg_value += time_events[key].passes

				agg_value += second_stoppage.passes
				used_second_stoppage = True

			#When 1st half stoppage time is end of tw
			elif tupl[1] == -2:
				if_count += 1
				for key in sorted(time_events.iterkeys()):
					if key > tupl[0] and key <= 45:
						agg_value += time_events[key].passes

				agg_value += first_stoppage.passes
				used_first_stoppage = True

			#For every other case
			else:
				if_count += 1
				for key in sorted(time_events.iterkeys()):
					if key > tupl[0] and key <= tupl[1]:
						agg_value += time_events[key].passes
				#check if the first half stoppage window falls within this "other case"
				if tupl[0] <= 45.0 and tupl[1] >= 46.0:
					agg_value += first_stoppage.passes
					used_first_stoppage = True

			#We shouldn't ever use multiple conditions
			if if_count != 1:
				print(if_count)
				print(tupl)
				raise Exception("If conditions didn't hold for this time window tuple")

			agg_list.append([tw, tupl[2], agg_value])

		#Check that we've aggregated stats from both stoppage time periods
		if not used_first_stoppage:
			raise Exception("Lost the first half stoppage")
		if not used_second_stoppage:
			raise Exception("Lost the second half stoppage")


		# trim game state aggregations where we're looking at the same minute (and the sum is 0)
		agg_list_trimmed = []

		for item in agg_list:
			tw = item[0]
			if tw[0] == tw[1] and item[2] == 0:
				continue

			agg_list_trimmed.append(item)

		return agg_list_trimmed



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

						#check for stoppage times, then assign minute
						if item.is_first_half() and (item.seconds / 60.0 > 45.0):
							minute = -2
						
						elif item.is_second_half() and (item.seconds / 60.0 > 45.0):
							minute = -1
						else:
							minute = math.ceil(item.get_minute_exact())
	
						meta_data = str(item.action_team) + ' > ' + str(item.action)
						moment_tuple = (minute, meta_data)

						"""Possible thought: to count duplicates w/in same minute?"""

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
					
