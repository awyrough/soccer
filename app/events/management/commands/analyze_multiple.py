# analyze_multiple.py

import datetime
import csv
import os

from django.core.management.base import BaseCommand, CommandError
from games.models import *
from events.models import *

from events.analysis.analyze import *

class Command(BaseCommand):
	help = 'analyzing multiple aggregate_stats scripts at once'

	def add_arguments(self,parser):
		# add optional print to csv flag
		parser.add_argument(
			"--print_to_csv",
			action="store_true",
            dest="print_to_csv",
            default=False,
            help="save file?",
            )
	def handle(self,*args,**options):
		arg_print_to_csv = options["print_to_csv"]

		results = []

		sw_id = 3
		moments = ["GOAL"]
		moment_teams = ["Both", "Self", "Oppo"]
		metric_info = {
			0:["passes","sum","per_min"]
			,1:["pass_accuracy","average","total"]
			,2:["pass_balance","average","total"]
			,3:["passes_first_time","sum","per_min"]
			,4:["passes_first_time_accuracy","average","total"]
			
		}
		min_tws = [0.0, 2.5, 5.0]


		for moment in moments:
			for key, value in metric_info.iteritems():
				for moment_team in moment_teams:
					for min_tw in min_tws:
						results.append(aggregate(sw_id, moment, moment_team, value[0], \
						value[1], value[2], min_tw=min_tw, \
						outliers_flag=True))

		if arg_print_to_csv:

			header=["sw_id", "Team", "moment", "moment_team", "metric_fcn", \
			"aggregate_fcn", "lift_type", "min_tw", "max_tw", "daterange", \
			"start_date", "end_date", "outliers_flag","outlier_count", \
			"non_outlier_count", "mean_value", "statistical_significance", \
			"p_value", "terminal_command"]
	
			os.chdir("/Users/Swoboda/Desktop/")
			output_filename = "analysis_results.csv"
			output = open(output_filename, "a")
			writer = csv.writer(output, lineterminator="\n")

			writer.writerow(header)

			for item in results:
				writer.writerow(item)

			output.close()

		else:
			for item in results:
				print(item)