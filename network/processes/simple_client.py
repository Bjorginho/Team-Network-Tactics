from socket import socket
import rich
# from rich.prompt import Prompt
# from rich.table import Table
from game import print_available_champs


def _input(prompt: str) -> str:
    return input(prompt + ": ")


def _build_request(team: str = "", command: str = "", args: str = ""):
    return team + ";" + command + ";" + args


class Client:
    def __init__(self, buffer_size: int = 1024):
        self._sock = socket()
        self._sock.connect(('localhost', 5550))
        self._buffer_size = buffer_size
        self._run()

    def _run(self):
        champions = []
        request = _build_request(team="red", command="new-connection")
        self._send_request(request)

        # TODO: Print welcome message here
        if data := self._get_response():
            rich.print(data)
        print("\n")
        # TODO: Print champ table
        request = _build_request(team="red", command="print-champs")
        self._send_request(request)
        if data := self._get_response():
            champions = data
            print_available_champs(champions)

        # TODO: Pick champions

        # TODO: Server simulates a game

        # TODO: Print match summary here

    def _handle_response(self, resp: str):
        pass

    def _send_request(self, request: str):
        self._sock.send(request.encode())

    def _get_response(self) -> str:
        return self._sock.recv(self._buffer_size).decode()


if __name__ == "__main__":
    Client()
