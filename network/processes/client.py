from socket import socket
import rich
# from rich.prompt import Prompt
# from rich.table import Table
# from network.game import print_available_champs
from rich.table import Table


def _input(prompt: str) -> str:
    return input(prompt + ": ")


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
        champions = []

        request = _build_request(command="get-team")
        self._send_request(request)

        while data := self._get_response():
            if data[0] == "OK":
                self._team = data[1]
            break
        print("Team: ", self._team)

        request = _build_request(team=self._team, command="welcome")
        self._send_request(request)

        # TODO: Print welcome message here
        while data := self._get_response():
            if data[0] == "OK":
                rich.print(data[1])
                break
        print()
        print("---List Champs----------------------")
        # TODO: Print champ table
        request = _build_request(team=self._team, command="list-champs")
        print("Sending: ", request)
        self._send_request(request)
        if data := self._get_response():
            if not data:
                print("From server: \n", data)

        print()
        # TODO: Pick champions
        print("---Pick-Champs---------------------")
        while len(champions) < 2:
            champ = input("Pick champ: ")
            if champ not in champions:
                request = _build_request(team=self._team, command="pick-champ", arg=champ)
                self._send_request(request)
                if data := self._get_response():
                    if data[0] == "OK":
                        champions.append(champ)
                    else:
                        print(data[1])
            else:
                print("You've already picked this champ!")

        print("Your champions: ", champions)
        print()

        request = _build_request(team=self._team, command="ready")
        print("Sending: ", request)
        self._send_request(request)
        if data := self._get_response():
            if data[0] == "OK":
                print("From server: \n", data)

        # TODO: Server simulates a game
        print("---Simulate---------------------")

        print()
        # TODO: Print match summary here
        print("---Match-Summary---------------------")

    def _handle_response(self, resp: str):
        pass

    def _send_request(self, request: str):
        self._sock.send(request.encode())

    def _get_response(self):
        resp = self._sock.recv(self._buffer_size).decode()
        res_lst = resp.split(";")
        return res_lst[0], res_lst[1]


if __name__ == "__main__":
    Client()

