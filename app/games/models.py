from __future__ import unicode_literals

from django.db import models

# Create your models here.
class Game(models.Model):
	"""
	Model for MLS Games and meta information.
	"""
	date = models.DateField("date played")

	def __str__(self):
		return "%s" % self.date