from pymongo import MongoClient
from core import Champion, Match
import json

username = "admin"
password = "admin123"
cluster_name = "cluster0"

CLUSTER = MongoClient(f"mongodb+srv://{username}:{password}@{cluster_name}.igyfh.mongodb.net/TNT?retryWrites=true&w=majority")
DB = CLUSTER["TNT"]


class Champions:
    def __init__(self):
        self.collection = DB["Champions"]
        self.champions = self.__load_champs()

    def __load_champs(self):
        champs = {}
        for c in self.collection.find({}):
            name, rock, paper, scissors = c["name"], c["rock"], c["paper"], c["scissors"]
            champ = Champion(name, rock, paper, scissors)
            champs[champ.name] = champ
        return champs

    def del_and_overwrite(self):
        self.collection.delete_many({})
        with open("../champions.json") as f:
            data = json.load(f)
            self.collection.insert_many(data["champions"])

    def add_champ(self, name: str, rock: int, paper: int, scissors: int):
        self.collection.insert_one({"name": name, "rock": rock, "paper": paper, "scissors": scissors})


class MatchHistory:
    def __init__(self):
        self.collection = DB["Match_History"]

    def post_match(self, player1, player2, score):

        if score[0] > score[1]:
            winner = player1["name"]
        elif score[0] < score[1]:
            winner = player2["name"]
        else:
            winner = "Draw"
        self.collection.insert_one({"red": player1, "blue": player2, "score": score, "winner": winner})
