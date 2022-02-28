from database import Champions
from selectors import EVENT_READ, DefaultSelector
from socket import socket, create_server
from threading import Thread

from src.local.game import print_available_champs


class Server:
    def __init__(self, host: str, port: int, buffer_size: int = 2048):
        self._sock = create_server((host, port))
        self._sock.setblocking(False)
        self._sel = DefaultSelector()
        self._sel.register(self._sock, EVENT_READ, True)
        self._buffer_size = buffer_size
        self._connections = []
        self._champs = Champions()
        self._match_history = None

    def run(self):
        print("Waiting for connections...")
        while True:
            events = self._sel.select()  # Sockets that are ready to be handled
            for key, _ in events:
                if key.data:
                    self._accept(key.fileobj)
                    self._connections.append(key.fileobj)
                    print(self._connections)
                else:
                    self._handle(key.fileobj)

    def _accept(self, sock: socket):
        conn, _ = sock.accept()
        print(f'[ACCEPTED] {conn}')
        conn.setblocking(False)
        self._sel.register(conn, EVENT_READ)

    def _handle(self, conn: socket):
        print("[RECEIVED] ", conn.getsockname())
        if data := conn.recv(self._buffer_size):
            user_inp = data.decode().split()
            try:
                com = user_inp[0]
                arg = user_inp[1]
                match com:
                    case "Get":
                        print("Get")
                    case "Change":
                        print("Change")
                    case "Get_all":
                        print("Get all")
                        all = self._champs.champs_stats
                        print_available_champs(all)
                #  champ = CHAMPS.get_champ_object(user_inp)
                print("[SENDING] ", conn.getsockname())
                conn.sendall(commands[com].encode())
            finally:
                conn.sendall("Server couldn't fetch your command".encode())

        else:
            print("[CLOSING] ", conn.getsockname())
            conn.close()
            self._sel.unregister(conn)


commands = {
    "Get": "get champ!",
    "Change": "change name!",
    "Get_all": "get all champs!"
}

if __name__ == "__main__":
    s = Server('localhost', 5555)
    s.run()
