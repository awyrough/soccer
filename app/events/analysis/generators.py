import random

def create_artificial_windows_by_fn(
		step_fn, start=0, end=90, inc=1):
	"""
	Create artificial windows based on some functions.

	e.g. 

	fn(lambda x: x + 5) gives you all windows from 0 -> 90 by 
	5 minutes ([0, 5], [5, 10], etc.)

	fn(lambda x: x+5, end=20) will gives you all 5 min windows
	ending at 20 minutes.
	"""
	assert start <= end, "end can't be before start"
	windows = []
	time = start
	while start <= end:
		next = step_fn(start)
		window = [start, next if next < end else end]
		windows.append(window)
		start = next + inc
	return windows


def create_random_artificial_windows_with_bounds(
		start=0, end=90, inc_min=1, inc_max=10):
	"""
	Create artificial windows based on some functions.

	e.g. 

	fn(lambda x: x + 5) gives you all windows from 0 -> 90 by 
	5 minutes ([0, 5], [5, 10], etc.)

	fn(lambda x: x+5, end=20) will gives you all 5 min windows
	ending at 20 minutes.
	"""
	assert start <= end, "end can't be before start"
	assert inc_min <= inc_max, "minimum increment must be LTE to max"
	windows = []
	time = start
	inc = inc_min
	while start < end:
		if inc_min != inc_max:
			inc = random.randint(inc_min,inc_max)	
		next = start + inc
		window = [start, next if next <= end else end]
		windows.append(window)
		start = next
	return windows