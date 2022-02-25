from pymongo import MongoClient
import json


class ChampionsDB:
    def __init__(self, database: str, collection: str):
        self.user = "admin"
        self.__password = "admin123"
        self.__cluster_name = "cluster0"
        self.cluster = MongoClient(
            f"mongodb+srv://{self.user}:{self.__password}@{self.__cluster_name}.igyfh.mongodb.net/TNT?retryWrites=true&w=majority")
        self.db = self.cluster[database]
        self.collection = self.db[collection]

    def get_champion(self, name: str):
        return self.collection.find({"name": name})[0]

    def get_all_champs(self):
        return self.collection.find({})

    def del_and_overwrite(self):
        self.collection.delete_many({})
        with open("../champions.json") as f:
            data = json.load(f)
            self.collection.insert_many(data["champions"])

    def add_champ(self, name:str, rock:int, paper:int, scissors:int):
        self.collection.insert_one({"name": name, "rock": rock, "paper": paper, "scissors": scissors})

    """def delete_champ(self, name:str):
        self.collection.delete_one({"name": name})"""


class MatchHistory:

    def __init__(self):
        pass

    def get_history(self, player_name):
        return "Not yet implemented"