# aggregate_stats.py

# INPUT: 1) a team's sw_id
#		 2) the type of statistic events by which you want to define a moment
#			2.5) as well as which team each should apply to (Self, Opponent, or Both)
#		 3) the metrics of interest
#
# OUTPUT: aggregated stats for the games

import math
import datetime
import os
import csv
import numpy as np
from scipy.stats import ttest_1samp, wilcoxon, ttest_ind, mannwhitneyu

from django.core.management.base import BaseCommand, CommandError
from games.models import *
from events.models import *

from events.utils.time_and_statistic import *
from events.utils.team import *

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
			"--moment",
			dest="moment",
			default="",
			help="EventAction to determine what moments to pull",
			)
		parser.add_argument(
			"--moment_team",
			dest="moment_team",
			default="",
			help="TeamIdentifier = Self, Oppo, or Both",
			)
		parser.add_argument(
			"--metric",
			dest="metric",
			default="",
			help="Identify which metric to pull",
			)
		parser.add_argument(
			"--daterange",
            dest="daterange",
            default=False,
            help="Comma separated start and end dates. Example: 2015-06-13,2015-07-05",
            )
		parser.add_argument(
			"--tw_min_length",
            dest="tw_min_length",
            default=0.0,
            help="minimum length of time windows to compute lifts for",
            )
		parser.add_argument(
			"--tw_max_length",
            dest="tw_max_length",
            default=0.0,
            help="maximum length of time windows to compute lifts for",
            )
		# add optional print to csv flag
		parser.add_argument(
			"--print_to_csv",
			action="store_true",
            dest="print_to_csv",
            default=False,
            help="save file?",
            )
	
	def handle(self,*args,**options):
		"""
		1) Intake all variables
		"""
		# Check to make sure the necessary arguments are input
		if not options["sw_id"]:
			raise Exception("A sw_id is required for analysis")
		if not options["moment"]:
			raise Exception("Please explain how to define moments; format of 'EventAction,TeamIdentifier;' please; TeamIdentifier = Self,Oppo,Both")
		if not options["moment_team"]:
			raise Exception("Do the moments apply to Self, Oppo, or Both?")
		if not options["metric"]:
			raise Exception("We need a metric to aggregate")

		# save the inputs as variables
		arg_sw_id = options["sw_id"]
		arg_moment = options["moment"]
		arg_moment_team = options["moment_team"]
		if arg_moment_team not in ["Self", "Oppo", "Both"]:
			raise Exception("Unknown team identifier: " + str(arg_moment_team) + "\nShould be either Self, Oppo, Both")
		arg_metric = options["metric"]

		arg_daterange = options["daterange"]
		arg_start_date = None
		arg_end_date = None
		if arg_daterange:
			arg_daterange = arg_daterange.split(",")
			arg_start_date = datetime.datetime.strptime(arg_daterange[0], "%Y-%m-%d")
			arg_end_date = datetime.datetime.strptime(arg_daterange[1], "%Y-%m-%d")

			if arg_start_date > arg_end_date:
				raise Exception("Wrong date order")

		arg_tw_min_length = float(options["tw_min_length"])
		if not arg_tw_min_length:
			arg_tw_min_length = 0.0

		arg_tw_max_length = float(options["tw_max_length"])
		if not arg_tw_max_length:
			arg_tw_max_length = 100.0

		arg_print_to_csv = options["print_to_csv"]
		if arg_print_to_csv:
			arg_print_to_csv = True
		else:
			arg_print_to_csv = False
		
		"""
		2) Find all relevant games
		"""
		# pull the team name
		arg_team = Team.objects.get(sw_id=arg_sw_id)
		print("TEAM: " + str(arg_team) + "\n")

		# find all home/away games for the team, and order ASC by date
		games = get_team_games(arg_team, arg_start_date, arg_end_date)
		
		"""
		3) Pull time windows for analysis
		"""

		# pull time windows
		time_windows = {}
		meta_info = {}
		agg_moments = {}
		for game in games:
			time_windows[game] = create_windows_for_game(arg_team, game, arg_moment, arg_team)
			meta_info[game] = create_window_meta_information_for_game(arg_team, game, arg_moment, arg_team)
			agg_moments[game] = create_window_aggregate_action_counts_for_game(arg_team, game, arg_moment, arg_team)
			print(game)
			print(time_windows[game])
			print(meta_info[game])
			print(agg_moments[game])
			print("")


		raise Exception("MADE IT SO FAR")


		"""
		pull team games (replace lines 288 - 290)
		--> sw_games.py

		pull meta information of each game State
			- use same logic as time windows but create list of action + action team?
			- write another method using same logic that calculates aggregate score?
			- ANOTHER that calculates goal_differential?
		--> sw_time.py which should be called sw_event_stats.py

		write method that aggregates TimeStatistic over time window input
		--> sw_time_stats.py
			export = dict[game]-[list for tw's]

		method for taking aggregated time stats 
		"""






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

		
		# FOR EACH METRIC, by game (for which we have moments), aggregate the stats and STORE THEM in a structure of dictionaries and a list
		sw_aggregated_stats = {}
		for metric in arg_metrics:
			sw_aggregated_stats[metric] = {}

			print("\nMETRIC = " + str(metric))
			for date in sorted(game_state_definer):
				sw_aggregated_stats[metric][date] = []

				game = games_and_dates[date]
				
				game_name = str(game)

				agg_s = aggregate_statistic(game,db_team,metric,game_state_definer[date])

				count = 0 #counter for timewindows per game
				for item in agg_s:
					row = [metric, str(date), game_name, count, item[0], time_window_length(item[0]), item[1], item[2]]
					sw_aggregated_stats[metric][date].append(row)
					count += 1
		
		oldrow = []
		calculated_lifts = []
		for m in sw_aggregated_stats:
			for d in sorted(sw_aggregated_stats[m]):
				time_window_too_short = False
				for row in sw_aggregated_stats[m][d]:
					index = row[3]
					
					if row[3] == 0:
						oldrow = row
						continue

					if (row[3] - oldrow[3] != 1) and not time_window_too_short:
						raise Exception("Order of agg stats is wrong")

					if oldrow[7] == 0:
						oldrow = row
						continue

					if row[5] < arg_tw_minimum_length:
						time_window_too_short = True
						continue

					else:
						new_perf = row[7]/row[5]
						old_perf = oldrow[7]/oldrow[5]
						lift = (new_perf - old_perf)/old_perf

						calculated_lifts.append(lift)
						sw_aggregated_stats[m][d][index].append(lift)

						oldrow = row

		if arg_print_to_csv:
			os.chdir("/Users/Swoboda/Desktop/")
			output_filename = "program_results__" + str(db_team) + "_" +   ".csv"
			output = open(output_filename, "a")
			writer = csv.writer(output, lineterminator="\n")

			for m in sw_aggregated_stats:
				for d in sorted(sw_aggregated_stats[m]):
					for row in sw_aggregated_stats[m][d]:
						writer.writerow(row)

			output.close()

		np_calculated_lifts = np.array(calculated_lifts)

		# one sample t-test
		# null hypothesis: expected value = 7725
		print "\nmean = ", np.mean(np_calculated_lifts)
		t_statistic, p_value = ttest_1samp(np_calculated_lifts, 0)

		# p_value < 0.05 => alternative hypothesis:
		# data deviate significantly from the hypothesis that the mean
		# is 0 at the 5% level of significance
		print "one-sample t-test p-value = ", p_value
		print "statistical significance = ", 1-p_value

