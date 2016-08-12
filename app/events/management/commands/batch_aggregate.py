# batch_aggregate.py

import datetime
import csv
import os
import time

from django.core.management.base import BaseCommand, CommandError
from games.models import *
from events.models import *

from events.analysis.aggregate import *

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

		START = time.time()

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
			,5:["shots","sum","per_min"]
			,6:["shots_on_target","sum","per_min"]
			,7:["shot_accuracy","average","total"]
			,8:["shot_balance","average","total"]
			,9:["final_3rd_entries","sum","per_min"]
			,10:["pen_area_entries","sum","per_min"]
			,11:["pen_area_entry_accuracy","average","total"]
			,12:["tackles","sum","per_min"]
			,13:["tackled","sum","per_min"]
			,14:["interceptions","sum","per_min"]
			,15:["clearances","sum","per_min"]
			,16:["fouls","sum","per_min"]
			,17:["tackle_balance","average","total"]
			,18:["aggression_own","average","total"]
		}
		min_tws = [5.0, 7.5, 10.0]

		count = 0

		for moment in moments:
			for key, value in metric_info.iteritems():
				for moment_team in moment_teams:
					for min_tw in min_tws:
						results.append(aggregate(sw_id, moment, moment_team, value[0], \
						value[1], value[2], min_tw=min_tw, \
						outliers_flag=True))
						
						count += 1
						if count % 25 == 0:
							print "Analyzed %s Aggregations" % str(count)
							print "Elapsed Time = %s mins" % str((time.time()-START)/60)





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
			
			print "Total Elapsed Time = %s mins" % str((time.time()-START)/60)

		else:
			for item in results:
				print(item)