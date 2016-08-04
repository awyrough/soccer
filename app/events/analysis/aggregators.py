from events.utils.time_and_statistic import *
import numpy as np
import numbers

# Define the 'metric' here
PASSES = lambda x: x.passes
GOALS = lambda x: x.goals
PASS_ACCURACY = lambda x: float(x.passes_succ) / float(x.passes) if x.passes > 0 else None
# SHOTS = lambda x: x.shots
# SHOTS_ON_TARGET = lambda x: x.shots_ot
# SHOT_ACCURACY = lambda x: float(x.shots_ot) / float(x.shots) if x.shots > 0 else None
# SHOTS_INSIDE_BOX = lambda x: x.shots_inside_box
# SHOT_ACCURACY_INSIDE_BOX
# SHOTS_OUTSIDE_BOX = lambda x: x.shots_outside_box
# SHOT_ACCURACY_OUTSIDE_BOX
# CORNERS = lambda x: x.corners
# FREE_KICKS = lambda x: x.free_kicks_taken
# PEN_AREA_ENTRIES = lambda x: x.entries_pen_area
# PEN_AREA_ENTRY_ACCURACY 
# FINAL_3RD_ENTRIES = lambda x: x.entries_final_3rd
# PASSES_OWNHALF = lambda x: x.passes_attempted_ownhalf
# PASSES_OPPHALF = lambda x: x.passes_attempted_opphalf
# PASS_ACCURACY_OWNHALF
# PASS_ACCURACY_OPPHALF
# PASSES_FIRST_TIME = lambda x: x.first_time_passes
# PASS_ACCURACY_FIRST_TIME
# CLEARANCES = lambda x: x.clearances
# INTERCEPTIONS = lambda x: x.interceptions
# BLOCKS = lambda x: x.blocks
# OFFSIDES = lambda x: x.offsides
# DRIBBLES = lambda x: x.dribbles
# FOULS = lambda x: x.fouls
# FOULED = lambda x: x.fouled
# AGGRESSION_OWN = lambda x: float(x.fouls) / float(x.tackles) if x.tackles > 0 else None
# AGGRESSION_OPP = lambda x: float(x.fouled) / float(x.tackled) if x.tackled > 0 else None



# Define the 'aggregation' here (average, median, total)
SUM = lambda x: sum(x)
AVERAGE = lambda x: np.mean(x)

def pass_accuracy_improved(event):
	return float(event.passes_succ) / float(event.passes) if event.passes > 0 else None

def average_with_nones(values):
	non_null = [val for val in values if isinstance(val, numbers.Number)]
	if non_null:
		return sum(non_null) / len(non_null)
	return None

MAP_METRIC_FCN = {
	"passes": PASSES
	,"goals": GOALS
	,"pass_accuracy": PASS_ACCURACY
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