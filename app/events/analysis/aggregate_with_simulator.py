# aggregate_with_simulator.py

# INPUT: 
# OUTPUT:

from datetime import datetime

from django.core.management.base import BaseCommand, CommandError
from games.models import *
from events.models import *

from events.utils.time_and_statistic import *
from events.utils.team import *
from events.utils.graph import *
from events.analysis.aggregators import *
from events.analysis.statistics import *
from events.analysis.simulators import *

def aggregate_vs_simulate(sw_id, moment, moment_team, metric_fcn,
	aggregate_fcn, lift_type, iterations, daterange=False, min_tw=0.0,
	max_tw=100.0, print_to_csv=False, outliers_flag=False, max_simulated_incr=90):

	if moment_team not in ["Self", "Oppo", "Both"]:
		raise Exception("Unknown team identifier: " + str(moment_team) + "\nShould be either Self, Oppo, Both")
	if max_tw != 100.0:
		raise Exception("ALERT! Right now nothing is done with max_tw. Why are you changing it?")

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
	7) Simulate other random time windows 
	"""
	simulated_mean = null_hypothesis_simulator_iterations(sw_id, metric_fcn, aggregate_fcn,\
		lift_type, incr_minimum=int(min_tw), incr_maximum=max_simulated_incr,start_date=start_date, end_date=end_date,\
		outliers_flag=outliers_flag,iterations=iterations)

	"""
	7) Calculate Statistical Significance
	"""
	# if arg_details:
	# 	print "Time Window Minimum Limit of %s Mins " % (arg_min_tw)
	# 	print("\n")

	mean, t_stat, p_val = statistical_significance(lift_info, null_hypo=simulated_mean)

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
	f.append(simulated_mean*100)
	f.append(iterations)
	f.append(outliers_flag)
	f.append(len(outliers))
	f.append(len(non_outliers))
	f.append(mean*100)
	f.append(1-p_val)
	f.append(p_val)
	command = "python manage.py single_aggregate --sw_id=" + str(sw_id) + " --moment=" + str(moment) + " --moment_team=" + str(moment_team) \
		+ " --metric_fcn="  + str(metric_fcn) + " --aggregate_fcn=" + str(aggregate_fcn) + " --lift_type=" + str(lift_type) + " --min_tw=" + str(min_tw) \
		+ " --max_tw=" + str(max_tw) + " --null_hypo=" + str(simulated_mean) + " --details"
	if daterange:
		command = command + " --daterange=\"" + str(start_date) + "," + str(end_date) + "\""
	if outliers_flag:
		command = command + " --outliers"
	f.append(command)

	return f

def aggregate_vs_simulate_two_sample(sw_id, moment, moment_team, metric_fcn,
	aggregate_fcn, lift_type, iterations, daterange=False, min_tw=0.0,
	max_tw=100.0, print_to_csv=False, outliers_flag=False, max_simulated_incr=90):

	if moment_team not in ["Self", "Oppo", "Both"]:
		raise Exception("Unknown team identifier: " + str(moment_team) + "\nShould be either Self, Oppo, Both")
	if max_tw != 100.0:
		raise Exception("ALERT! Right now nothing is done with max_tw. Why are you changing it?")

	start_date = False
	end_date = False
	if daterange:
		daterange = daterange.split(",")

		start_date = datetime.strptime(daterange[0], "%Y-%m-%d")
		end_date = datetime.strptime(daterange[1], "%Y-%m-%d")

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

	"""
	6) Choose if we're doing outliers; if so, replace the current lift_info with the non_outliers
	"""
	if outliers_flag:
		non_outliers, outliers = run_outlier_check(lift_info)
		lift_info = non_outliers
		
	"""
	7) Simulate other random time windows 
	"""
	sim_global_mean, sim_mean_list = null_hypothesis_simulator_iterations(sw_id, metric_fcn, aggregate_fcn,\
		lift_type, incr_minimum=int(min_tw), incr_maximum=max_simulated_incr,start_date=start_date, end_date=end_date,\
		outliers_flag=outliers_flag,iterations=iterations)

	"""
	7) Statistical Significance --> One Sample T-Test vs. Sim_Global_Mean  
	"""
	onesample__mean, onesample__t_stat, onesample__p_val = onesample__statistical_significance(lift_info, null_hypo=sim_global_mean)

	# #ONLY DO THIS IF WE'RE RUNNING A BATCH SCRIPT WITH ONLY ONE INPUT...
	# print "ONE SAMPLE TEST"
	# print "Mean = ", onesample__mean
	# print "Sim Mean = ", sim_global_mean
	# print "T_stat = ", onesample__t_stat
	# print "p_val = ", onesample__p_val
	# print "\n \n"

	"""
	8) Statistical Significance --> Two Sample Welch's T-Test vs. Sim_Mean_List  
	"""
	twosample__actual_mean, twosample__sim_mean, twosample__t_stat, twosample__p_val = twosample__statistical_significance(lift_info, sim_mean_list)

	# #ONLY DO THIS IF WE'RE RUNNING A BATCH SCRIPT WITH ONLY ONE INPUT...
	# print "TWO SAMPLE TEST"
	# print "Actual Mean = ", twosample__actual_mean
	# print "Simulated Mean = ", twosample__sim_mean
	# print "T_stat = ", twosample__t_stat
	# print "p_val = ", twosample__p_val
	# print "\n \n"
	# print extract_only_indexed_values(lift_info, 0)
	# print extract_only_indexed_values(sim_mean_list, 0)

	# #ONLY DO THIS IF WE'RE RUNNING A BATCH SCRIPT WITH ONLY ONE INPUT...
	# plot_two_samples(lift_info, sim_mean_list, twosample__actual_mean, \
	# 	twosample__sim_mean, onesample__p_val, twosample__p_val)

	"""
	9) Print / Return valuable information

	list columns: 
	"""
	header = [
		"sw_id"
		,"Team"
		,"moment"
		,"moment_team"
		,"metric_fcn"
		,"aggregate_fcn"
		,"lift_type"
		,"min_tw"
		,"max_tw"
		,"max_simulated_incr"
		,"actual_mean"
		,"simulated_mean"
		,"relative_performance"
		,"two_sample_sig"
		,"two_sample_pval"
		,"one_sample_sig"
		,"one_sample_pval"
		,"outliers_flag"
		,"# of actual outliers"
		,"# of actual non-outliers"
		,"daterange"
		,"start_date"
		,"end_date"
		,"simulation_iterations"
		,"actual_raw_values"
		,"simulated_raw_values"
		]
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
	f.append(max_simulated_incr)
	f.append(twosample__actual_mean*100)
	f.append(twosample__sim_mean*100)
	f.append(relative_performance(twosample__actual_mean, twosample__sim_mean))
	f.append(1-twosample__p_val)
	f.append(twosample__p_val)
	f.append(1-onesample__p_val)
	f.append(onesample__p_val)
	f.append(outliers_flag)
	f.append(len(outliers))
	f.append(len(non_outliers))
	f.append(daterange)
	f.append(start_date)
	f.append(end_date)
	f.append(iterations)
	f.append(str(extract_only_indexed_values(lift_info, 0)))
	f.append(str(extract_only_indexed_values(sim_mean_list, 0)))

	return f, header



