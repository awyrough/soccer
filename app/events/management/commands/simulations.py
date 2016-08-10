# simulations.py

# INPUT: 1) a team's sw_id
#		 2) the type of statistic events by which you want to define a moment
#			2.5) as well as which team each should apply to (Self, Opponent, or Both)
#		 3) the metric of interest
#		 4) (optional) a date range
#		 5) (optional) print to csv 
#		 6) (optional) min time window
#		 7) (optional) max time window
#
# OUTPUT: aggregated stats for the games

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
			"--metric_fcn",
			dest="metric_fcn",
			default="passes",
			help="Identify which metric function to use on minute events (e.g. 'pass_accuracy')",
			)
		parser.add_argument(
			"--aggregate_fcn",
			dest="aggregate_fcn",
			default="sum",
			help="Identify which aggregate function to use on collection of window metrics",
			)
		parser.add_argument(
			"--lift_type",
			dest="lift_type",
			default="",
			help="Time Type of Lift Calculation: Total, Per Min",
			)
		parser.add_argument(
			"--increment",
			dest="increment",
			default="",
			help="How do we want to increment the simulations?",
			)		
		parser.add_argument(
			"--daterange",
            dest="daterange",
            default=False,
            help="Comma separated start and end dates. Example: 2015-06-13,2015-07-05",
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
		if not options["metric_fcn"]:
			raise Exception("We need a metric to aggregate")
		if not options["aggregate_fcn"]:
			raise Exception("We need a way to aggregate")
		if not options["lift_type"]:
			raise Exception("We need a lift time type: Total, Per Min")
		if not options["increment"]:
			raise Exception("We need a simulations increment")

		# save the inputs as variables
		arg_sw_id = options["sw_id"]
		arg_metric_fcn = options["metric_fcn"]
		arg_aggregate_fcn = options["aggregate_fcn"]
		arg_increment = float(options["increment"])

		arg_daterange = options["daterange"]
		arg_start_date = None
		arg_end_date = None
		if arg_daterange:
			arg_daterange = arg_daterange.split(",")
			arg_start_date = datetime.datetime.strptime(arg_daterange[0], "%Y-%m-%d")
			arg_end_date = datetime.datetime.strptime(arg_daterange[1], "%Y-%m-%d")

			if arg_start_date > arg_end_date:
				raise Exception("Wrong date order")
		arg_lift_type = options["lift_type"]

		# Hard coding these min and max values because they should be irrelvant
		arg_min_tw = 0.0
		arg_max_tw = 100.0

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
		3) Pull time windows, meta information, and aggregate tally of the moments for analysis
		"""
		time_windows = {}
		meta_info = {}
		agg_tally_moments = {}
		for game in games:
			time_windows[game] = create_artificial_windows_by_fn(lambda x: x + arg_increment, start = 0, end = 90, inc=arg_increment)
			meta_info[game] = []
			agg_tally_moments[game] = []
			for item in time_windows[game]:
				meta_info[game].append("Simulation")
				agg_tally_moments[game].append(0)	

		"""
		4) Aggregate metric over time windows
		"""
		agg_stats = {}
		for game in games:
			agg_stats[game] = do_collect_and_aggregate(arg_team, game \
					,windows=time_windows[game], meta_info=meta_info[game] \
					,agg_tally_moments=agg_tally_moments[game] \
					,metric_fcn=MAP_METRIC_FCN[arg_metric_fcn] \
					,aggregate_fcn=MAP_AGGREGATE_FCN[arg_aggregate_fcn])


		"""
		5) Calculate Lifts
		"""
		lift_info, agg_stats = calculate_lift(games, agg_stats, MAP_LIFT_TYPE_FCN[arg_lift_type], arg_min_tw)
		for game in games:
			print("\n" + str(game))
			for item in agg_stats[game]:
				print(agg_stats[game][item])

		print("\n \n \n \n")

		"""
		6) Calculate Outliers (Don't want to as of 8/3)
		"""
		# non_outliers, outliers = run_outlier_check(lift_info)

		# print "outlier count = ", len(outliers)
		# print "outliers:"
		# for item in outliers:
		# 	print '%s, on %s. z-score = %s' % (item[0],item[1],item[2])
		# print("\n")

		# print "non_outlier count", len(non_outliers)

		"""
		7) Calculate Statistical Significance
		"""

		# mean, t_stat, p_val = statistical_significance(non_outliers)

		# mean = round(mean, 5)

		# print "mean percentage lift = ", (mean*100)
		# print "statistical significance = ", ((1-p_val))


		"""
		8) Calculate Statistical Significance (No outliers)
		"""
		print "Time Window Minimum Limit of %s Mins " % (arg_min_tw)
		print("\n \n \n \n")

		mean, t_stat, p_val = statistical_significance(lift_info)

		mean = round(mean, 8)

		print "mean percentage lift = ", (mean*100)
		print "statistical significance = ", ((1-p_val))
		print("\n \n \n \n")

		"""
		9) Plot output as a scatter plot
		"""
		plot_scatterplot(lift_info)

	