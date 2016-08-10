# analyze.py

# INPUT: 
# OUTPUT:

import datetime

from django.core.management.base import BaseCommand, CommandError
from games.models import *
from events.models import *

from events.utils.time_and_statistic import *
from events.utils.team import *
from events.utils.graph import *
from events.analysis.aggregators import *
from events.analysis.statistics import *

def aggregate(sw_id, moment, moment_team, metric_fcn,
	aggregate_fcn, lift_type, daterange=False, min_tw=0.0,
	max_tw=100.0, print_to_csv=False, outliers_flag=False):

	if moment_team not in ["Self", "Oppo", "Both"]:
		raise Exception("Unknown team identifier: " + str(moment_team) + "\nShould be either Self, Oppo, Both")

	start_date = False
	end_date = False
	if daterange:
		daterange = daterange.split(",")
		start_date = datetime.datetime.strptime(daterange[0], "%Y-%m-%d")
		end_date = datetime.datetime.strptime(daterange[1], "%Y-%m-%d")

		if start_date > end_date:
			raise Exception("Wrong date order")

	"""
	2) Find Relevant Games
	"""		
	# pull the team name
	team = Team.objects.get(sw_id=sw_id)

	# find all home/away games for the team, and order ASC by date
	games = get_team_games(team, start_date, end_date)

	"""
	3) Pull time windows, meta information, and aggregate tally of the moments for analysis
	"""
	time_windows = {}
	meta_info = {}
	agg_tally_moments = {}
	for game in games:
		time_windows[game] = create_windows_for_game(team, game, moment, moment_team)
		meta_info[game] = create_window_meta_information_for_game(team, game, moment, moment_team)
		agg_tally_moments[game] = create_window_tally_action_counts_for_game(team, game, moment, moment_team)

	"""
	4) Aggregate metric over time windows
	"""
	agg_stats = {}
	for game in games:
		agg_stats[game] = do_collect_and_aggregate(team, game \
				,windows=time_windows[game], meta_info=meta_info[game] \
				,agg_tally_moments=agg_tally_moments[game] \
				,metric_fcn=MAP_METRIC_FCN[metric_fcn] \
				,aggregate_fcn=MAP_AGGREGATE_FCN[aggregate_fcn])

	"""
	5) Calculate Lifts
	"""
	lift_info, agg_stats = calculate_lift(games, agg_stats, MAP_LIFT_TYPE_FCN[lift_type], min_tw)
	
	# if arg_details:
	# 	for game in games:
	# 		print("\n" + str(game))
	# 		for item in agg_stats[game]:
	# 			print(agg_stats[game][item])

	# 	print("\n")

	"""
	6) Choose if we're doing outliers 
	"""
	if outliers_flag:
		non_outliers, outliers = run_outlier_check(lift_info)

		# print "outlier count = ", len(outliers)
		# print "non_outlier count = ", len(non_outliers)
		# print "outliers:"
		# for item in outliers:
		# 	print '    %s, on %s. z-score = %s' % (item[0],item[1],item[2])
		# print("\n")

		lift_info = non_outliers
	

	"""
	7) Calculate Statistical Significance
	"""
	# if arg_details:
	# 	print "Time Window Minimum Limit of %s Mins " % (arg_min_tw)
	# 	print("\n")

	mean, t_stat, p_val = statistical_significance(lift_info)

	mean = round(mean, 8)

	# print "Mean Percentage Change = ", (mean*100)
	# print "Statistical Significance = ", ((1-p_val))
	# print("")
	# print mean*100
	# print 1-p_val
	# if arg_outliers:
	# 	print len(outliers)
	# else:
	# 	print "N/A"
	# print("\n")

	"""
	8) Print / Return valuable information

	list columns: 
	sw_id, Team, moment, moment_team, metric_fcn, aggregate_fcn, lift_type, min_tw, max_tw, daterange, start_date, end_date, outliers_flag \
		,outlier_count, non_outlier_count, mean_value, statistical_significance, p_value, terminal_command
	"""
	f = []
	f.append(sw_id)
	f.append(str(team))
	f.append(moment)
	f.append(moment_team)
	f.append(metric_fcn)
	f.append(aggregate_fcn)
	f.append(lift_type)
	f.append(min_tw)
	f.append(max_tw)
	f.append(daterange)
	f.append(start_date)
	f.append(end_date)
	f.append(outliers_flag)
	f.append(len(outliers))
	f.append(len(non_outliers))
	f.append(mean*100)
	f.append(1-p_val)
	f.append(p_val)
	command = "python manage.py aggregate_stats --sw_id=" + str(sw_id) + " --moment=" + str(moment) + " --moment_team=" + str(moment_team) \
		+ " --metric_fcn="  + str(metric_fcn) + " --aggregate_fcn=" + str(aggregate_fcn) + " --lift_type=" + str(lift_type) + " --min_tw=" + str(min_tw) \
		+ " --max_tw=" + str(max_tw) + " --details"
	if daterange:
		command = command + " --daterange=\"" + str(start_date) + "," + str(end_date) + "\""
	if outliers_flag:
		command = command + " --outliers"
	f.append(command)

	return f

