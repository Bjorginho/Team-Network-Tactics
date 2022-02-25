from database import Champions
from selectors import EVENT_READ, DefaultSelector
from socket import socket, SO_REUSEADDR, SOL_SOCKET

# Selector object
sel = DefaultSelector()

# Setup server socket
sock = socket()
sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
sock.bind(("localhost", 5555))
sock.listen(2)  # Maximum two connections
sock.setblocking(False)
sel.register(sock, EVENT_READ, True)

# Databases
CHAMPS_DB = Champions()


def accept(new_socket: socket):
    """
    :param new_socket: incoming socket
    :return:
    """
    print("[ACCEPT] ", new_socket.getsockname())
    conn, address = new_socket.accept()  # Should be ready
    print(f'Accepted [{conn}] from [{address}]')
    conn.setblocking(False)  # This socket should not be blocking anything, pass Selector control of socket
    sel.register(conn, EVENT_READ)


def read(conn: socket):
    """
    Handle a connection
    :param conn: connection
    :return: Nothing
    """
    print("[READ] ", conn.getsockname())
    data = conn.recv(1024)  # Should be ready
    if data:
        sentence = data.decode()
        new_sentence = sentence.upper()
        # conn.send(new_sentence.encode())
        conn.send(f"Hello {conn.getsockname()}".encode())
        champ = CHAMPS_DB.get_champion(sentence)
        conn.send(f"You picked {champ}")
    else:
        print(f'Closing [{conn}]')
        sel.unregister(conn)


print("Waiting for connections...")
while True:
    events = sel.select()  # Sockets that are ready to be handled
    for key, _ in events:
        if key.data:
            accept(key.fileobj)
        else:
            read(key.fileobj)
