from socket import create_server, SOL_SOCKET, SO_REUSEADDR
from database import Champions
import pickle


class DatabaseServer:

    def __init__(self, host: str, port: int, buffer_size: int = 1024):
        self._sock = create_server((host, port))
        self._sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self._buffer_size = buffer_size

        # Databases
        self._db_champs = Champions()
        self._db_match_history = None

    def run(self):
        print(f"Listening on {self._sock.getsockname()}")
        while True:
            conn, _ = self._sock.accept()
            request = conn.recv(1024).decode()
            print(f'Received from [{conn.getsockname()}]')
            data_lst = request.split(";")
            command = data_lst[0]
            match command:
                case "get-champs":
                    response = pickle.dumps(self._db_champs.champs_stats)
                    conn.send(response)
                case "post-match":
                    pass
                case _:
                    pass
            conn.close()


if __name__ == "__main__":
    db = DatabaseServer(host='localhost', port=5555)
    db.run()