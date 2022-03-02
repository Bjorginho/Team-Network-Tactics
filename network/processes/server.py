from database import Champions
from selectors import EVENT_READ, DefaultSelector
from socket import socket, create_server


class Server:
    def __init__(self, host: str, port: int, buffer_size: int = 1024):
        self._sock = create_server((host, port))
        self._sock.setblocking(False)
        self._sel = DefaultSelector()
        self._sel.register(self._sock, EVENT_READ, True)
        self._buffer_size = buffer_size
        self._champs = Champions()
        self._match_history = None
        self._taken_champs = []
        self._connections = {}

    def run(self):
        print("Waiting for connections...")
        while True:
            events = self._sel.select()  # Sockets that are ready to be handled
            for key, _ in events:
                if len(self._connections) <= 2:
                    if key.data:
                        self._accept(key.fileobj)
                    else:
                        self._handle(key.fileobj)

    def _accept(self, sock: socket):
        conn, address = sock.accept()
        print(f'Accepted: {address}')
        conn.setblocking(False)
        self._sel.register(conn, EVENT_READ)
        if len(self._connections) == 0:
            color = "red"
        else:
            color = "blue"
        self._connections[conn] = {"team": color, "champs": [], "ready": False}

    def _handle(self, conn: socket):
        if data := conn.recv(self._buffer_size):
            print("Request: ", data.decode())
            request = data.decode().split(";")
            try:
                team, command, arg = request[0], request[1], request[2]
                response = ""
                match command:
                    case "get-team":
                        msg = self._connections[conn]["team"]
                        response = "OK;" + msg

                    case "welcome":
                        msg = "Welcome to [bold yellow]Team Local Tactics[/bold yellow]!\nEach player choose a champion each time. "
                        response = "OK;" + msg

                    case "get-color":
                        pass
                    case "list-champs":
                        champs = self._champs.champs_stats
                        status = "OK"
                        response = status + ";" + champs.keys()
                        print("Sending: ", response)

                    case "pick-champ":
                        champ_lst = self._champs.champions
                        available = list(set(champ_lst) ^ set(self._taken_champs))
                        print("All: ", champ_lst)
                        print("Avalable: ", available)
                        if arg not in champ_lst:
                            status = "ERROR"
                            msg = "Available champs: [" + ', '.join(available) + "]"
                            response = status + ";" + msg
                        elif arg in available:
                            msg = arg
                            status = "OK"
                            response = status + ";" + msg
                            self._taken_champs.append(arg)
                            self._connections[conn]["champs"].append(arg)
                        else:
                            status = "ERROR"
                            msg = "Sorry, " + arg + " is taken enemy summoner!"
                            response = status + ";" + msg
                    case "ready":
                        self._connections[conn]["ready"] = True
                        print("Values, ", self._connections.values())
                        status = "OK"
                        msg = "You are now ready!"
                        response = status + ";" + msg
                    case _:
                        response = "ERROR;bad-request"
                print("Response: ", response)
                conn.sendall(response.encode())
                for c in self._connections:
                    print("Team: ", self._connections[c]["team"], " with: ", self._connections[c]["champs"])
            except Exception:
                conn.sendall(f"ERROR;Bad request [{data}]".encode())
        else:
            print(f"Closing: {conn.getsockname()}")
            conn.close()
            self._sel.unregister(conn)


if __name__ == "__main__":
    s = Server('localhost', 5550)
    s.run()
