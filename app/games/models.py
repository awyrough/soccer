from __future__ import unicode_literals

from django.db import models

"""
Notes:
	blank=True   <-  if T, then not required in form
	null=True 	 <-  if T, then can be stored as Null
	blank=True, null = True <- field is optional
"""

# Create your models here.
class Game(models.Model):
	"""
	Model for MLS Games and meta information.
	"""
	date = models.DateField("date played")
	homeTeam = models.ForeignKey('Team', related_name='homeTeam', default = -9999)
	awayTeam = models.ForeignKey('Team', related_name='awayTeam', default = -9999)
	stadium = models.ForeignKey('Stadium', null=True, blank=True)
	attendance = models.IntegerField("Attendance", null=True, blank=True)
	#add a weather FK at some point?
	def __str__(self):
		return "%s" % self.date

# Create Team model
class Team(models.Model):
	"""
	Model for each soccer team
	"""
	#teamID automatically made
	name = models.CharField("Name", max_length = 50)
	conference = models.CharField("Conference", max_length = 20, null=True)
	city = models.CharField("City", max_length = 50, null=True, blank=True)
	state = models.CharField("State", max_length = 20, null=True, blank=True)
	yearJoined = models.IntegerField("yearJoined", default = -9999, null=True)


# Create Stadium model
class Stadium(models.Model):
	"""
	Make a model for all stadiums used
	"""

	name = models.CharField("Stadium Name", max_length = 200)
	capacity = models.IntegerField("Capacity", default = 0)

	def __str__(self):
		return self.name