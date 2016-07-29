from __future__ import unicode_literals

from django.db import models

from games.models import Game, Team

import math

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

	# always return the raw number, so we can choose later to round up using math.ceil()
	"""How do we return 45+stoppage vs. 46 min?"""
	def get_minute_exact(self):
		minutes = self.seconds / 60.0
		if (self.half == 1):
			minutes = self.FIRST_HALF_START_MINUTE + minutes
		if (self.half == 2):
			minutes =  self.SECOND_HALF_START_MINUTE + minutes
		if (self.half == 3):
			minutes = self.EXTRA_TIME_START_MINUTE + minutes
		return minutes

	def get_minute_ceiling(self):
		"""
		Return ceiling of minute of action (as reported in box stats) from a given event.
				If there is less than 1 second of action into a new minute, don't round up
		    	If stoppage time, report -1 for 1st half or -2 for second half
		"""
		minutes = self.seconds / 60.0 #get approx minute
		if self.half == 1:
			if minutes > 45.0:
				minutes = -1
			else:
				minutes = int(self.seconds) / 60
				# as long as we're a full second into next minute, round up
				if self.seconds - minutes*60 >= 1:
					minutes += 1 
				minutes = float(minutes)
		elif self.half == 2:
			minutes += 45
			if minutes > 90.0:
				minutes = -2
			else:
				minutes = int(self.seconds) / 60
				# as long as we're a full second into next minute, round up
				if self.seconds - minutes*60 >= 1:
					minutes += 1
				# account for second half
				minutes += 45.0 
		else: # (self.half != 1) or (self.half != 2):
			raise Exception("This Event has no half associated with it?")
		return minutes

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
	action_team = models.ForeignKey(Team, related_name="actions", null=True,
				 default="", on_delete=models.SET_DEFAULT)
	def __str__(self):
		return "%s: %s %s @ %s (hf = %s)" % (self.game, 
					self.action_team,
					self.action,
					str(self.get_minute()),
					self.half)

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

def _default_moment_value():
	return models.IntegerField(default=0)

class TimeEvent(models.Model):
	FIRST_HALF_EXTRA_TIME = -1
	SECOND_HALF_EXTRA_TIME = -2

	team = models.ForeignKey(Team, on_delete=models.CASCADE)
	game = models.ForeignKey(Game, on_delete=models.CASCADE)
	
	# TODO(hillwyrough): set bounds on these fields for values
	time_on_pitch = models.FloatField()
	minute = models.IntegerField()
	
	home_score = _default_moment_value()
	away_score = _default_moment_value()
	
	# define stats
	passes = _default_moment_value()
	passes_succ = _default_moment_value()
	passes_unsucc = _default_moment_value()
	passes_received = _default_moment_value()
	
	shots = _default_moment_value()
	shots_on_target = _default_moment_value()
	goals = _default_moment_value()
	
	offsides = _default_moment_value()
	
	dribbles = _default_moment_value()
	crosses = _default_moment_value()
	corners_taken = _default_moment_value()
	free_kicks_taken = _default_moment_value()
	
	fouls = _default_moment_value()
	fouled = _default_moment_value()
	yellow_cards = _default_moment_value()
	red_cards = _default_moment_value()
	
	tackles = _default_moment_value()
	tackled = _default_moment_value()
	blocks = _default_moment_value()
	interceptions = _default_moment_value()
	clearances = _default_moment_value()
	blocked_shots = _default_moment_value()
	shots_on_target_ex_blocked = _default_moment_value()
	shots_off_target_ex_blocked = _default_moment_value()
	shots_inside_box = _default_moment_value()
	shots_on_target_inside_box = _default_moment_value()
	shots_outside_box = _default_moment_value()
	shots_on_target_outside_box = _default_moment_value()
	goals_inside_box = _default_moment_value()
	goals_outside_box = _default_moment_value()
	entries_final_third = _default_moment_value()
	entries_pen_area = _default_moment_value()
	entries_pen_area_succ = _default_moment_value()
	entries_pen_area_unsucc = _default_moment_value()
	first_time_passes = _default_moment_value()
	first_time_passes_complete = _default_moment_value()
	first_time_passes_incomplete = _default_moment_value()
	passes_attempted_ownhalf = _default_moment_value()
	passes_successful_ownhalf = _default_moment_value()
	passes_attempted_opphalf = _default_moment_value()
	passes_successful_opphalf = _default_moment_value()

	def _is_first_half_extra_time(self):
		return self.minute == FIRST_HALF_EXTRA_TIME

	def _is_second_half_extra_time(self):
		return self.minute == SECOND_HALF_EXTRA_TIME
