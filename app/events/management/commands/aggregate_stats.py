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

import sw_time

def time_window_length(time_window_list):
	start = time_window_list[0]
	end = time_window_list[1]

	additional = 0.0

	if ((start != -2) and (start < 46)) and end >= 46: # if the TW passes the 1st half stoppage mark
			additional = 1.5	
	if start == -2:
		start = 45.0 #want to use 45 so that the calculation below accounts for min 46 as you step into the second half

	if end == -2:
		end = 45.0 + 1.5 #avg of 97 seconds of 1st half stoppage
	elif end == -1:
		end = 90.0 + 4.0 #avg of 238 seconds of 2nd half stoppage

	return end - start 
		

def aggregate_statistic(game, primary_team, metric, gs_definer):
		workable_metrics = ["time_on_pitch","minute","home_score","away_score","passes","passes_succ","passes_unsucc","passes_received","shots","shots_on_target","goals","offsides","dribbles","crosses","corners_taken","free_kicks_taken","fouls","fouled","yellow_cards","red_cards","tackles","tackled","blocks","interceptions","clearances","blocked_shots","shots_on_target_ex_blocked","shots_off_target_ex_blocked","shots_inside_box","shots_on_target_inside_box","shots_outside_box","shots_on_target_outside_box","goals_inside_box","goals_outside_box","entries_final_third","entries_pen_area","entries_pen_area_succ","entries_pen_area_unsucc","first_time_passes","first_time_passes_complete","first_time_passes_incomplete"]

		#use the below while all we have is passes in the per 1 min stat file
		if metric not in workable_metrics:
			raise Exception("Can't analyze " + metric + " right now; use: " + str(workable_metrics))

		#for the future, break up calculations based on type of metric
		if metric in workable_metrics:
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

		# for key in time_events:
		# 	print(getattr(time_events[key], metric))

		agg_list = []
		
		used_first_stoppage = False
		if not first_stoppage:	#account the possibility of no agg statistic for stoppage times
			used_first_stoppage = True
		
		used_second_stoppage = False
		if not second_stoppage:
			used_second_stoppage = True

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
			return [[[0.0,-1],"No Defined Moments in Game", " "]]
			#raise Exception("Check why there aren't any game states")

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
				#(so we don't want to incl 1st half stoppage)
				
				if tupl[1] == -1:
					for key in sorted(time_events.iterkeys()):
						if key >= 46:
							agg_value += getattr(time_events[key], metric)

					agg_value += getattr(second_stoppage, metric)
					used_second_stoppage = True

				elif tupl[1] <= 90:
					if key >= 46 and key <= tupl[1]:
						agg_value += getattr(time_events[key], metric)


			#When 2nd half stoppage time is end of tw
			elif tupl[1] == -1:
				if_count += 1
				for key in sorted(time_events.iterkeys()):
					if key > tupl[0]:
						agg_value += getattr(time_events[key], metric)

				if not used_second_stoppage:
					agg_value += getattr(second_stoppage, metric)
					used_second_stoppage = True

				if tupl[0] <= 45:
					if not used_first_stoppage:
						agg_value += getattr(first_stoppage, metric)
						used_first_stoppage = True

			#When 1st half stoppage time is end of tw
			elif tupl[1] == -2:
				if_count += 1
				for key in sorted(time_events.iterkeys()):
					if key > tupl[0] and key <= 45:
						agg_value += getattr(time_events[key], metric)

				if not used_first_stoppage:
					agg_value += getattr(first_stoppage, metric)
					used_first_stoppage = True

			#For every other case
			else:
				if_count += 1
				for key in sorted(time_events.iterkeys()):
					if key > tupl[0] and key <= tupl[1]:
						agg_value += getattr(time_events[key], metric)
				#check if the first half stoppage window falls within this "other case"
				if tupl[0] <= 45.0 and tupl[1] >= 46.0:
					if not used_first_stoppage:
						agg_value += getattr(first_stoppage, metric)
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
		parser.add_argument(
			"--daterange",
            dest="daterange",
            default=False,
            help="comma separated start and end dates",
            )
		parser.add_argument(
			"--tw_minimum_length",
            dest="tw_minimum_length",
            default=0.0,
            help="minimum length of time windows to compute lifts for",
            )
		parser.add_argument(
			"--tw_maximum_length",
            dest="tw_maximum_length",
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

		arg_daterange = options["daterange"]
		if arg_daterange:
			arg_daterange = arg_daterange.split(";")
			arg_daterange[0] = datetime.datetime.strptime(arg_daterange[0], "%m/%d/%Y")
			arg_daterange[1] = datetime.datetime.strptime(arg_daterange[1], "%m/%d/%Y")

			if arg_daterange[1] < arg_daterange[0]:
				raise Exception("Wrong date order")

		arg_tw_minimum_length = float(options["tw_minimum_length"])
		if not arg_tw_minimum_length:
			arg_tw_minimum_length = 0.0

		arg_print_to_csv = options["print_to_csv"]
		if arg_print_to_csv:
			arg_print_to_csv = True
		else:
			arg_print_to_csv = False

		# pull the team name
		db_team = Team.objects.get(sw_id=arg_sw_id)
		print("\nTEAM: " + str(db_team))

		# find all home/away games for the team, and order ASC by date
		if arg_daterange:
			db_team_games = Game.objects.filter(home_team = db_team, date__range=[arg_daterange[0],arg_daterange[1]]) | Game.objects.filter(away_team = db_team, date__range=[arg_daterange[0],arg_daterange[1]])
		else:
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

