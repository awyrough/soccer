from events.models import StatisticEvent, TimeEvent
from games.models import Game

def get_team_games(team, start = None, end = None):
    """
    Return a sorted QuerySet of all the team's games in our DB.

    If a start and end date are given, restrict the search to just those dates
    """
    if start and end:
        games = Game.objects.filter(home_team = team, date__range=[start,end]) \
            | Game.objects.filter(away_team = team, date__range=[start,end])
    else:
        games = Game.objects.filter(home_team = team) \
            | Game.objects.filter(away_team = team)

    if not games:
        raise Exception("No games found for " + str(team))

    return games.order_by('date')







