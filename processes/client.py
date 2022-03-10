from socket import create_connection
from team_local_tactics import print_available_champs, print_match_summary
from core import Champion
import time
import pickle
import rich
import json


class Client:
    def __init__(self, name: str, buffer_size: int = 1024):
        self._sock = create_connection(('localhost', 5550))
        self._buffer_size = buffer_size
        self._name = name

        self._team = None
        self._champs = []

        self._find_match()

    def _find_match(self):
        """
        This method sends request to server to join a lobby.
        Wait until enemy opponent connected.

        """
        print(f"Welcome {self._name}\nPlease wait for game to start.")
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
            name, rock, paper, scissors = dict["name"], dict["rock"], dict["paper"], dict["scissors"]
            json_data[key] = Champion(name, rock, paper, scissors)

        print_available_champs(json_data)

        print("\n")

        #  Pick champions
        print("Champion select, pick champ or wait for other player. ")
        while len(self._champs) < 2:
            self._build_and_send(team=self._team, command="get-turn")
            _, turn = self._get_response()
            if turn == self._team:
                while champ := input("Pick champ: "):
                    if champ not in self._champs:
                        self._build_and_send(team=self._team, command="pick-champ", arg=champ)
                        if data := self._get_response():
                            status = data[0]
                            msg = data[1]
                            if status == "OK":
                                # Ignore msg, just append champ
                                self._champs.append(champ)
                                print(f"You picked {champ}\nWaiting for enemy to pick champ.")
                                break
                            else:
                                # Print error message
                                print(msg)
                    else:
                        print("You've already picked this champ!")

        print("You picked ", " and ".join(self._champs))

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

        match_bytes = self._sock.recv(self._buffer_size)
        match = pickle.loads(match_bytes)

        print_match_summary(match)

        red, blue = match.score

        if red < blue:
            winner = "blue"
        elif red > blue:
            winner = "red"
        else:
            winner = "draw"

        match winner:
            case self._team:
                print("Congratulations you won!")
            case "draw":
                print("It was a draw")
            case _:
                print("Sorry you lost, better luck next time!")

        print("Thank you for playing!\n"
              "This is only a demo (MVP) of Team-Network-Tactics so more functions will come sooner or later!")

    def _build_and_send(self, team: str = "", command: str = "", arg: str = ""):
        request = team + ";" + command + ";" + arg
        self._sock.send(request.encode())

    def _get_response(self):
        response = self._sock.recv(self._buffer_size).decode()
        status, msg = response.split(";")
        return status, msg


if __name__ == "__main__":
    player_name = input("You are soon going to play Team Network Tactics!\nBut first, input your name here:\n")
    Client(name=player_name)
