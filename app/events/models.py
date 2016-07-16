from __future__ import unicode_literals

from django.db import models

from games.models import Game

class GameEvent(models.Model):
	"""
	Abstract class for game events.
	This should hold any common fields among all game-level events.
	"""
	FIRST_HALF_START_MINUTE = 0.0
	FIRST_HALF_START_SECOND = 0.0
	SECOND_HALF_START_MINUTE = 45.0
	SECOND_HALF_START_SECOND = 2700.0
	EXTRA_TIME_START_MINUTE = 90.0
	EXTRA_TIME_START_SECOND = 5400.0

	game = models.ForeignKey(Game, on_delete=models.CASCADE)
	half = models.IntegerField(default=1, choices=((1,1), (2,2), (3,3)))
	seconds = models.FloatField(default=0.0)

	class Meta:
		"""
		NB: This means there will be no GameEvent table. It is just a
		design pattern.
		"""
		abstract = True

	def is_first_half(self):
		return self.half == 1

	def is_second_half(self):
		return self.half == 2
	
	def is_extra_time(self):
		return self.half >= 3

	def get_minute(self, rounding=1):
		minutes = self.seconds / 60.0
		if (self.half == 1):
			minutes = self.FIRST_HALF_START_MINUTE + minutes
		if (self.half == 2):
			minutes =  self.SECOND_HALF_START_MINUTE + minutes
		if (self.half == 3):
			minutes = self.EXTRA_TIME_START_MINUTE + minutes
		return round(minutes, rounding)

class StatisticEvent(GameEvent):
	ACTIONS = (
		("BLOCK", "Block"),
		("CLEARANCE", "Clearance"),
		("CORNER_CROSS", "Corner Cross"),
		("CROSS", "Cross"),
		("DEFLECTION", "Deflection"),
		("DIRECT_FREE_KICK_CROSS", "Direct Free Kick Cross"),
		("DIRECT_FREE_KICK_PASS", "Direct Free Kick Pass"),
		("DIRECT_FREE_KICK_SHOT", "Direct Free Kick Shot"),
		("DRIBBLE", "Dribble"),
		("DROP_BALL", "Drop Ball"),
		("FOUL", "Foul"),
		("FOUL_THROW", "Foul Throw"),
		("GOAL", "Goal"),
		("GOAL_KICK", "Goal Kick"),
		("GOALKEEPER_CATCH", "Goalkeeper Catch"),
		("GOALKEEPER_DROP_CATCH", "Goalkeeper Drop Catch"),
		("GOALKEEPER_KICK", "Goalkeeper Kick"),
		("GOALKEEPER_PICK_UP", "Goalkeeper Pick Up"),
		("GOALKEEPER_PUNCH", "Goalkeeper Punch"),
		("GOALKEEPER_SAVE", "Goalkeeper Save"),
		("GOALKEEPER_SAVE_CATCH", "Goalkeeper Save Catch"),
		("GOALKEEPER_THROW", "Goalkeeper Throw"),
		("HANDBALL", "Handball"),
		("HEADER", "Header"),
		("HEADER_SHOT", "Header Shot"),
		("INDIRECT_FREE_KICK_CROSS", "Indirect Free Kick Cross"),
		("INDIRECT_FREE_KICK_PASS", "Indirect Free Kick Pass"),
		("KICK_OFF", "Kick Off"),
		("OFFSIDE", "Offside"),
		("OWN_GOAL", "Own Goal"),
		("PASS", "Pass"),
		("PENALTY_SHOT", "Penalty Shot"),
		("RED_CARD", "Red Card"),
		("SHOT", "Shot"),
		("START_OF_HALF", "Start Of Half"),
		("SUBSTITUTION", "Substitution"),
		("TACKLE", "Tackle"),
		("THROWN_IN", "Thrown In"),
		("TOUCH", "Touch"),
		("YELLOW_CARD", "Yellow Card"),
	)
	
	action = models.CharField(max_length=50, choices=ACTIONS,
				  default="TOUCH")
	#player = models.ForeignKey(Player, related_name="actions", null=True,
	#			   default=null, on_delete=models.SET_DEFAULT)
	#team = models.ForeignKey(Team, related_name="actions", null=True,
	#			 default=null, on_delete=models.SET_DEFAULT)
	def __str__(self):
		return "%s: %s @ %s" % (self.game, 
					self.action,
					str(self.get_minute()))

	class Meta:
		# TODO(hillwyrough): define unique together
		pass

class Goal(GameEvent):
	"""
	Intended fields:
		- Player/Scorer
	NB: This should **not** have information about the goal itself.
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
