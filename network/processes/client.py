from socket import socket
# from src.local.game import print_available_champs
from threading import Thread


class Client:
    def __init__(self, buffer_size: int = 2048):
        self._sock = socket()
        self._sock.connect(('localhost', 5555))
        self._buffer_size = buffer_size
        self._champions = []

        self._running_thread = Thread(target=self._run())
        self._running_thread.start()

    def _run(self):
        print("Commands:\n Get | Change | Get_all | fetch  ")
        champion = input("Pick a champ: ")
        while inp := input("Command >> ").lower():
            match inp:
                case "get":
                    msg = "Get " + champion
                    self._sock.sendall(msg.encode())
                    print(self._sock.recv(self._buffer_size).decode())
                case "change":
                    msg = "Change "
                case "get_all":
                    mes = "Get_all " + "Hi"
                    self._sock.sendall(mes.encode())
                    print(self._sock.recv(self._buffer_size).decode())
                case _:
                    print("Invalid command")
        self._running_thread.join()


if __name__ == "__main__":
    Client()
