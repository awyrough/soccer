from events.utils.time_and_statistic import *
import numpy as np

# Define the 'metric' here
PASSES = lambda x: x.passes
GOALS = lambda x: x.goals
PASS_ACCURACY = lambda x: x.passes_unsucc / x.passes

# Define the 'aggregation' here (average, median, total)
COUNT = lambda x: sum(x)
AVERAGE = lambda x: np.mean(x)

# Set some defaults for sanity and testing
DEFAULT_METRIC = PASSES
DEFAULT_AGGREGATE = COUNT

def metric_command(metric_string):
	m_c = {}
	m_c["passes"] = PASSES
	m_c["goals"] = GOALS
	m_c["pass_accuracy"] = PASS_ACCURACY

	return m_c[metric_string]

def do_collect_and_aggregate(
		team, game, windows, meta_info, agg_tally_moments,
		metric=DEFAULT_METRIC, aggregate=DEFAULT_AGGREGATE):
	"""
	Iterate over windows and collect stats, bucket by windows,
	and run an aggregation.

	e.g. do_collect_and_aggregate(t, g, w) will produce an entry
	like '0-5': 43 (i.e. there were 43 passes in 0-5 for this team
		in this game)
	"""
	if metric in [PASS_ACCURACY]:
		aggregate = AVERAGE
	collection = {}
	window_count = 0
	for window in windows:
		start, end = window[0], window[1]
		events = get_game_time_events_for_team(
			game, team, start_minute=start, end_minute=end)
		time_hash = "[%s, %s]" % (start, end)
		agg_metric = aggregate([metric(event) for event in events])
		collection[window_count] = (agg_metric, time_hash, time_window_length((start,end)) \
				, meta_info[window_count], agg_tally_moments[window_count])
		window_count += 1
	return collection