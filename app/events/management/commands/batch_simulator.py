# batch_simulate.py

import datetime
import csv
import os
import time

from django.core.management.base import BaseCommand, CommandError
from games.models import *
from events.models import *

from events.analysis.simulators import *

class Command(BaseCommand):
	help = 'analyzing multiple aggregate_stats scripts at once'

	def add_arguments(self,parser):
		parser.add_argument(
			"--iterations",
            dest="iterations",
            default="",
            help="How many iterations for each simulation?",
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
		if not options["iterations"]:
			raise Exception("We need a simulations iterations number")
		arg_iterations = int(options["iterations"])
		arg_print_to_csv = options["print_to_csv"]

		START = time.time()

		results = []

		sw_id = 3
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
			# ,12:["tackles","sum","per_min"]
			# ,13:["tackled","sum","per_min"]
			# ,14:["interceptions","sum","per_min"]
			# ,15:["clearances","sum","per_min"]
			# ,16:["fouls","sum","per_min"]
			# ,17:["tackle_balance","average","total"]
			# ,18:["aggression_own","average","total"]
		}

		increments = [(5,5),(10,10),(15,15),(30,30),(45,45),\
						(5,10),(5,15),(5,30),(5,45),(5,60),\
						(10,15),(10,30),(10,45),(10,60),\
						(15,30),(15,45),(15,60),\
						(15,90),(30,60)]
		count = 0

		for key, value in metric_info.iteritems():
			for increment_pair in increments:
				if increment_pair[0] == increment_pair[1]:
					arg_iters = 1
				else:
					arg_iters = arg_iterations
				#pool results of each iteration to then take an average to add to the output
				iter_pool = []
				
				for x in range(1, arg_iters+1):
					main, non_numerical, numerical = simulate(sw_id, value[0], \
					value[1], value[2], incr_minimum=increment_pair[0], \
					incr_maximum=increment_pair[1], outliers_flag=True, iteration=x)

					count += 1
					if count % 25 == 0:
						print "Analyzed %s Simulations" % str(count)
						print "Elapsed Time = %s mins" % str((time.time()-START)/60)

					results.append(main)
					iter_pool.append(numerical)

				#add the average row in
				results.append(average_iterations(non_numerical, iter_pool, arg_iters))


		if arg_print_to_csv:

			header=["sw_id", "Team", "metric_fcn", "aggregate_fcn", "lift_type", \
			"start_minute", "end_minute", "incr_minimum", "incr_maximum",\
			"daterange","start_date","end_date","outliers_flag","iteration","outlier_count", \
			"non_outlier_count", "mean_value", "statistical_significance", \
			"p_value", "terminal_command"]
	
			os.chdir("/Users/Swoboda/Desktop/")
			output_filename = "simulation_results.csv"
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