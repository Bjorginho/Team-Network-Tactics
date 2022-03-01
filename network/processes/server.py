from database import Champions
from selectors import EVENT_READ, DefaultSelector
from socket import socket, create_server
from threading import Thread


class Server:
    def __init__(self, host: str, port: int, buffer_size: int = 1024):
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
            if len(self._connections) == 2:
                print("We have two connections, ", self._connections)
                game_thread = Thread(target=self._start_game(self._sock, self._connections))
                game_thread.start()
                self._connections = []

            events = self._sel.select()  # Sockets that are ready to be handled
            for key, _ in events:
                if key.data:
                    self._accept(key.fileobj)
                else:
                    self._handle(key.fileobj)

    def _accept(self, sock: socket):
        conn, address = sock.accept()
        print(f'Accepted: {address}')
        conn.setblocking(False)
        self._sel.register(conn, EVENT_READ)
        self._connections.append(sock)

    def _handle(self, conn: socket):
        if data := conn.recv(self._buffer_size):
            print("Request from client: ", data.decode())
            request = data.decode().split(";")
            try:
                team, command, args = request[0], request[1], request[2]

                response = ""
                match command:
                    case "new-connection":
                        response = "Welcome to [bold yellow]Team Local Tactics[/bold yellow]!\nEach player choose a champion each time. "
                    case "print-champs":
                        response = self._champs.champs_stats
                    case _:
                        response = "bad-request"
                conn.sendall(response.encode())
            except Exception:
                conn.sendall(f"Bad request [{data}]".encode())
        else:
            print(f"Closing: {conn.getsockname()}")
            conn.close()
            self._sel.unregister(conn)

    def _start_game(self, _sock, connections: list[socket]):
        p1 = connections[0]
        p2 = connections[1]
        print(f"Game started \n {p1.getsockname()} vs {p2.getsockname()}")


if __name__ == "__main__":
    s = Server('localhost', 5550)
    s.run()
