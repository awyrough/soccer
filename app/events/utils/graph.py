import pylab
import matplotlib.pyplot as plt
from numpy.random import rand
from datetime import datetime
import pandas as pd
# # plt.plot(range(10))
# # plt.savefig('testplot.png')
# # Image.open('testplot.png').save('testplot.jpg','JPEG')

# lifts = [-0.4678362573099
# ,1.1271929824561
# ,0.1071268489467
# ,0.3035367275554
# ,-0.5174418604651
# ,1.1515151515152
# ,-0.9225352112676
# ,-0.3461493100601
# ,0.1063591580833
# ,0.0820058997050
# ,-0.2092875318066
# ,-0.2307692307692
# ,0.0462885738115
# ,-0.8362573099415
# ,5.1782178217822
# ,-0.3333333333333
# ,-0.0833333333333
# ,0.3090909090909
# ,0.6882399368587
# ,0.0000000000000
# ,-0.0217744556386
# ,0.9919678714859
# ,-0.3013608870968
# ,-0.6540252827678
# ,0.1085189112761
# ,-0.1015625000000
# ,-0.1619047619048
# ,-0.4545454545455
# ,-0.0485714285714
# ,0.1388814557131
# ,-0.1543062200957
# ,-0.1845940319223
# ,-0.0930442637760
# ,-0.1758420862007
# ,-0.5654885654886
# ,-0.6058201058201
# ,0.1086711711712
# ,-0.0267593763169
# ,0.7777777777778
# ,-0.0568181818182
# ,-0.0353545328856
# ,-0.0488565488565
# ,-0.4800000000000
# ,0.0947368421053
# ,0.0131118881119
# ,-0.3940983606557
# ,0.7857142857143
# ,-0.1111111111111
# ,0.3125000000000
# ,-0.3506493506494
# ,0.6133333333333
# ,-0.6060606060606
# ,-0.3246753246753
# ,-0.1380471380471
# ,-0.1910021551724
# ,-0.2032967032967
# ,0.5333333333333
# ,0.6088154269972
# ,0.0655577299413
# ,0.6423611111111
# ,-0.1004453240970
# ,-0.1235973597360
# ,-0.0280991735537
# ,-0.5884353741497
# ,0.2499415478139
# ,-0.1504518872940
# ,0.1069004524887
# ,2.7142857142857
# ,-0.2565619784555
# ,3.5442176870748
# ,-0.3083832335329
# ,-0.1748379024002
# ,0.4274193548387
# ,-0.2592592592593
# ,-0.1428571428571
# ,0.1595361855258
# ,0.1831896551724
# ,0.1111111111111
# ,-0.2461538461538
# ,-0.1661807580175
# ,-0.1785714285714
# ,-0.3659878921299
# ,-1.0000000000000
# ,0.3536442006270]

# dates_string = ["3/7/15","3/22/15","3/22/15","4/11/15","4/11/15","4/11/15","4/11/15","4/18/15","4/18/15","4/25/15","4/25/15","5/2/15","5/2/15","5/9/15","5/9/15","5/13/15","5/13/15","5/13/15","5/23/15","5/23/15","5/27/15","5/30/15","5/30/15","5/30/15","6/3/15","6/3/15","6/3/15","6/3/15","6/6/15","6/6/15","6/6/15","6/14/15","6/21/15","6/21/15","6/21/15","6/24/15","7/3/15","7/18/15","7/26/15","7/26/15","7/26/15","7/26/15","7/26/15","8/1/15","8/1/15","8/1/15","8/1/15","8/1/15","8/1/15","8/1/15","8/1/15","8/1/15","8/8/15","8/13/15","8/13/15","8/13/15","8/13/15","8/22/15","8/22/15","8/30/15","8/30/15","8/30/15","9/12/15","9/12/15","9/19/15","9/19/15","9/19/15","9/26/15","9/26/15","10/2/15","10/2/15","10/18/15","10/18/15","10/18/15","10/18/15","10/25/15","10/25/15","10/25/15","10/25/15","10/25/15","10/28/15","10/28/15","10/28/15","11/1/15"]

# dates = [datetime.strptime(date, '%m/%d/%y').date() for date in dates_string]

# print(dates)

def plot_scatterplot(lift_tuple):
	# import Image
	pylab.show()

	for item in lift_tuple:
		lift = item[0]
		date = pd.to_datetime(item[1])

		plt.scatter(date, lift)

	plt.legend()
	plt.grid(True)
	plt.show()	

# for color in ['red', 'green', 'blue']:
#     n = 750
#     x, y = rand(2, n)
#     scale = 200.0 * rand(n)
#     plt.scatter(x, y, c=color, s=scale, label=color,
#                 alpha=0.3, edgecolors='none')


