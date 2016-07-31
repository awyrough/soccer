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

					calculated_lifts.append((lift_value, str(game.date)))
					agg_collection[game][index] = agg_collection[game][index] + (lift_value,)
				# replace what is the most previous legitimate time window
				previous = current

	return calculated_lifts, agg_collection

def extract_only_first_values(lift_array):
	x = []
	for item in lift_array:
		x.append(item[0])
	return x

def statistical_significance(lifts, null_hypo = 0):
	"""
	Method to input lifts and understand statistical significance of measurement	
	"""
	lifts = np.array(lifts)
	
	mean = np.mean(lifts)
	t_statistic, p_value = ttest_1samp(lifts, null_hypo)
	
	return mean, t_statistic, p_value

def is_outlier(points, thresh=3.5):
    """
    Returns a boolean array with True if points are outliers and False 
    otherwise.

    AJ's Threshold logic: Leys, C., et al., Detecting outliers: Do not use standard deviation around the mean, 
	use absolute deviation around the median, Journal of Experimental Social Psychology (2013), 
	LINK: http://dx.doi.org/10.1016/j.jesp.2013.03.013

    Input:
        points = List of lifts
        thresh = The modified z-score to use as a threshold. Observations with
            a modified z-score (based on the median absolute deviation) greater
            than this value are classified as outliers.

    Returns:
    	A boolean array

    References:
        Boris Iglewicz and David Hoaglin (1993), "Volume 16: How to Detect and
        Handle Outliers", The ASQC Basic References in Quality Control:
        Statistical Techniques, Edward F. Mykytka, Ph.D., Editor. 
    """
    points = np.array(points)
    median = np.median(points, axis=0)
    diff = np.absolute(points - median)
    med_abs_deviation = np.median(diff)

    modified_z_score = 0.6745 * diff / med_abs_deviation

    return modified_z_score > thresh, modified_z_score

def identify_outliers(points):
	outlier_bool, z_score = is_outlier(points)

	if len(points) != len(outlier_bool):
		raise Exception("Lists not the same lenghth")
	
	return zip(points, outlier_bool, z_score)

def run_outlier_check(points):
	zipped = identify_outliers(points)

	outliers = []
	non_outliers = []

	for item in zipped:
		if item[1] == False:
			non_outliers.append((item[0], item[2]))
		else:
			outliers.append((item[0], item[2]))
		
	if len(non_outliers) + len(outliers) != len(zipped):
		raise Exception("Lost data points")

	return non_outliers, outliers


