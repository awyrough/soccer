from events.models import StatisticEvent, TimeEvent
from games.models import Game

def get_game_time_events(game):
    return TimeEvent.objects.filter(game=game).order_by("minute")

def _include_first_half_stoppage(start, end):
    """
    Return true if the start and end times span the first half
    stoppage time.
    """
    # If you start in the first half and end in the second half
    # or beyond
    if start <= 45 and (end > 45 or end == None):
        return True

def _include_second_half_stoppage(start, end):
    """
    Return true if the start and end times span the second
    half stoppage time.
    """
    # You would only include if there is no end
    return end > 90 or end == None

def get_game_time_events(game, start_minute=None, end_minute=None):
    """
    Return the time events in a game that begin with start minute
    and end with end minute, inclusive.
    """
    queryset = get_game_time_events(game) 
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
    # AJ Edit -- not sure why you included a pass, as I believe we need to return the queryset we're creating?
    #pass

    return queryset

def get_game_statistic_events(game):
    """
    Return all statistics from a given game.
    """
    return StatisticEvent.objects.filter(game=game)

def get_game_stats_by_action(game, action):
    """
    Return all statistics from a given game and action.
    """
    return get_game_statistic_events(game).filter(action=action)

def create_windows_for_game_action(game, action):
    """
    Return list of tuples as [start, end] of all the windows
    in a game.

    If there are no actions, it returns a full game window.
    If the last action is before the end of the game, the final
    window should be until the end of the game, including stoppage.
    """
    actions = get_game_stats_by_action(game, action) \
        .order_by("half", "seconds")
    if actions.count() == 0:
        return [[0, -2], ]
    windows = []
    start = 0
    last_action = None
    for action in actions:
        end = action.get_minute_ceiling()
        window = [start, end]
        windows.append(window)
        start = end
        last_action = action
    if last_action.get_minute_ceiling() != -2:
        windows.append([start, -2])
    return windows









