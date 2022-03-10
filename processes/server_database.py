from socket import socket, create_server, SOL_SOCKET, SO_REUSEADDR
from selectors import EVENT_READ, DefaultSelector
from database import Champions, MatchHistory
import pickle


class DatabaseServer:

    def __init__(self, host: str, port: int, buffer_size: int = 1024):
        self._sock = create_server((host, port))
        self._sock.setblocking(False)
        self._sel = DefaultSelector()
        self._sel.register(self._sock, EVENT_READ, True)
        self._sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self._buffer_size = buffer_size

        # Databases
        self._db_champs = Champions()
        self._db_match_history = MatchHistory()

    def run(self):
        print(f"Listening on {self._sock.getsockname()}")
        while True:
            events = self._sel.select()
            for key, _ in events:
                if key.data:
                    self._accept(key.fileobj)
                else:
                    self._handle(key.fileobj)

    def _accept(self, sock: socket):
        conn, address = sock.accept()
        print(f'Client [ACCEPTED]: {address}')
        conn.setblocking(True)
        self._sel.register(conn, EVENT_READ)

    def _handle(self, conn: socket):

        if data := conn.recv(self._buffer_size):
            print(f'[RECEIVED] Request from [{conn}]')

            data_lst = data.decode().split(";")
            command = data_lst[0]
            match command:
                case "get-champs":
                    print("[SENDING] Sending champs to game server")
                    response = pickle.dumps(self._db_champs.champions)
                    conn.send(response)
                case "post-match":
                    request = conn.recv(self._buffer_size)
                    match = pickle.loads(request)
                    print("[SENDING] Match to database socket")
                    print(match)
                    self._db_match_history.post_match(
                        player1=match["red"],
                        player2=match["blue"],
                        score=match["score"]
                    )
        else:
            print(f"Client [CLOSING]: {conn.getsockname()}")
            conn.close()
            self._sel.unregister(conn)



if __name__ == "__main__":
    db = DatabaseServer(host='localhost', port=5555)
    db.run()
