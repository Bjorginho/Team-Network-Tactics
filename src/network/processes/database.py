from pymongo import MongoClient
from src.local.tlt.core import Champion
import json


def parse_champ(champ_cursor):
    name, rock, paper, scissors = champ_cursor["name"], champ_cursor["rock"], champ_cursor["paper"], champ_cursor["scissors"]
    return Champion(str(name), float(rock), float(paper), float(scissors))


class Champions:
    def __init__(self):
        self.user = "admin"
        self.__password = "admin123"
        self.__cluster_name = "cluster0"
        self.cluster = MongoClient(
            f"mongodb+srv://{self.user}:{self.__password}@{self.__cluster_name}.igyfh.mongodb.net/TNT?retryWrites=true&w=majority")
        self.db = self.cluster["TNT"]
        self.collection = self.db["Champions"]
        self.champions = {}

    def get_champ(self, champ_name: str):
        return self.collection.find({"name": champ_name})[0]

    def load_champs_from_db(self):
        return self.collection.find({})

    def load_champs(self):
        for c in self.collection.find():
            champ = parse_champ(c)
            self.champions[champ.name] = champ
        return self.champions

    def del_and_overwrite(self):
        self.collection.delete_many({})
        with open("../champions.json") as f:
            data = json.load(f)
            self.collection.insert_many(data["champions"])

    def add_champ(self, name: str, rock: int, paper: int, scissors: int):
        self.collection.insert_one({"name": name, "rock": rock, "paper": paper, "scissors": scissors})




