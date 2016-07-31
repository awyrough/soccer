import numpy as np
from scipy.stats import ttest_1samp, wilcoxon, ttest_ind, mannwhitneyu


def lift(pre_value, post_value):
	"""
	Define, mathematically, how we want to calculate lift between T-1 and T
	"""
	return (post_value - pre_value) / pre_value

def get_time_type_code(time_type):
	known_types = ["Total", "Per Min"]
	if time_type not in known_types:
		raise Exception("Unknown time type")
	if time_type == "Total":
		return 0
	elif time_type == "Per Min":
		return 1
	else:
		return None

def calculate_lift(games, agg_collection, time_type, min_time_window):
	"""
	Time Types:
		0 = Total
		1 = Per Min 
		(?) 2 = Per Game
	"""
	calculated_lifts = []

	for game in games:
		previous = None
		for index in sorted(agg_collection[game]):
			current = agg_collection[game][index]
			#if the first window, save and continue
			if index == 0 and current[2] > min_time_window:
				previous = current
				continue
			# if the window is long enough
			if current[2] > min_time_window:
				# if this game has a legitimate previous time window to compare to
				# and if the pre won't be 0 (as you can't calculate)
				if previous and previous[0] != 0:
					if time_type == 0:
						pre = float(previous[0])
						post = float(current[0])
					elif time_type == 1:
						pre = float(previous[0]) / previous[2]
						post = float(current[0]) / current[2]						
					else: #other cases we haven't planned for yet
						pre = None
						post = None
					lift_value = lift(pre, post)

					calculated_lifts.append(lift_value)
					agg_collection[game][index] = agg_collection[game][index] + (lift_value,)
				# replace what is the most previous legitimate time window
				previous = current

	return calculated_lifts, agg_collection

def statistical_significance(lifts, null_hypo = 0):
	"""
	Method to input lifts and understand statistical significance of measurement	
	"""
	lifts = np.array(lifts)
	
	mean = np.mean(lifts)
	t_statistic, p_value = ttest_1samp(lifts, null_hypo)
	
	return mean, t_statistic, p_value

