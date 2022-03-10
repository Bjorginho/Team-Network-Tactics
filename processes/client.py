import json
from socket import socket
import rich
from team_local_tactics import print_available_champs, print_match_summary
from core import Champion
import time
import pickle


class Client:
    def __init__(self, name: str, buffer_size: int = 1024):
        self._sock = socket()
        self._buffer_size = buffer_size
        self._name = name
        self._sock.connect(('localhost', 5550))

        self._team = None
        self._champs = []

        self._find_match()

    def _find_match(self):
        self._build_and_send(command="new-connection", arg=self._name)

        response, data = self._get_response()
        if response == "OK":
            self._team = data

        self._build_and_send(team=self._team, command="other-ready")

        wait_for_player = True
        while wait_for_player:
            try:
                while True:
                    response, msg = self._get_response()
                    if response == "OK":
                        print(msg)
                        wait_for_player = False
                        break
                    else:
                        time.sleep(1.5)
                        print(msg)
                        self._build_and_send(team=self._team, command="other-ready")
            finally:
                continue

        self._run()

    def _run(self):
        print("\n               GAME STARTED\n")
        print(f"You were assigned team {self._team}")

        self._build_and_send(team=self._team, command="welcome")

        #  Print welcome message
        _, data = self._get_response()
        rich.print(data)

        #  Print champ table
        self._build_and_send(team=self._team, command="list-champs")

        json_bytes = self._sock.recv(self._buffer_size)
        json_data = json.loads(json_bytes.decode())
        # Parse data
        for key in json_data:
            dict = json_data[key]
            name, rock, paper = dict["name"], dict["rock"], dict["paper"]
            scissors = round(1 - rock - paper, 2)
            json_data[key] = Champion(name, rock, paper, scissors)

        print_available_champs(json_data)

        print("\n")
        #  Pick champions
        while len(self._champs) < 2:
            champ = input("Pick champ: ")
            if champ not in self._champs:
                self._build_and_send(team=self._team, command="pick-champ", arg=champ)
                if data := self._get_response():
                    status = data[0]
                    msg = data[1]
                    if status == "OK":
                        # Ignore msg, just append champ
                        self._champs.append(champ)
                    else:
                        # Print error message
                        print(msg)
            else:
                print("You've already picked this champ!")

        print("Your champions: ", self._champs)

        self._build_and_send(team=self._team, command="ready")

        wait = True
        while wait:
            try:
                while data := self._get_response():
                    if data[0] == "OK":
                        wait = False
                        break
                    else:
                        time.sleep(3)
                        print(data[1])
                        self._build_and_send(team=self._team, command="ready")
            finally:
                continue

        self._build_and_send(team=self._team, command="get-match-summary")
        result = None
        while data := self._sock.recv(self._buffer_size):
            result = pickle.loads(data)
            break

        print_match_summary(result)

    def _build_and_send(self, team: str = "", command: str = "", arg: str = ""):
        request = team + ";" + command + ";" + arg
        self._sock.send(request.encode())

    def _get_response(self):
        response = self._sock.recv(self._buffer_size).decode()
        status, msg = response.split(";")
        return status, msg


if __name__ == "__main__":
    player_name = input("You are soon going to play Team Network Tactics!\nBut first, input your name here: ")
    Client(name=player_name)
