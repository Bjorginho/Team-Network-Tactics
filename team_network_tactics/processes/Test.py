from team_network_tactics.core import Team, Match
from team_network_tactics.team_local_tactics import print_match_summary
from database import Champions
import rich

db = Champions()

player1, player2 = ["Asir", "Vain"], ["Cactus", "Luanne"]

match = Match(
    Team([db.champs_stats[name] for name in player1]),
    Team([db.champs_stats[name] for name in player2])
)

match.play()

rich.print(match)
print_match_summary(match)
