from events.utils.time_and_statistic import *
import numpy as np
import numbers


# Create a function to be used in all of the Lambda functions below
def ratio_with_nones(numerator, denominator):
	return float(numerator) / float(denominator) if float(denominator) > 0 else None

# Define the 'metric' here
PASSES = lambda x: x.passes
GOALS = lambda x: x.goals
PASS_ACCURACY = lambda x: ratio_with_nones(x.passes_succ, x.passes) 
SHOTS = lambda x: x.shots
SHOTS_ON_TARGET = lambda x: x.shots_on_target
SHOTS_OFF_TARGET = lambda x: x.shots - x.shots_on_target
SHOT_ACCURACY = lambda x: ratio_with_nones(x.shots_on_target, x.shots)
SHOTS_INSIDE_BOX = lambda x: x.shots_inside_box
SHOTS_INSIDE_BOX_ON_TARGET = lambda x: x.shots_on_target_inside_box
SHOT_ACCURACY_INSIDE_BOX = lambda x: ratio_with_nones(x.shots_on_target_inside_box, x.shots_inside_box)
SHOTS_OUTSIDE_BOX = lambda x: x.shots_outside_box
SHOTS_OUTSIDE_BOX_ON_TARGET = lambda x: x.shots_on_target_outside_box
SHOT_ACCURACY_OUTSIDE_BOX = lambda x: ratio_with_nones(x.shots_on_target_outside_box, x.shots_outside_box)
SHOT_BALANCE = lambda x: ratio_with_nones(x.shots_inside_box, x.shots_outside_box + x.shots_inside_box)

BLOCKED_SHOTS = lambda x: x.blocked_shots
SHOT_BLOCKED_RATIO = lambda x: ratio_with_nones(x.blocked_shots, x.shots)
CORNERS = lambda x: x.corners
FREE_KICKS = lambda x: x.free_kicks_taken
PEN_AREA_ENTRIES = lambda x: x.entries_pen_area
PEN_AREA_ENTRIES_SUCC = lambda x: x.entries_pen_area_succ
PEN_AREA_ENTRIES_UNSUCC = lambda x: x.entries_pen_area_unsucc
PEN_AREA_ENTRY_ACCURACY = lambda x: ratio_with_nones(x.entries_pen_area_succ, x.entries_pen_area)
FINAL_3RD_ENTRIES = lambda x: x.entries_final_third
PASSES_OWNHALF = lambda x: x.passes_attempted_ownhalf
PASSES_OWNHALF_SUCC = lambda x: x.passes_successful_ownhalf
PASSES_OPPHALF = lambda x: x.passes_attempted_opphalf
PASSES_OPPHALF_SUCC = lambda x: x.passes_successful_opphalf
PASS_ACCURACY_OWNHALF = lambda x: ratio_with_nones(x.passes_successful_ownhalf, x.passes_attempted_ownhalf)
PASS_ACCURACY_OPPHALF = lambda x: ratio_with_nones(x.passes_successful_opphalf, x.passes_attempted_opphalf)
PASSES_FIRST_TIME = lambda x: x.first_time_passes
PASSES_FIRST_TIME_SUCC = lambda x: x.first_time_passes_complete
PASSES_FIRST_TIME_UNSUCC = lambda x: x.first_time_passes_incomplete
PASS_ACCURACY_FIRST_TIME = lambda x: ratio_with_nones(x.first_time_passes_complete, x.first_time_passes)
PASS_BALANCE = lambda x: ratio_with_nones(x.passes_attempted_opphalf, x.passes_attempted_ownhalf + x.passes_attempted_opphalf)

CLEARANCES = lambda x: x.clearances
INTERCEPTIONS = lambda x: x.interceptions
BLOCKS = lambda x: x.blocks
OFFSIDES = lambda x: x.offsides
DRIBBLES = lambda x: x.dribbles
FOULS = lambda x: x.fouls
FOULED = lambda x: x.fouled
TACKLES = lambda x: x.tackles
TACKLED = lambda x: x.tackled
TACKLE_BALANCE = lambda x: ratio_with_nones(x.tackles, x.tackles + x.tackled)
AGGRESSION_OWN = lambda x: ratio_with_nones(x.fouls, x.tackles)
AGGRESSION_OPP = lambda x: ratio_with_nones(x.fouled, x.tackled) 
YELLOW_CARDS = lambda x: x.yellow_cards
RED_CARDS = lambda x: x.red_cards 


# Define the 'aggregation' here (average, median, total)
SUM = lambda x: sum(x)
AVERAGE = lambda x: np.mean(x)

def average_with_nones(values):
	non_null = [val for val in values if isinstance(val, numbers.Number)]
	if non_null:
		return sum(non_null) / len(non_null)
	return None

MAP_METRIC_FCN = {
	"passes": PASSES
	,"goals": GOALS
	,"pass_accuracy": PASS_ACCURACY
	,"pass_balance":PASS_BALANCE
	,"shot_accuracy": SHOT_ACCURACY
	,"final_3rd_entries": FINAL_3RD_ENTRIES
	,"pen_area_entry_accuracy": PEN_AREA_ENTRY_ACCURACY
	,"offsides":OFFSIDES
	,"dribbles":DRIBBLES
	,"aggression_own":AGGRESSION_OWN
	,"aggression_opp":AGGRESSION_OPP
	,"tackles":TACKLES
	,"tackled":TACKLED
	,"tackle_balance":TACKLE_BALANCE
	,"fouls":FOULS
	,"blocks":BLOCKS
	,"interceptions":INTERCEPTIONS
	,"clearances":CLEARANCES
	,"shots_inside_box":SHOTS_INSIDE_BOX
	,"shots_outside_box":SHOTS_OUTSIDE_BOX
	,"shot_accuracy_inside_box":SHOT_ACCURACY_INSIDE_BOX
	,"shot_accuracy_outside_box":SHOT_ACCURACY_OUTSIDE_BOX
	,"shot_balance":SHOT_BALANCE
}

MAP_AGGREGATE_FCN = {
	"sum": SUM
	,"average": average_with_nones
}

def do_collect_and_aggregate(
		team, game, windows, meta_info, agg_tally_moments,
		metric_fcn, aggregate_fcn):
	"""
	Iterate over windows and collect stats, bucket by windows,
	and run an aggregation.

	e.g. do_collect_and_aggregate(t, g, w) will produce an entry
	like '0-5': 43 (i.e. there were 43 passes in 0-5 for this team
		in this game)
	"""
	collection = {}
	window_count = 0
	for window in windows:
		start, end = window[0], window[1]
		events = get_game_time_events_for_team(
			game, team, start_minute=start, end_minute=end)
		time_hash = "[%s, %s]" % (start, end)
		agg_metric = aggregate_fcn([metric_fcn(event) for event in events])
		collection[window_count] = (agg_metric, time_hash, time_window_length((start,end)) \
				, meta_info[window_count], agg_tally_moments[window_count])
		window_count += 1
	return collection