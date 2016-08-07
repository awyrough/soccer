from events.models import StatisticEvent, TimeEvent
from games.models import Game

from django.db.models import Q

def _include_first_half_stoppage(start, end):
    """
    Return true if the window spans the first half stoppage time.
    """
    # If you start in the first half and end in the second half
    # or beyond
    if (0 <= start <= 45) and (end > 45 or end == -2 or end == None):
        return True
    if (end == -1):
        return True
    if (start == -1):
        return False

def _include_second_half_stoppage(start, end):
    """
    Return true if the window spans the second half stoppage time.
    """
    # You would only include if there is no end
    return end > 90 or end == None or end == -2

def get_game_time_events(game):
    return TimeEvent.objects.filter(game=game).order_by("minute")

def get_game_time_events_window(game, start_minute=None, end_minute=None):
    """
    Return the time events in a game that begin with start minute
    and end with end minute, inclusive.

    AJ 7/30: We couldn't do the simple gt and lte logic because of cases where we'd 
    either kick out stoppage times or have a start/end be a stoppage time
    """
    queryset = get_game_time_events(game) 

    #Handle cases where start min could be a stoppage time; always include stoppage timeEvents
    if start_minute == -2:
        raise Exception("The start of a time window shouldn't be second half stoppage")
    elif start_minute == -1:
        approx_start = 45.1
        queryset = queryset.filter(Q(minute__gt=approx_start) | Q(minute__lt=0))
    elif start_minute >= 0:
        queryset = queryset.filter(Q(minute__gt=start_minute) | Q(minute__lt=0))

    #Handle cases where end min could be a stoppage time; always include stoppage timeEvents
    if end_minute == -1:
        approx_end = 45.1
        queryset = queryset.filter(Q(minute__lte=approx_end) | Q(minute__lt=0))
    elif end_minute == -2:
        approx_end = 90.1
        queryset = queryset.filter(Q(minute__lte=approx_end)) 
    elif end_minute >= 0:
        queryset = queryset.filter(Q(minute__lte=end_minute) | Q(minute__lt=0))
    
    # NOW decide whether or not to kick out stoppage events
    if (not _include_first_half_stoppage(start_minute, end_minute)):
        queryset = queryset.exclude(
            minute=TimeEvent.FIRST_HALF_EXTRA_TIME)
    if (not _include_second_half_stoppage(start_minute, end_minute)):
        queryset = queryset.exclude(
            minute=TimeEvent.SECOND_HALF_EXTRA_TIME)

    return queryset

def get_game_time_events_for_team(
    game, team, start_minute=None, end_minute=None):
    """
    Return the minute events by team.
    """
    return get_game_time_events_window(
        game, start_minute=start_minute, end_minute=end_minute) \
            .filter(team=team)

def get_game_statistic_events(game):
    """
    Return all statistics from a given game.
    """
    return StatisticEvent.objects.filter(game=game)

def get_game_statistic_events_by_action_and_team(team, game, action, identifier):
    """
    Return all statistics from a given game and action. Changes depending on Both, Self, Oppo relative to team
    """
    if identifier == "Self":
        return get_game_statistic_events(game).filter(action=action, action_team=team)
    elif identifier == "Oppo":
        return get_game_statistic_events(game).filter(action=action).exclude(action_team = team)
    else:
        return get_game_statistic_events(game).filter(action=action)
        
def create_windows_for_game(team, game, action, identifier):
    """
    Return list of tuples as [start, end] of all the windows
    in a game.

    If there are no actions, it returns a full game window.
    If the last action is before the end of the game, the final
    window should be until the end of the game, including stoppage.
    """
    actions = get_game_statistic_events_by_action_and_team(team, game, action, identifier) \
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
        if end == -2:
            break
    if last_action.get_minute_ceiling() != -2:
        windows.append([start, StatisticEvent.SECOND_HALF_EXTRA_TIME])
    return windows

def create_window_meta_information_for_game(team, game, action, identifier):
    """
    Return list of meta information describing the start of each window
    in a game.

    If there are no actions, it returns a full window that says "No Moments"
    If the last action is before the end of the game, the final
    window should be until the end of the game, including stoppage.
    """
    actions = get_game_statistic_events_by_action_and_team(team, game, action, identifier) \
        .order_by("half", "seconds")
    if actions.count() == 0:
        return ["No Moments Found"]
    meta_info = []
    meta_info.append("Game Start")
    last_action = None
    for action in actions:
        meta_info.append(str(action.action_team) + " > " + str(action.action))
        last_action = action
        if action.get_minute_ceiling() == -2:
            break
    if (last_action.get_minute_ceiling() == -2) and (len(actions) == 1):
        meta_info = ["Game Start; End with stoppage time " + str(last_action.action_team) \
            + " > " + str(last_action.action)]
    return meta_info

def create_window_tally_action_counts_for_game(team, game, action, identifier):
    """
    Return list of aggregate counts (i.e. relative game states) describing the start of each window
    in a game.

    If there are no actions, it returns a list with one "0" value
    """
    actions = get_game_statistic_events_by_action_and_team(team, game, action, identifier) \
        .order_by("half", "seconds")
    action_count = 0
    if actions.count() == 0:
        return [action_count]
    action_count_history = []
    action_count_history.append(action_count)
    for action in actions:
        if action.action_team == team:
            action_count += 1
        else:
            action_count += -1
        action_count_history.append(action_count)
    return action_count_history

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
    if start == -1:
        start = 45
    if end == -1:
        end = 45
    elif end == -2:
        end = 90

    return end - start + additional #we're saying start is exclusive end are both inclusive








