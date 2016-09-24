import numpy as np
from scipy import stats
from scipy.stats import ttest_1samp, wilcoxon, ttest_ind, mannwhitneyu


def LIFT_TOTAL(previous, current):
	"""
	At a total level calculate lift between T-1 and T

	Inputs are lists of the form: (350, '[0, -2]', 95.5, 'Meta Info', 0)

	"""
	post = float(current[0])
	pre = float(previous[0])

	return (post - pre) / pre

def LIFT_PER_MIN(previous, current):
	"""
	At a per-min level calculate lift between T-1 and T

	Inputs are lists of the form: (350, '[0, -2]', 95.5, 'Meta Info', 0)

	"""
	post = float(current[0])/float(current[2])
	pre = float(previous[0])/float(previous[2])

	return (post - pre) / pre

MAP_LIFT_TYPE_FCN = {
	"total": LIFT_TOTAL
	,"per_min": LIFT_PER_MIN
}

def calculate_lift(games, agg_collection, lift_fcn, min_time_window=0):
	"""
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
				# and if the pre value won't be 0 (as you can't calculate)
				# and if the pre value isn't None (in the case of all ratios being None)
				if previous and previous[0] != 0 and previous[0] and current[0]:
					lift_value = lift_fcn(previous, current)

					calculated_lifts.append((lift_value, str(game.date)))
					agg_collection[game][index] = agg_collection[game][index] + (lift_value,)
				# replace what is the most previous legitimate time window
				previous = current

	return calculated_lifts, agg_collection

def extract_only_indexed_values(lift_array, index):
	x = []
	for item in lift_array:
		if type(item) != type((1,1)): #if the array is of tuples,
			x = lift_array
			break
		x.append(item[index])

	return x

def onesample__statistical_significance(actual_lifts_tuple_list, null_hypo = 0):
	"""
	Method to input lifts and understand statistical significance of measurement	
	"""
	actual = extract_only_indexed_values(actual_lifts_tuple_list, 0)
	actual = np.array(actual)
	
	mean = np.mean(actual)
	t_statistic, p_value = ttest_1samp(actual, null_hypo)
	
	return mean, t_statistic, p_value

def twosample__statistical_significance(actual_lifts_tuple_list, simulated_tuple_list):
	"""
	Method to input lifts and understand statistical significance of measurement	
	"""
	actual = extract_only_indexed_values(actual_lifts_tuple_list, 0)
	actual = np.array(actual)
	actual_mean = np.mean(actual)

	simulated = extract_only_indexed_values(simulated_tuple_list, 0)
	simulated = np.array(simulated)
	simulated_mean = np.mean(simulated)

	mean = np.mean(actual)
	#use Welch's t-test (http://iaingallagher.tumblr.com/post/50980987285/t-tests-in-python)
	t_statistic, p_value = ttest_ind(actual, simulated, equal_var=False)
	
	return actual_mean, simulated_mean, t_statistic, p_value

def is_outlier(points, thresh=4):
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

def identify_outliers(points_tuple_list):
	points = extract_only_indexed_values(points_tuple_list, 0)
	dates = extract_only_indexed_values(points_tuple_list, 1)

	outlier_bool, z_score = is_outlier(points)

	if len(points) != len(outlier_bool):
		raise Exception("Lists not the same lenghth")
	
	return zip(points, dates, outlier_bool, z_score)

def run_outlier_check(points_tuple_list):
	zipped = identify_outliers(points_tuple_list)

	outliers = []
	non_outliers = []

	for item in zipped:
		if item[2] == False:
			non_outliers.append((item[0], item[1], item[3]))
		else:
			outliers.append((item[0], item[1], item[3]))
		
	if len(non_outliers) + len(outliers) != len(zipped):
		raise Exception("Lost data points")

	return non_outliers, outliers

def relative_performance(moment_perf, simulated_perf):
	if moment_perf > simulated_perf:
		sign = 1
	elif moment_perf < simulated_perf:
		sign = -1
	else:
		sign = 0

	percent_chg = round(abs((moment_perf - simulated_perf) / simulated_perf),1)

	return sign*percent_chg
