from __future__ import unicode_literals

from django.db import models

"""
Notes:
	blank=True   <-  if T, then not required in form
	null=True 	 <-  if T, then can be stored as Null
	blank=True, null = True <- field is optional
"""

class Game(models.Model):
	"""
	Model for MLS Games and meta information.
	"""
	date = models.DateField("date played")
	homeTeam = models.ForeignKey('Team', related_name='homeTeam', default = -9999)
	awayTeam = models.ForeignKey('Team', related_name='awayTeam', default = -9999)
	stadium = models.ForeignKey('Stadium', null=True, blank=True, on_delete=models.SET_NULL)
	attendance = models.IntegerField("Attendance", null=True, blank=True)
	#add a weather FK at some point?
	def __str__(self):
		return "%s" % self.date

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
	SURFACES = (
		("1", "Grass"),
		("2", "AstroTurf"),
		("3", "FieldTurf"),
		("4", "Turf"),
		("5", "Bluegrass"),
		("6", "Polytan"),
		("7", "Team Pro EF RD"),
		("8", "AstroTurf GameDay Grass 3D"),
		("9", "Bermuda Bandera / Ryegrass Mixture")
	)

	name = models.CharField("Stadium Name", max_length=200)
	capacity = models.IntegerField("Soccer-specific capacity", default=0)
	year_opened = models.IntegerField(default=-9999)
	is_primary = models.BooleanField("Regular MLS stadium", default=True)
	surface = models.CharField(max_length=2, choices=SURFACES, default="1")

	# home_team = models.ForeignKey(Team)

	sw_id = models.IntegerField(unique=True)
	city = models.CharField("Stadium City", max_length=200)
	state = models.CharField("Stadium State", max_length=200)
	soccer_specific = models.BooleanField(default=False)
	
	def __str__(self):
		return self.name

	def surface_type(self):
		return self.SURFACES[int(self.surface) - 1][1]
