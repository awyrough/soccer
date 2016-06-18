from __future__ import unicode_literals

from django.db import models

from games.models import Game

class GameEvent(models.Model):
	"""
	Abstract class for game events.

	This should hold any common fields among all game-level events.

	It defines a many-to-one relationship with a Game, i.e. GameEvents can
	be accessed through the Game using 
		"GameEvents.objects.filter(game=game) = all game events for a game"
		"game.gameevent_set = all game events for a game"
	"""
	game = models.ForeignKey(Game, on_delete=models.CASCADE)
	minute = models.IntegerField()

	class Meta:
		"""
		NB: This means there will be no GameEvent table. It is just a
		design pattern.
		"""
		abstract = True

class Goal(GameEvent):
	"""
	Intended fields:
		- Player/Scorer
	NB: This should **not** have information about the goal itself, I think
	this should be reserved for a StatisticsEvent which is linked to this goal.
	But this is a converation for another day and not worth talking about.
	"""
	pass

class Substitution(GameEvent):
	"""
	Intended fields:
		- player_on
		- player_off
		- reason (tactical/injury)
	"""
	pass

class DisciplinaryAction(GameEvent):
	"""
	Intended fields:
		- player
		- type (red/yellow)
	"""
	pass