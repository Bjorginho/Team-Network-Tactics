from pymongo import MongoClient
from core import Champion
"""
These classes gets data (champions) and post data (match history) to mongoDB database, methods are called by the database server socket. 
"""

# Set up username, password and cluster_name
username = "admin"
password = "admin123"
cluster_name = "cluster0"

# Connect to MongoDB
CLUSTER = MongoClient(
    f"mongodb+srv://{username}:{password}@{cluster_name}.igyfh.mongodb.net/TNT?retryWrites=true&w=majority")
# Get database from cluster
DB = CLUSTER["TNT"]


class Champions:
    def __init__(self):
        self.__collection = DB["Champions"]
        self.champions = self.__load_champs()

    def __load_champs(self):
        champs = {}
        for c in self.__collection.find({}):
            name, rock, paper, scissors = c["name"], c["rock"], c["paper"], c["scissors"]
            champ = Champion(name, rock, paper, scissors)
            champs[champ.name] = champ
        print(f"Loaded {len(champs)} champions from database ")
        return champs

    def _add_champ(self, name: str, rock: int, paper: int, scissors: int):
        self.__collection.insert_one({"name": name, "rock": rock, "paper": paper, "scissors": scissors})
        print(f"Added {name} (rock: {rock}, paper: {paper}, scissors: {scissors}) to database")


class MatchHistory:
    def __init__(self):
        self.__collection = DB["Match_History"]

    def post_match(self, player1, player2, score):
        if score[0] > score[1]:
            winner = player1["name"]
        elif score[0] < score[1]:
            winner = player2["name"]
        else:
            winner = "Draw"
        self.__collection.insert_one({"red": player1, "blue": player2, "score": score, "winner": winner})
