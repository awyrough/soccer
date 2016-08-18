# batch_aggregate_with_simulator.py

# sample code: 
#	python manage.py batch_aggregate_with_simulator --null_hypo_iterations=5 --max_simulated_incr=10 --print_to_csv



import datetime
import csv
import os
import time

from django.core.management.base import BaseCommand, CommandError
from games.models import *
from events.models import *

from events.analysis.aggregate_with_simulator import *

class Command(BaseCommand):
	help = 'analyzing multiple aggregate_stats scripts at once'

	def add_arguments(self,parser):
		# add optional print to csv flag
		parser.add_argument(
			"--sw_id",
			dest="sw_id",
			default="",
			help="sw_id to identify team on which to analyze",
			)
		parser.add_argument(
			"--print_to_csv",
			action="store_true",
            dest="print_to_csv",
            default=False,
            help="save file?",
            )
		parser.add_argument(
			"--null_hypo_iterations",
            dest="null_hypo_iterations",
            default=15,
            help="number of null hypo iterations?",
            )
		parser.add_argument(
			"--max_simulated_incr",
            dest="max_simulated_incr",
            default=90,
            help="max length of simulated increment?",
            )
	def handle(self,*args,**options):
		if not options["sw_id"]:
			raise Exception("A sw_id is required for analysis")

		sw_id = int(options["sw_id"])
		START = time.time()

		arg_print_to_csv = options["print_to_csv"]
		max_simulated_incr = int(options["max_simulated_incr"])
		null_hypo_iterations = int(options["null_hypo_iterations"])

		results = []

		moments = ["GOAL", "SUBSTITUTION", "YELLOW_CARD"]
		# moments = ["SUBSTITUTION", "YELLOW_CARD"]
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
		min_tws = [5.0, 7.5, 10.0, 15.0]

		count = 0

		for moment in moments:
			if moment == "SUBSTITUTION":
				max_simulated_incr = 30
			for key, value in metric_info.iteritems():
				for moment_team in moment_teams:
					for min_tw in min_tws:
						results.append(aggregate_vs_simulate(sw_id, moment, moment_team, value[0], \
						value[1], value[2], iterations=null_hypo_iterations, min_tw=min_tw, \
						outliers_flag=True, max_simulated_incr=max_simulated_incr))
						
						count += 1
						if count % 25 == 0:
							print "Analyzed %s Aggregations" % str(count)
							print "Elapsed Time = %s mins; \t %s" % (str((time.time()-START)/60), time.strftime('%l:%M%p %Z'))





		if arg_print_to_csv:

			header=["sw_id", "Team", "moment", "moment_team", "metric_fcn", \
			"aggregate_fcn", "lift_type", "min_tw", "max_tw", "daterange", \
			"start_date", "end_date", "simulated_mean","simulation_iterations","outliers_flag","outlier_count", \
			"non_outlier_count", "mean_value", "statistical_significance", \
			"p_value", "terminal_command"]
	
			os.chdir("/Users/Swoboda/Desktop/")
			output_filename = str(sw_id) + "__"+ str(time.strftime('%Y_%m_%d')) +"_analysis_results.csv"
			output = open(output_filename, "a")
			writer = csv.writer(output, lineterminator="\n")

			writer.writerow(header)

			for item in results:
				writer.writerow(item)

			output.close()
			
		else:
			for item in results:
				print(item)

		print "Total Elapsed Time = %s mins" % str((time.time()-START)/60)
