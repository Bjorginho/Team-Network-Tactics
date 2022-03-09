from pymongo import MongoClient
from core import Champion
import json

username = "admin"
password = "admin123"
cluster_name = "cluster0"


class Champions:
    def __init__(self):
        self.cluster = MongoClient(f"mongodb+srv://{username}:{password}@{cluster_name}.igyfh.mongodb.net/TNT?retryWrites=true&w=majority")
        self.db = self.cluster["TNT"]
        self.collection = self.db["Champions"]
        self.champs_stats = self.__load_champs()
        self.champions = list(self.champs_stats.keys())

    def get_champ_object(self, champ_name: str):
        return self.collection.find({"name": champ_name})[0]

    def __load_champs(self):
        champs = {}
        for c in self.collection.find({}):
            name, rock, paper, scissors = c["name"], c["rock"], c["paper"], c["scissors"]
            champ = Champion(name, rock, paper, scissors)
            champs[champ.name] = champ
            # self.champions[champ.name] = (rock, paper, scissors)
        return champs

    def del_and_overwrite(self):
        self.collection.delete_many({})
        with open("../champions.json") as f:
            data = json.load(f)
            self.collection.insert_many(data["champions"])

    def add_champ(self, name: str, rock: int, paper: int, scissors: int):
        self.collection.insert_one({"name": name, "rock": rock, "paper": paper, "scissors": scissors})




