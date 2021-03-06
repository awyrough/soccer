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
from events.analysis.simulators import *

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
			"--incr_min",
			dest="incr_min",
			default="",
			help="minimum increment for simulations?",
			)	
		parser.add_argument(
			"--incr_max",
			dest="incr_max",
			default="",
			help="max increment for simulations?",
			)	
		parser.add_argument(
			"--start_minute",
            dest="start_minute",
            default=0,
            help="Simulation start minute",
            )	
		parser.add_argument(
			"--end_minute",
            dest="end_minute",
            default=90,
            help="Simulation end minute",
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
		# add optional print to csv flag
		parser.add_argument(
			"--outliers",
			action="store_true",
            dest="outliers",
            default=False,
            help="outliers?",
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
		if not options["incr_min"]:
			raise Exception("We need a simulations increment")
		if not options["incr_max"]:
			raise Exception("We need a simulations increment")

		# save the inputs as variables
		arg_sw_id = options["sw_id"]
		arg_metric_fcn = options["metric_fcn"]
		arg_aggregate_fcn = options["aggregate_fcn"]
		arg_incr_min = int(options["incr_min"])
		arg_incr_max = int(options["incr_max"])
		arg_start_minute = float(options["start_minute"])
		arg_end_minute = float(options["end_minute"])

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
		arg_outliers = options["outliers"]

		# Hard coding these min and max values because they should be irrelvant
		arg_min_tw = 0.0
		arg_max_tw = 100.0

		arg_print_to_csv = options["print_to_csv"]
		if arg_print_to_csv:
			arg_print_to_csv = True
		else:
			arg_print_to_csv = False
		

		iterations = 100

		"""
		2) Simulate
		"""
		sim_global_mean, sim_mean_list = null_hypothesis_simulator_iterations(arg_sw_id, arg_metric_fcn, arg_aggregate_fcn,\
		arg_lift_type, incr_minimum=arg_incr_min, incr_maximum=arg_incr_max,start_date=arg_start_date, end_date=arg_end_date,\
		outliers_flag=arg_outliers,iterations=iterations)

		for item in sim_mean_list:
			print item[0]
	