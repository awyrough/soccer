# batch_agg_with_sim_two_sample_2016_playoffs.py

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
			"--print_to_csv",
			action="store_true",
            dest="print_to_csv",
            default=False,
            help="save file?",
            )
		parser.add_argument(
			"--simulation_iterations",
            dest="simulation_iterations",
            default="",
            help="number of null hypo iterations?",
            )
		parser.add_argument(
			"--daterange",
            dest="daterange",
            default=False,
            help="Example comma separated format: 2015-06-13,2015-08-09",
            )
		parser.add_argument(
			"--filename",
            dest="filename",
            default="",
            help="addition to filename?",
            )

	def handle(self,*args,**options):
		START = time.time()
		prev_time = START
		if not options["simulation_iterations"]:
			raise Exception("Number of simulation iterations is needed")

		arg_daterange = str(options["daterange"]) #if this is not specified, then this will just be false
		arg_filename = str(options["filename"])
		arg_print_to_csv = options["print_to_csv"]
		simulation_iterations = int(options["simulation_iterations"])

		results = []
		VARIABLE_CRITERIA = []

		sw_ids = [4]
		moments_and_maxSimWindows = [("GOAL", 60), ("SUBSTITUTION", 30), ("YELLOW_CARD", 45)]
		# moment_teams = ["Both", "Self", "Oppo"]
		moment_teams = ["Self", "Oppo"]
		min_tws = [5.0]	
		# min_tws = [5.0, 7.5, 10.0, 15.0]
		other_info = {
			#key: metric_fcn, aggregation_fcn, lift_type
			0:["passes","sum","per_min"]
			,1:["pass_accuracy","average","total"]
			,2:["pass_balance","average","total"]
			,3:["passes_first_time","sum","per_min"]
			,4:["passes_first_time_accuracy","average","total"]
			,5:["shots","sum","per_min"]
			,6:["shots_on_target","sum","per_min"]
			,7:["shot_accuracy","average","total"]
			,8:["shot_balance","average","total"]
			,9:["pen_area_entries","sum","per_min"]
			,10:["pen_area_entry_accuracy","average","total"]
			,11:["final_3rd_entries","sum","per_min"]
			,12:["fouls","sum","per_min"]
			,13:["tackles","sum","per_min"]
			,14:["tackled","sum","per_min"]
			,15:["tackle_balance","average","total"]
			,16:["interceptions","sum","per_min"]
			,17:["clearances","sum","per_min"]
			,18:["aggression_own","average","total"]
		}

		#load in the various variable criteria to then run the scripts
		for sw_id in sw_ids:
			for item in moments_and_maxSimWindows:
				moment = item[0]
				max_simulated_incr = item[1]
				for key, value in other_info.iteritems():
					for moment_team in moment_teams:
						for min_tw in min_tws:
							VARIABLE_CRITERIA.append([sw_id, moment, moment_team, value[0],\
								value[1], value[2], min_tw, max_simulated_incr])

		print "1) Have Created VARIABLE_CRITERIA \t(%s mins; %s)" % (str((time.time()-START)/60), time.strftime('%l:%M%p %Z'))	
		print "----------------------------------"



		if arg_print_to_csv:
			os.chdir("/Users/Swoboda/Desktop/")
			temp_output_filename = "twosamp_results__" + str(time.strftime('%Y_%m_%d')) + "_" + arg_filename + "_tempBuild.csv"
			temp_output = open(temp_output_filename, "a")
			temp_writer = csv.writer(temp_output, lineterminator="\n")

			output_filename = "twosamp_results__" + str(time.strftime('%Y_%m_%d')) + "_" + arg_filename + ".csv"
			output = open(output_filename, "a")
			writer = csv.writer(output, lineterminator="\n")
	

		header = []
		count = 0
		temp_results = []
		temp_results_count = 0

		for vc in VARIABLE_CRITERIA:
			row, head = aggregate_vs_simulate_two_sample(vc[0], vc[1], vc[2], vc[3],\
				vc[4], vc[5], iterations=simulation_iterations, daterange=arg_daterange,
				min_tw=vc[6], outliers_flag=True, max_simulated_incr=vc[7])
			results.append(row)
			temp_results.append(row)
			count += 1

			if count == 1:
				header = head
				temp_writer.writerow(header)

			if count % 5 == 0:
				for r in temp_results:
					temp_writer.writerow(r)

				print "Analyzed %s Aggregation-Simulation Combinations" % str(count)
				print "		delta = %s mins; elapsed = %s mins; \t %s" % (str((time.time()-prev_time)/60), str((time.time()-START)/60), time.strftime('%l:%M%p %Z'))	
				prev_time = time.time()

				temp_results = []

			
		if arg_print_to_csv:	
			temp_output.close()

			writer.writerow(header)
		
			for r in results:
				writer.writerow(r)

			output.close()	
		
		print "Total Elapsed Time = %s mins" % str((time.time()-START)/60)
