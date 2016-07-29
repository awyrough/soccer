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