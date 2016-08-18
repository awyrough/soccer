# batch_agg_with_sim_two_sample.py.py


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
	def handle(self,*args,**options):
		if not options["simulation_iterations"]:
			raise Exception("Number of simulation iterations is needed")

		START = time.time()
		prev_time = START
		arg_print_to_csv = options["print_to_csv"]
		simulation_iterations = int(options["simulation_iterations"])

		results = []
		VARIABLE_CRITERIA = []

		sw_ids = [3, 7]
		moments_and_maxSimWindows = [("GOAL", 60), ("SUBSTITUTION", 30), ("YELLOW_CARD", 45)]
		moment_teams = ["Both", "Self", "Oppo"]
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
		# min_tws = [5.0, 7.5, 10.0, 15.0]
		min_tws = [5.0]
		
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

		header = []
		count = 0
		for vc in VARIABLE_CRITERIA:
			row, head = aggregate_vs_simulate_two_sample(vc[0], vc[1], vc[2], vc[3],\
				vc[4], vc[5], iterations=simulation_iterations, min_tw=vc[6],\
				outliers_flag=True,max_simulated_incr=vc[7])
			results.append(row)

			if count == 0:
				header = head
			count += 1
			if count % 10 == 0:
				print "Analyzed %s Aggregation-Simulation Combinations" % str(count)
				print "		delta = %s mins; elapsed = %s mins; \t %s" % (str((time.time()-prev_time)/60), str((time.time()-START)/60), time.strftime('%l:%M%p %Z'))	
				prev_time = time.time()
			
		if arg_print_to_csv:
			os.chdir("/Users/Swoboda/Desktop/")
			output_filename = "twosample_results__" + str(time.strftime('%Y_%m_%d')) + ".csv"
			output = open(output_filename, "a")
			writer = csv.writer(output, lineterminator="\n")

			writer.writerow(header)

			for r in results:
				writer.writerow(r)

			output.close()

		print "Total Elapsed Time = %s mins" % str((time.time()-START)/60)
