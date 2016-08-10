import pylab
import matplotlib.pyplot as plt
from numpy.random import rand
from datetime import datetime
import pandas as pd
import matplotlib.dates as mdates
from events.analysis.statistics import *

def plot_scatterplot(lift_tuple, title_string):

	pylab.show()

	f, ax = plt.subplots()

	for item in lift_tuple:
		lift = item[0]
		date = pd.to_datetime(item[1])

		#with plt.style.context('ggplot'):
		ax.scatter(date, lift*100, color='blue')


	mean, t_stat, p_val = statistical_significance(lift_tuple)

	plt.axhline(y=0, color="black")
	plt.axhline(y=mean*100, color="blue", linestyle="dashed")
		
	ax.set_title(title_string + '\nAvg Lift = %s \n Signif  = %s' % (mean*100, 1-p_val))
	plt.margins(x=0.05, y=0.05)
	ax.fmt_xdata = mdates.DateFormatter('%Y-%m-%d')
	plt.legend()
	plt.grid(True)
	plt.tight_layout()
	plt.show()	
