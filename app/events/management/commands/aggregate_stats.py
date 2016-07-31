# aggregate_stats.py

# example command line: $ python manage.py aggregate_stats --sw_id=3 --moment=GOAL --metric=passes --moment_team=Self

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
from events.analysis.aggregators import *
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
			"--time_type",
			dest="time_type",
			default="",
			help="Time Type of Lift Calculation: Total, Per Min",
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
		if not options["time_type"]:
			raise Exception("We need a calculation time type: Total, Per Min")

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
		arg_time_type_code = get_time_type_code(options["time_type"])

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
		3) Pull time windows, meta information, and aggregate tally of the moments for analysis
		"""
		time_windows = {}
		meta_info = {}
		agg_tally_moments = {}
		for game in games:
			time_windows[game] = create_windows_for_game(arg_team, game, arg_moment, arg_moment_team)
			meta_info[game] = create_window_meta_information_for_game(arg_team, game, arg_moment, arg_moment_team)
			agg_tally_moments[game] = create_window_tally_action_counts_for_game(arg_team, game, arg_moment, arg_moment_team)

		"""
		4) Aggregate metric over time windows
		"""
		agg_stats = {}
		met = metric_command(arg_metric)
		for game in games:
			agg_stats[game] = do_collect_and_aggregate(arg_team, game \
					,windows=time_windows[game], meta_info=meta_info[game] \
					,agg_tally_moments=agg_tally_moments[game], metric=met)

		"""
		5) Calculate Lifts
		"""
		lifts, agg_stats = calculate_lift(games, agg_stats, arg_time_type_code, arg_tw_min_length)
		for game in games:
			print("\n" + str(game))
			for item in agg_stats[game]:
				print(agg_stats[game][item])

		print("\n \n \n \n")
		print(lifts)
		print("\n \n \n \n")

		"""
		6) Calculate Statistical Significance
		"""

		mean, t_stat, p_val = statistical_significance(lifts)

		mean = round(mean, 5)

		print "mean percentage lift = ", (mean*100)
		print "statistical significance = ", ((1-p_val))
	