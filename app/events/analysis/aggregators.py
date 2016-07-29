from events.utils.time import get_game_time_events_for_team

# Define the 'metric' here
PASSES = lambda x: x.passes
PASS_ACCURACY = lambda x: x.passes_unsucc / x.passes

# Define the 'aggregation' here (average, median, total)
COUNT = lambda x: sum(x)

# Set some defaults for sanity and testing
DEFAULT_METRIC = PASSES
DEFAULT_AGGREGATE = COUNT

def do_collect_and_aggregate(
		game, team, windows, 
		metric=DEFAULT_METRIC, aggregate=DEFAULT_AGGREGATE):
	"""
	Iterate over windows and collect stats, bucket by windows,
	and run an aggregation.

	e.g. do_collect_and_aggregate(g, t, w) will produce an entry
	like '0-5': 43 (i.e. there were 43 passes in 0-5 for this team
		in this game)
	"""
	collection = {}
	for window in windows:
		start, end = window[0], window[1]
		events = get_game_time_events_for_team(
			game, team, start_minute=start, end_minute=end)
		time_hash = "%s-%s" % (start, end)
		collection[time_hash] = aggregate(
			[metric(event) for event in events])
	return collection