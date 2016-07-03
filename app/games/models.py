from __future__ import unicode_literals

from django.db import models

class Game(models.Model):
	date = models.DateField("date played")
	homeTeam = models.ForeignKey("Team", related_name="homeTeam", default = -9999)
	awayTeam = models.ForeignKey("Team", related_name="awayTeam", default = -9999)
	stadium = models.ForeignKey("Stadium", null=True, blank=True, on_delete=models.SET_NULL)
	attendance = models.IntegerField("Attendance", null=True, blank=True)
	
	def __str__(self):
		return "%s vs. %s (%s)" % (self.homeTeam, self.awayTeam, self.date)

	def location(self):
		# The stadium field should only be populated
		# i.f.f. the game is played at a location OTHER THAN
		# the home team's main stadium?
		if self.stadium:
			return stadium
		else:
			return Stadium.objects.get(team=self.homeTeam)

	class Meta:
		unique_together = ["homeTeam", "awayTeam", "date"]

class Team(models.Model):
	sw_id = models.IntegerField(unique=True)
	name = models.CharField("Name", max_length = 50)
	conference = models.CharField("Conference", max_length = 20, null=True, blank=True)
	city = models.CharField("City", max_length = 50, null=True, blank=True)
	state = models.CharField("State", max_length = 20, null=True, blank=True)
	year_joined = models.IntegerField("yearJoined", default = -9999)
	
	def __str__(self):

		return self.name

class Stadium(models.Model):
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

	home_team = models.ForeignKey(Team)

	sw_id = models.IntegerField(unique=True)
	city = models.CharField("Stadium City", max_length=200)
	state = models.CharField("Stadium State", max_length=200)
	soccer_specific = models.BooleanField(default=False)
	
	def __str__(self):
		return self.name

	def surface_type(self):
		return self.SURFACES[int(self.surface) - 1][1]
