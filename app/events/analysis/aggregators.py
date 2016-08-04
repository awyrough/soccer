from events.utils.time_and_statistic import *
import numpy as np
import numbers

# Define the 'metric' here
PASSES = lambda x: x.passes
GOALS = lambda x: x.goals
PASS_ACCURACY = lambda x: float(x.passes_succ) / float(x.passes) if x.passes > 0 else None

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