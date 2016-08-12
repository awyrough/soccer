# simulate.py


import datetime

from django.core.management.base import BaseCommand, CommandError
from games.models import *
from events.models import *

from events.utils.time_and_statistic import *
from events.utils.team import *
from events.utils.graph import *
from events.analysis.aggregators import *
from events.analysis.generators import *
from events.analysis.statistics import *

def average_iterations(beginning_list, iteration_pool_list, iteration_count):
	outlier_ct = 0.0
	non_outlier_ct = 0.0
	mean = 0.0
	sig = 0.0
	p_val = 0.0

	for item in iteration_pool_list:
		outlier_ct += item[0]
		non_outlier_ct += item[1]
		mean += item[2]
		sig += item[3]
		p_val += item[4]

	row = beginning_list + ["AVERAGE"]+ [str(outlier_ct/iteration_count)] + [str(non_outlier_ct/iteration_count)] + \
		[str(mean/iteration_count)]	+ [str(sig/iteration_count)]+ [str(p_val/iteration_count)] + ["NO CODE"]

	return row
	
def simulate(sw_id, metric_fcn, aggregate_fcn, lift_type, start_minute=0, 
	end_minute=90, incr_minimum=5, incr_maximum=5, daterange=False,
	print_to_csv=False,outliers_flag=False,iteration=0):
	"""
	1) Intake all variables
	"""
	start_date = False
	end_date = False
	if daterange:
		daterange = daterange.split(",")
		start_date = datetime.datetime.strptime(daterange[0], "%Y-%m-%d")
		end_date = datetime.datetime.strptime(daterange[1], "%Y-%m-%d")

		if start_date > end_date:
			raise Exception("Wrong date order")

	"""
	2) Find all relevant games
	"""
	#pull the tema name
	team = Team.objects.get(sw_id=sw_id)
	#find all home/away games for the team
	games = get_team_games(team, start_date, end_date)

	"""
	3) Pull time windows, meta information, and aggregate tally of the moments for analysis
	"""
	time_windows = {}
	meta_info = {}
	agg_tally_moments = {}
	for game in games:
		time_windows[game] = create_random_artificial_windows_with_bounds(start=start_minute, \
			end=end_minute, inc_min=incr_minimum, inc_max=incr_maximum)
		meta_info[game] = []
		agg_tally_moments[game] = []
		# fill out the other dictionarys with dummy information (easy fix for not needing this)
		for item in time_windows[game]:
			meta_info[game].append("Simulation")
			agg_tally_moments[game].append(0)	

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
	lift_info, agg_stats = calculate_lift(games, agg_stats, MAP_LIFT_TYPE_FCN[lift_type])
	# for game in games:
	# 	print("\n" + str(game))
	# 	for item in agg_stats[game]:
	# 		print(agg_stats[game][item])

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

	"""
	8) Print / Return valuable information

	list columns: 
	sw_id, Team, metric_fcn, aggregate_fcn, lift_type, start_minute, end_minute, incr_minimum, incr_maximum, iteration, daterange, start_date, end_date, outliers_flag \
		,outlier_count, non_outlier_count, mean_value, statistical_significance, p_value, terminal_command
	"""
	f = []
	f.append(sw_id)
	f.append(str(team))
	f.append(metric_fcn)
	f.append(aggregate_fcn)
	f.append(lift_type)
	f.append(start_minute)
	f.append(end_minute)
	f.append(incr_minimum)
	f.append(incr_maximum)
	f.append(daterange)
	f.append(start_date)
	f.append(end_date)
	f.append(outliers_flag)
	f.append(iteration)
	f.append(len(outliers))
	f.append(len(non_outliers))
	f.append(mean*100)
	f.append(1-p_val)
	f.append(p_val)
	command = "python manage.py simulate_stats --sw_id=" + str(sw_id) + " --metric_fcn="  + str(metric_fcn) + " --aggregate_fcn=" \
		+ str(aggregate_fcn) + " --lift_type=" + str(lift_type) + " --start_minute=" + str(start_minute) \
		+ " --end_minute=" + str(end_minute) + " --incr_min=" + str(incr_minimum) \
		+ " --incr_max=" + str(incr_maximum) 
	if daterange:
		command = command + " --daterange=\"" + str(start_date) + "," + str(end_date) + "\""
	if outliers_flag:
		command = command + " --outliers"
	f.append(command)

	non_numerical = f[0:13]
	numerical = f[14:19]
	return f, non_numerical, numerical

	