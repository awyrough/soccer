from events.models import StatisticEvent
from games.models import Game

def get_game_stats(game):
    """
    Return all statistics from a given game.
    """
    return StatisticEvent.objects.filter(game=game)

def get_game_stats_by_action(game, action):
    """
    Return all statistics from a given game and action.
    """
    return get_game_stats(game).filter(action=action)

def _convert_minute_to_half_and_seconds(minute):
    seconds = minute * 60.0
    # first half
    if (seconds < StatisticEvent.SECOND_HALF_START_SECOND):
        return {"half": 1, "seconds": seconds}
    else:
        return {"half": 2, 
                "seconds": seconds - StatisticEvent.SECOND_HALF_START_SECOND}

def get_game_stats_by_minute(game, start, end):
    """
    Return all statistics from a given game between start and end
    BY MINUTE
    """
    start_seconds = start * 60.0
    end_seconds = end * 60.0

    stats = get_game_stats(game)
    # if we start in the first half, filter ever
    pass
    
def get_statistics_from_game_by_minute(game, start_minute, end_minute):
    pass
