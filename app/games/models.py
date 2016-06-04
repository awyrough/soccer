from __future__ import unicode_literals

from django.db import models

# Create your models here.
class Game(models.Model):
	"""
	Model for MLS Games and meta information.
	"""
	date = models.DateField("date played")

	stadium = models.ForeignKey("Stadium")

	def __str__(self):
		return "%s" % self.date


# Create Stadium model
class Stadium(models.Model):
	"""
	Make a model for all stadiums used
	"""

	name = models.CharField("Stadium Name", max_length = 200)
	capacity = models.IntegerField("Capacity", default = 0)

	def __str__(self):
		return self.name