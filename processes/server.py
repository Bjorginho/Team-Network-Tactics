from socket import socket, create_server, create_connection
from selectors import EVENT_READ, DefaultSelector
from core import Match, Team
from rich import print
import json
import pickle


class Server:
    def __init__(self, host: str, port: int, buffer_size: int = 1024):
        self._sock = create_server((host, port))
        self._sock.setblocking(False)
        self._sel = DefaultSelector()
        self._sel.register(self._sock, EVENT_READ, True)
        self._buffer_size = buffer_size
        self._connections = {}

        # Connect to database
        self._db_socket = create_connection(('localhost', 5555))
        self._champions = self.__get_champs()
        self._dict_champ_stats = self.__load_champ_stats()

        self._taken_champs = []
        self._match = None

    def __get_champs(self):
        # Request champions dictionary from Database Server
        request = "get-champs;"
        print("DB [SENDING] Requesting champions from database socket")
        self._db_socket.sendall(request.encode())
        data = self._db_socket.recv(self._buffer_size)
        champs = pickle.loads(data)
        if champs is not None:
            print("DB [RECEIVED] Received champions from database socket")
        return champs

    def __post_match(self, match):
        request = "post-match;"
        self._db_socket.sendall(request.encode())
        print("DB [SENDING] Sending match to database socket")
        match_encoded = pickle.dumps(match)
        self._db_socket.sendall(match_encoded)

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
        print(f'Client [ACCEPTED]: {address}')
        conn.setblocking(False)
        self._sel.register(conn, EVENT_READ)
        self.__register_and_assign_team(conn)

    def __register_and_assign_team(self, conn: socket):
        if len(self._connections) % 2 == 0:
            color = "red"
        else:
            color = "blue"
        self._connections[conn] = {"team": color, "champs": [], "ready": False}

    def _handle(self, conn: socket):
        if data := conn.recv(self._buffer_size):
            print("Client [REQUEST] ", data.decode())
            request = data.decode().split(";")
            team, command, arg = request[0], request[1], request[2]

            match command:
                case "new-connection":
                    self._connections[conn]["name"] = arg
                    response = "OK;" + self._connections[conn]["team"]
                case "other-ready":
                    if len(self._connections) == 2:
                        response = "OK;Two players connected"
                    else:
                        response = "ERROR;Waiting for opponent."
                case "get-team":
                    response = "OK;" + self._connections[conn]["team"]
                case "welcome":
                    response = "OK;" + "\nWelcome to [bold yellow]Team Local Tactics[/bold yellow]!\nEach player choose a champion each time.\n"
                case "list-champs":
                    response = json.dumps(self._dict_champ_stats)
                case "get-turn":
                    if len(self._taken_champs) % 2 == 0:
                        response = "OK;red"
                    else:
                        response = "OK;blue"
                case "pick-champ":
                    champ_lst = (self._champions.keys())
                    available = list(set(champ_lst) ^ set(self._taken_champs))
                    if arg not in champ_lst:
                        response = "ERROR;Available champs: [" + ', '.join(available) + "]"
                    elif arg in available:
                        response = "OK;" + arg
                        self._taken_champs.append(arg)
                        self._connections[conn]["champs"].append(arg)
                    else:
                        response = "ERROR;Sorry, " + arg + " is taken enemy summoner!"
                case "ready":
                    self._connections[conn]["ready"] = True
                    count = 0
                    for connection in self._connections:
                        if self._connections[connection]["ready"]:
                            count += 1
                    if count == 2:
                        response = "OK;Both ready"
                        if self._match is None:
                            self._match = self._simulate_match()
                    else:
                        response = "ERROR;Waiting for other client."
                case "get-match-summary":
                    response = pickle.dumps(self._match)
                case _:
                    response = "ERROR;bad-request"
            # Respond client
            if command == "get-match-summary":
                conn.sendall(response)
            else:
                conn.sendall(response.encode())
        else:
            print(f"Client [CLOSING]: {conn.getsockname()}")
            conn.close()
            self._sel.unregister(conn)

    def _simulate_match(self):

        p1_name, p2_name = "", ""
        player1, player2 = [], []
        for conn in self._connections:
            if self._connections[conn]["team"] == "red":
                player1 = self._connections[conn]["champs"]
                p1_name = self._connections[conn]["name"]
            elif self._connections[conn]["team"] == "blue":
                player2 = self._connections[conn]["champs"]
                p2_name = self._connections[conn]["name"]

        match = Match(
            Team([self._champions[name] for name in player1]),
            Team([self._champions[name] for name in player2])
        )
        match.play()

        match_obj = {
            "red":
                {"name": p1_name, "champs": player1},
            "blue": {"name": p2_name, "champs": player2},
            "score": match.score
        }
        self.__post_match(match_obj)

        # Reset data
        self._taken_champs = []
        for conn in self._connections:
            self._connections[conn]["champs"] = []
        return match

    def __load_champ_stats(self):
        d = {}

        for champ in self._champions:
            # display objects content using __dict__
            dict = self._champions[champ].__dict__
            name = dict["_name"]
            rock = dict["_rock"]
            paper = dict["_paper"]
            scissors = round(1 - rock - paper, 2)

            d[champ] = {"name": name, "rock": rock, "paper": paper, "scissors": scissors}
        return d


if __name__ == "__main__":
    s = Server('localhost', 5550)
    s.run()
