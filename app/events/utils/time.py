from events.models import StatisticEvent, TimeEvent
from games.models import Game

def get_game_events(game):
    return TimeEvent.objects.filter(game=game).order_by("minute")

def _include_first_half_stoppage(start, end):
    """
    Return true if the start and end times span the first half
    stoppage time.
    """
    # If you start in the first half and end in the second half
    # or beyond
    if (start <= 45 or start == -1) and (end > 45 or end == None):
        return True

def _include_second_half_stoppage(start, end):
    """
    Return true if the start and end times span the second
    half stoppage time.
    """
    # You would only include if there is no end
    return end > 90 or end == None or end == -2

def get_game_time_events(game, start_minute=None, end_minute=None):
    """
    Return the time events in a game that begin with start minute
    and end with end minute, inclusive.
    """
    queryset = get_game_events(game) 
    if (not _include_first_half_stoppage(start_minute, end_minute)):
        queryset = queryset.exclude(
            minute=TimeEvent.FIRST_HALF_EXTRA_TIME)
    if (not _include_second_half_stoppage(start_minute, end_minute)):
        queryset = queryset.exclude(
            minute=TimeEvent.SECOND_HALF_EXTRA_TIME)
    if start_minute != None:
        queryset = queryset.filter(minute__gt=start_minute)
    if end_minute != None:
        queryset = queryset.filter(minute__lte=end_minute)
    return queryset

def get_game_time_events_for_team(
    game, team, start_minute=None, end_minute=None):
    """
    Return the minute events by team.
    """
    return get_game_time_events(
        game, start_minute=start_minute, end_minute=end_minute) \
            .filter(team=team)

def get_game_statistic_events(game):
    """
    Return all statistics from a given game.
    """
    return StatisticEvent.objects.filter(game=game)

def get_game_stats_by_action_and_team(team, game, action, identifier):
    """
    Return all statistics from a given game and action. Changes depending on Both, Self, Oppo relative to team
    """
    if identifier == "Both":
        return get_game_statistic_events(game).filter(action=action)
    if identifier == "Self":
        return get_game_statistic_events(game).filter(action=action, action_team=team)
    if identifier == "Oppo":
        return get_game_statistic_events(game).filter(action=action).exclude(action_team = team)

def create_windows_for_game(team, game, action, identifier):
    """
    Return list of tuples as [start, end] of all the windows
    in a game.

    If there are no actions, it returns a full game window.
    If the last action is before the end of the game, the final
    window should be until the end of the game, including stoppage.
    """
    actions = get_game_stats_by_action_and_team(team, game, action, identifier) \
        .order_by("half", "seconds")
    if actions.count() == 0:
        return [[0, StatisticEvent.SECOND_HALF_EXTRA_TIME], ]
    windows = []
    start = 0
    last_action = None
    for action in actions:
        end = action.get_minute_ceiling()
        window = [start, end]
        windows.append(window)
        start = end # remember the start of window is exclusive
        last_action = action
    if last_action.get_minute_ceiling() != -2:
        windows.append([start, StatisticEvent.SECOND_HALF_EXTRA_TIME])
    return windows

def time_window_length(tuple):
    """
    Input a time window tuple and output a time length in minutes.
    Use 2015 Season Avgs for 1st half and 2nd half stoppage lengths
    """
    start = tuple[0]
    end = tuple[1]
    additional = 0.0
    if _include_first_half_stoppage(start, end):
        additional += 1.5
    if _include_second_half_stoppage(start, end):
        additional += 4.0
    return end - start + additional #we're saying start is exclusive end are both inclusive








