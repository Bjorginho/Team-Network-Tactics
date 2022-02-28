from socket import socket
from src.local.game import print_available_champs

class Client:
    def __init__(self, buffer_size: int = 2048):
        self._sock = socket()
        self._sock.connect(('localhost', 5555))
        self._champions = []
        self._run()

    def _run(self):
        print("Commands:\n Get | Change | Get_all | fetch  ")
        champion = input("Pick a champ: ")
        while inp := input("Command >> ").lower():
            match inp:
                case "get":
                    msg = "Get " + champion
                    self._sock.sendall(msg.encode())
                    print(self._sock.recv(2048).decode())
                case "change":
                    msg = "Change "
                case "get_all":
                    mes = "Get_all " + "Hi"
                    self._sock.sendall(mes.encode())
                    print(self._sock.recv(2048).decode())
                case _:
                    print("Invalid command")


if __name__ == "__main__":
    Client()
