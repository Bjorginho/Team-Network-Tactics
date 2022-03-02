from socket import socket
import rich
from rich.prompt import Prompt
from rich.table import Table
from rich.table import Table
from team_network_tactics.game import print_available_champs
import time
import os


def _build_request(team: str = "", command: str = "", arg: str = ""):
    return team + ";" + command + ";" + arg


class Client:
    def __init__(self, buffer_size: int = 1024):
        self._sock = socket()
        self._sock.connect(('localhost', 5550))
        self._buffer_size = buffer_size

        self._team = None
        self._champs = []

        self._run()

    def _run(self):

        request = _build_request(command="new-connection")
        self._send_request(request)
        print("Waiting for server to start game...")

        wait_for_player = True
        while wait_for_player:
            try:
                while data := self._get_response():
                    if data[0] == "OK":
                        print("Enemy connected")
                        wait_for_player = False
                        break
                    else:
                        time.sleep(3)
                        print(data[1])
                        self._send_request(request)
            finally:
                continue

        request = _build_request(command="get-team")
        self._send_request(request)

        while data := self._get_response():
            if data[0] == "OK":
                self._team = data[1]
            break

        print("-------------GAME STARTED-------------")
        print(f"You were assigned Team: [ {self._team} ]")

        request = _build_request(team=self._team, command="welcome")
        self._send_request(request)

        #  Print welcome message
        while data := self._get_response():
            if data[0] == "OK":
                rich.print(data[1])
                break

        #  Print champ table
        request = _build_request(team=self._team, command="list-champs")
        self._send_request(request)

        if data := self._sock.recv(self._buffer_size).decode():
            data = data.replace("{", "")
            data = data.replace("}", "")
            data = data.split(", ")
            for row in data:
                name, stats = row.split(":")
                name = name.replace("'", "")
                print(stats)
            # print_available_champs(ast.literal_eval(data))

        print("\n")
        #  Pick champions
        while len(self._champs) < 2:
            champ = input("Pick champ: ")
            if champ not in self._champs:
                request = _build_request(team=self._team, command="pick-champ", arg=champ)
                self._send_request(request)
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

        request = _build_request(team=self._team, command="ready")
        print("Sending: ", request)
        self._send_request(request)
        if data := self._get_response():
            if data[0] == "OK":
                print("From server: \n", data)

        # TODO: Server simulates a game
        print("---Simulate---------------------")

        # TODO: Print match summary here
        print("---Match-Summary---------------------")

    def _send_request(self, request: str):
        self._sock.send(request.encode())

    def _get_response(self):
        resp = self._sock.recv(self._buffer_size).decode()
        res_lst = resp.split(";")
        return res_lst[0], res_lst[1]


if __name__ == "__main__":
    Client()
